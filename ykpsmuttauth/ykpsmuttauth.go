/*
 * Copyright (c) 2024 Runxi Yu <https://runxiyu.org>
 * SPDX-License-Identifier: BSD-2-Clause
 *
 * Key inspiration was taken from mutt_oauth2.py written by Alexander Perlis,
 * licensed under the GNU General Public License, version 2 or later, as
 * published by the Free Software Foundation. I don't think that this program
 * is a derivative work of mutt_oauth2.py in terms of GPL interpretation, but I
 * might be wrong.  Consult your lawyer if you want to use this program in a
 * context incompatible with the GPL.
 * https://raw.githubusercontent.com/muttmua/mutt/master/contrib/mutt_oauth2.py
 */

package main

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"net/url"
	"os"
	"time"
)

type Registration struct {
	AuthorizeEndpoint  string
	DevicecodeEndpoint string
	TokenEndpoint      string
	Tenant             string
	Scope              string
	ClientID           string
}

type Token struct {
	AccessToken           string `json:"access_token"`
	AccessTokenExpiration string `json:"access_token_expiration"`
	RefreshToken          string `json:"refresh_token"`
	Email                 string `json:"email"`
}

var ykps = Registration{
	AuthorizeEndpoint:  "https://login.microsoftonline.com/ddd3d26c-b197-4d00-a32d-1ffd84c0c295/oauth2/v2.0/authorize",
	DevicecodeEndpoint: "https://login.microsoftonline.com/ddd3d26c-b197-4d00-a32d-1ffd84c0c295/oauth2/v2.0/devicecode",
	TokenEndpoint:      "https://login.microsoftonline.com/ddd3d26c-b197-4d00-a32d-1ffd84c0c295/oauth2/v2.0/token",
	Tenant:             "ddd3d26c-b197-4d00-a32d-1ffd84c0c295",
	Scope:              "offline_access https://outlook.office.com/IMAP.AccessAsUser.All https://outlook.office.com/SMTP.Send",
	ClientID:           "fea760d5-b496-4f63-be1e-93855c1c5f78",
}

var token Token
var tokenFile string
var authorize_email string

func init() {
	flag.StringVar(&tokenFile, "tokenfile", "", "(required) persistent token storage")
	flag.StringVar(&authorize_email, "authorize", "", "email to newly authorize")
	flag.Parse()
}

func readTokenFile() error {
	data, err := os.ReadFile(tokenFile)
	if err != nil {
		return err
	}
	return json.Unmarshal(data, &token)
}

func writeTokenFile() error {
	data, err := json.Marshal(&token)
	if err != nil {
		return err
	}
	return os.WriteFile(tokenFile, data, 0600)
}

func accessTokenValid() bool {
	if token.AccessTokenExpiration == "" {
		return false
	}
	expirationTime, err := time.Parse(time.RFC3339, token.AccessTokenExpiration)
	if err != nil {
		return false
	}
	return time.Now().Before(expirationTime)
}

func updateTokens(r map[string]interface{}) error {
	token.AccessToken = r["access_token"].(string)
	expiresIn := int(r["expires_in"].(float64))
	token.AccessTokenExpiration = time.Now().Add(time.Duration(expiresIn) * time.Second).Format(time.RFC3339)
	if refreshToken, ok := r["refresh_token"]; ok {
		token.RefreshToken = refreshToken.(string)
	}
	return writeTokenFile()
}

func generateCodeVerifier() (string, string, error) {
	verifier := make([]byte, 90)
	_, err := rand.Read(verifier)
	if err != nil {
		return "", "", err
	}
	codeVerifier := base64.RawURLEncoding.EncodeToString(verifier)
	hash := sha256.Sum256([]byte(codeVerifier))
	codeChallenge := base64.RawURLEncoding.EncodeToString(hash[:])
	return codeVerifier, codeChallenge, nil
}

func startHTTPServer() (chan string, int, error) {
	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		return nil, 0, err
	}

	codeChan := make(chan string)
	server := &http.Server{}
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		code := r.URL.Query().Get("code")
		if code != "" {
			codeChan <- code
		}
		w.Header().Set("Content-Type", "text/plain")
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "Done, please check your terminal")
	})

	go func() {
		if err := server.Serve(listener); err != http.ErrServerClosed {
			log.Fatalf("HTTP server error: %v", err)
		}
	}()

	return codeChan, listener.Addr().(*net.TCPAddr).Port, nil
}

func authorize_request() error {
	p := url.Values{
		"client_id": {ykps.ClientID},
		"tenant":    {ykps.Tenant},
		"scope":     {ykps.Scope},
	}
	codeVerifier, codeChallenge, err := generateCodeVerifier()
	if err != nil {
		return err
	}
	codeChan, port, err := startHTTPServer()
	if err != nil {
		return err
	}
	redirectURI := fmt.Sprintf("http://localhost:%d/", port)
	p.Set("redirect_uri", redirectURI)
	p.Set("response_type", "code")
	p.Set("code_challenge", codeChallenge)
	p.Set("code_challenge_method", "S256")
	p.Set("login_hint", token.Email)
	authorizeURL := ykps.AuthorizeEndpoint + "?" + p.Encode()
	fmt.Fprintf(os.Stderr, "Please visit:\n%s\n", authorizeURL)

	authCode := <-codeChan

	data := url.Values{
		"client_id":     {ykps.ClientID},
		"tenant":        {ykps.Tenant},
		"code":          {authCode},
		"redirect_uri":  {redirectURI},
		"grant_type":    {"authorization_code"},
		"code_verifier": {codeVerifier},
	}

	resp, err := http.PostForm(ykps.TokenEndpoint, data)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return errors.New(resp.Status)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}

	var response map[string]interface{}
	if err := json.Unmarshal(body, &response); err != nil {
		return err
	}

	if _, ok := response["error"]; ok {
		return fmt.Errorf("authorization error: %v", response["error"])
	}

	return updateTokens(response)
}

func refreshToken() error {
	if token.RefreshToken == "" {
		return errors.New("no refresh token available")
	}

	data := url.Values{
		"client_id":     {ykps.ClientID},
		"tenant":        {ykps.Tenant},
		"refresh_token": {token.RefreshToken},
		"grant_type":    {"refresh_token"},
	}

	resp, err := http.PostForm(ykps.TokenEndpoint, data)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return errors.New(resp.Status)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}

	var response map[string]interface{}
	if err := json.Unmarshal(body, &response); err != nil {
		return err
	}

	if _, ok := response["error"]; ok {
		return fmt.Errorf("refresh token error: %v", response["error"])
	}

	return updateTokens(response)
}

func main() {
	if tokenFile == "" {
		log.Fatal("You must provide a token file path.")
	}

	if err := readTokenFile(); err != nil {
		if !os.IsNotExist(err) {
			log.Fatalf("Error reading token file: %v", err)
		}
		if authorize_email == "" {
			log.Fatalf("You must run the script with --authorize at least once.")
		}
		token.Email = authorize_email
		token.AccessToken = ""
		token.AccessTokenExpiration = ""
		token.RefreshToken = ""
		if err := writeTokenFile(); err != nil {
			log.Fatalf("Error writing token file: %v", err)
		}
	}

	if authorize_email != "" {
		if err := authorize_request(); err != nil {
			log.Fatalf("Authorization error: %v", err)
		}
	} else if !accessTokenValid() {
		if err := refreshToken(); err != nil {
			log.Fatalf("Refresh token error: %v", err)
		}
	}

	if !accessTokenValid() {
		log.Fatal("No valid access token. This should not be able to happen.")
	}

	fmt.Println(token.AccessToken)
}

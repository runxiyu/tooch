/*
 * Change your YK Pao School outlook profile photo.
 *
 * Copyright (c) 2024 Runxi Yu <https://runxiyu.org>
 * SPDX-License-Identifier: BSD-2-Clause
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 *
 *     1. Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *     2. Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS "AS IS" AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

package main

import (
	"bytes"
	"context"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"

	"github.com/AzureAD/microsoft-authentication-library-for-go/apps/public"
)

func acquireTokenInteractive(app public.Client, username string) (string, error) {
	result, err := app.AcquireTokenInteractive(context.TODO(), []string{"User.ReadWrite"}, public.WithLoginHint(username))
	if err != nil {
		return "", fmt.Errorf("interactive authentication error: %w", err)
	}
	return result.AccessToken, nil
}

func acquireTokenPassword(app public.Client, username, password string) (string, error) {
	result, err := app.AcquireTokenByUsernamePassword(context.TODO(), []string{"User.ReadWrite"}, username, password)
	if err != nil {
		return "", fmt.Errorf("password authentication error: %w", err)
	}
	return result.AccessToken, nil
}

func updateProfilePhoto(token, userID, photoPath string) error {
	graphEndpoint := "https://graph.microsoft.com/v1.0"
	url := fmt.Sprintf("%s/users/%s/photo/$value", graphEndpoint, userID)

	photoData, err := os.ReadFile(photoPath)
	if err != nil {
		return fmt.Errorf("failed reading photo: %w", err)
	}

	var mimetype string
	if strings.HasSuffix(photoPath, ".jpg") || strings.HasSuffix(photoPath, ".jpeg") {
		mimetype = "image/jpeg"
	} else if strings.HasSuffix(photoPath, ".png") {
		mimetype = "image/png"
	}

	req, err := http.NewRequest("PUT", url, bytes.NewReader(photoData))
	if err != nil {
		return fmt.Errorf("failed making request: %w", err)
	}
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", mimetype)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("failed requesting: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed reading response: %w", err)
	}

	fmt.Println(resp.StatusCode)
	fmt.Printf("%s\n", body)

	return nil
}

func main() {
	var email, photo, passVar string

	flag.StringVar(&email, "email", "", "(required) username@ykpaoschool.cn")
	flag.StringVar(&photo, "photo", "", "(required) path to avatar")
	flag.StringVar(&passVar, "passvar", "", "environment variable containing the password")
	flag.Parse()

	if photo == "" || email == "" {
		flag.Usage()
		return
	}

	app, err := public.New("14f8346d-98c9-4f12-875f-3b2cabe7110a", public.WithAuthority("https://login.microsoftonline.com/organizations"))
	if err != nil {
		log.Fatalf("failed creating msal app: %v", err)
	}

	var token string
	if passVar == "" {
		token, err = acquireTokenInteractive(app, email)
	} else {
		password := os.Getenv(passVar)
		if password == "" {
			log.Fatalf("environment variable %s not found", passVar)
		}
		token, err = acquireTokenPassword(app, email, password)
	}
	if err != nil {
		log.Fatalf("failed to acquire token: %v", err)
	}

	err = updateProfilePhoto(token, email, photo)
	if err != nil {
		log.Fatalf("failed to update profile photo: %v", err)
	}
}

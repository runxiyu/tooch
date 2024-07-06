/*
 * Copyright (c) 2024 Runxi Yu <https://runxiyu.org>
 * SPDX-License-Identifier: BSD-2-Clause
 *
 * This script allows you to change your Microsoft Outlook photo
 * for YK Pao School. Note that they reset it at seemingly random
 * times every day, so you probably want to run this every hour
 * or something.
 *
 * I used to do "while true; do sleep 3600; ./chphoto.sh; done"
 * but that's obviously stupid, so here's a crontab:
 *
 *    0 * * * * $HOME/cronstuff/chphoto.sh
 *
 * and chphoto.sh is just:
 *
 *    cd $HOME/cronstuff/
 *    pass=XXXXXXXXXXXXXXX ./tooch/chphoto/chphoto -passvar pass -email sXXXXX@ykpaoschool.cn -photo ./tooch/sjdb-avatar.png > marker
 *    date >> marker
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
	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: %s [options] path_to_photo\n", os.Args[0])
		flag.PrintDefaults()
	}
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

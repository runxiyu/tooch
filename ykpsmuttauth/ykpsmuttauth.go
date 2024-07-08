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
	"encoding/json"
	"flag"
	"os"
	"fmt"
	"strings"
	// "log"
	// "io"
)

const authorize_endpoint string = "https://login.microsoftonline.com/ddd3d26c-b197-4d00-a32d-1ffd84c0c295/oauth2/v2.0/authorize"
const devicecode_endpoint string = "https://login.microsoftonline.com/ddd3d26c-b197-4d00-a32d-1ffd84c0c295/oauth2/v2.0/devicecode"
const token_endpoint string = "https://login.microsoftonline.com/ddd3d26c-b197-4d00-a32d-1ffd84c0c295/oauth2/v2.0/token"
const redirect_uri string = "https://login.microsoftonline.com/ddd3d26c-b197-4d00-a32d-1ffd84c0c295/oauth2/nativeclient"
const tenant string = "ddd3d26c-b197-4d00-a32d-1ffd84c0c295"
const client_id string = "fea760d5-b496-4f63-be1e-93855c1c5f78"
const client_secret string = ""
const domainpart string = ""

type authmatrix_t struct {
	Email                 *string `json:"email"`
	AccessToken           *string `json:"access_token"`
	AccessTokenExpiration *int    `json:"access_token_expiration"`
	RefreshToken          *string `json:"refresh_token"`
}

func nope(err error) {
	if err != nil {
		panic(err)
	}
}

func main() {
	var authorize, path string
	flag.StringVar(&authorize, "authorize", "", "new email to authorize")
	flag.StringVar(&path, "path", "", "(required) path to storage file")
	flag.Parse()

	if path == "" {
		flag.Usage()
		return
	}

	if authorize == "" {
		data, err := os.ReadFile(path)
		nope(err)
		var authmatrix authmatrix_t
		err = json.Unmarshal(data, &authmatrix)
		nope(err)
		if authmatrix.Email == nil || authmatrix.AccessToken == nil || authmatrix.AccessTokenExpiration == nil || authmatrix.RefreshToken == nil {
			fmt.Fprintln(os.Stderr, "your storage file is broken")
			os.Exit(2)
		}
	} else { // authorize
		if !strings.HasSuffix(authorize, "@" + domainpart) {
			fmt.Fprintln(os.Stderr, "bad email or invalid domainpart")
			os.Exit(2)
		}
		fmt.Fprintln(os.Stderr, "authorize not implemented")
		os.Exit(2)
	}
}

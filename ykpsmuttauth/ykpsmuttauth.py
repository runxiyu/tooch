#!/usr/bin/env python3
#
# Mutt OAuth2 token management script, version 2020-08-07
# Written against python 3.7.3, not tried with earlier python versions.
# Modified for YK Pao School application registrations.
#
#   Copyright (C) 2020 Alexander Perlis
#   Copyright (C) 2024 Runxi Yu <me@runxiyu.org>
#
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation; either version 2 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#   02110-1301, USA.

import sys
import json
import argparse
import urllib.parse
import urllib.request
import imaplib
import smtplib
import base64
import secrets
import hashlib
import time
from datetime import timedelta, datetime
from pathlib import Path
import socket
import http.server
import subprocess
import readline


registrations = {
    "ykps": {
        "authorize_endpoint": "https://login.microsoftonline.com/ddd3d26c-b197-4d00-a32d-1ffd84c0c295/oauth2/v2.0/authorize",
        "devicecode_endpoint": "https://login.microsoftonline.com/ddd3d26c-b197-4d00-a32d-1ffd84c0c295/oauth2/v2.0/devicecode",
        "token_endpoint": "https://login.microsoftonline.com/ddd3d26c-b197-4d00-a32d-1ffd84c0c295/oauth2/v2.0/token",
        "redirect_uri": "https://login.microsoftonline.com/ddd3d26c-b197-4d00-a32d-1ffd84c0c295/oauth2/nativeclient",
        "tenant": "ddd3d26c-b197-4d00-a32d-1ffd84c0c295",
        "imap_endpoint": "outlook.office365.com",
        "smtp_endpoint": "smtp.office365.com",
        "sasl_method": "XOAUTH2",
        "scope": (
            "offline_access https://outlook.office.com/IMAP.AccessAsUser.All "
            "https://outlook.office.com/SMTP.Send"
        ),
        "client_id": "fea760d5-b496-4f63-be1e-93855c1c5f78",
        "client_secret": "",
    },
}

ap = argparse.ArgumentParser()
ap.add_argument("tokenfile", help="persistent token storage")
ap.add_argument(
    "-a", "--authorize", action="store_true", help="manually authorize new tokens"
)
args = ap.parse_args()

token = {}
path = Path(args.tokenfile)
if path.exists():
    token = json.loads(path.read_bytes())


def writetokenfile():
    """Writes global token dictionary into token file."""
    if not path.exists():
        path.touch(mode=0o600)
    path.write_bytes(json.dumps(token).encode())


print("Obtained from token file:", json.dumps(token), file=sys.stderr)
if not token:
    if not args.authorize:
        sys.exit('You must run script with "--authorize" at least once.')
    print("Available app and endpoint registrations:", *registrations, file=sys.stderr)
    token["registration"] = input("OAuth2 registration: ")
    token["email"] = input("Account e-mail address: ")
    token["access_token"] = ""
    token["access_token_expiration"] = ""
    token["refresh_token"] = ""
    writetokenfile()

if token["registration"] not in registrations:
    sys.exit(
        f'ERROR: Unknown registration "{token["registration"]}". Delete token file '
        f"and start over."
    )
registration = registrations[token["registration"]]

authflow = "localhostauthcode"

baseparams = {"client_id": registration["client_id"], "tenant": registration["tenant"]}


def access_token_valid():
    """Returns True when stored access token exists and is still valid at this time."""
    token_exp = token["access_token_expiration"]
    return token_exp and datetime.now() < datetime.fromisoformat(token_exp)


def update_tokens(r):
    """Takes a response dictionary, extracts tokens out of it, and updates token file."""
    token["access_token"] = r["access_token"]
    token["access_token_expiration"] = (
        datetime.now() + timedelta(seconds=int(r["expires_in"]))
    ).isoformat()
    if "refresh_token" in r:
        token["refresh_token"] = r["refresh_token"]
    writetokenfile()
    if args.verbose:
        print(
            f'NOTICE: Obtained new access token, expires {token["access_token_expiration"]}.',
            file=sys.stderr,
        )


if args.authorize:
    p = baseparams.copy()
    p["scope"] = registration["scope"]

    verifier = secrets.token_urlsafe(90)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())[
        :-1
    ]
    redirect_uri = registration["redirect_uri"]
    listen_port = 0

    # Find an available port to listen on
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    listen_port = s.getsockname()[1]
    s.close()
    redirect_uri = "http://localhost:" + str(listen_port) + "/"
    # Probably should edit the port number into the actual redirect URL.

    p.update(
        {
            "login_hint": token["email"],
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
    )
    print(
        registration["authorize_endpoint"]
        + "?"
        + urllib.parse.urlencode(p, quote_via=urllib.parse.quote),
        file=sys.stderr,
    )

    authcode = ""
    print(
        "Visit displayed URL to authorize this application. Waiting...",
        end="",
        flush=True,
        file=sys.stderr,
    )

    class MyHandler(http.server.BaseHTTPRequestHandler):

        def do_HEAD(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

        def do_GET(self):
            global authcode
            querystring = urllib.parse.urlparse(self.path).query
            querydict = urllib.parse.parse_qs(querystring)
            if "code" in querydict:
                authcode = querydict["code"][0]
            self.do_HEAD()
            self.wfile.write(b"<html><head><title>Authorizaton result</title></head>")
            self.wfile.write(
                b"<body><p>Authorization redirect completed. You may "
                b"close this window.</p></body></html>"
            )

    with http.server.HTTPServer(("127.0.0.1", listen_port), MyHandler) as httpd:
        try:
            httpd.handle_request()
        except KeyboardInterrupt:
            pass

    if not authcode:
        sys.exit("Did not obtain an authcode.")

    for k in (
        "response_type",
        "login_hint",
        "code_challenge",
        "code_challenge_method",
    ):
        del p[k]
    p.update(
        {
            "grant_type": "authorization_code",
            "code": authcode,
            "client_secret": registration["client_secret"],
            "code_verifier": verifier,
        }
    )
    print("Exchanging the authorization code for an access token", file=sys.stderr)
    try:
        response = urllib.request.urlopen(
            registration["token_endpoint"], urllib.parse.urlencode(p).encode()
        )
    except urllib.error.HTTPError as err:
        print(err.code, err.reason, file=sys.stderr)
        response = err
    response = response.read()
    print(response, file=sys.stderr)
    response = json.loads(response)
    if "error" in response:
        print(response["error"], file=sys.stderr)
        if "error_description" in response:
            print(response["error_description"], file=sys.stderr)
        sys.exit(1)

    update_tokens(response)


if not access_token_valid():
    if args.verbose:
        print(
            "NOTICE: Invalid or expired access token; using refresh token "
            "to obtain new access token.",
            file=sys.stderr,
        )
    if not token["refresh_token"]:
        sys.exit('ERROR: No refresh token. Run script with "--authorize".')
    p = baseparams.copy()
    p.update(
        {
            "client_secret": registration["client_secret"],
            "refresh_token": token["refresh_token"],
            "grant_type": "refresh_token",
        }
    )
    try:
        response = urllib.request.urlopen(
            registration["token_endpoint"], urllib.parse.urlencode(p).encode()
        )
    except urllib.error.HTTPError as err:
        print(err.code, err.reason, file=sys.stderr)
        response = err
    response = response.read()
    print(response, file=sys.stderr)
    response = json.loads(response)
    if "error" in response:
        print(response["error"], file=sys.stderr)
        if "error_description" in response:
            print(response["error_description"], file=sys.stderr)
        print('Perhaps refresh token invalid. Try running once with "--authorize"')
        sys.exit(1)
    update_tokens(response)


if not access_token_valid():
    sys.exit("ERROR: No valid access token. This should not be able to happen.")


# print("Access Token: ", end="", file=sys.stderr)
print(token["access_token"])


def build_sasl_string(user, host, port, bearer_token):
    return f"user={user}\1auth=Bearer {bearer_token}\1\1"


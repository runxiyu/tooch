#!/usr/bin/env python3

# crontab to change the profile photo every hour:
#
#    0 * * * * $HOME/cronstuff/chphoto.sh
#
# and chphoto.sh is just:
# 
#    cd $HOME/cronstuff/
#    . ./venv/bin/activate
#    pass=XXXXXXXXXXXXXXX ./tooch/chphoto.py -p pass sXXXXX@ykpaoschool.cn ./tooch/sjdb-avatar.png > marker
#    date >> marker


from __future__ import annotations
import logging
from pprint import pprint
from typing import Any
import argparse
import mimetypes
import os

import msal  # type: ignore
import requests

# logging.basicConfig(level=logging.DEBUG)
# logging.getLogger("msal").setLevel(logging.INFO)


def acquire_token_interactive(app: msal.PublicClientApplication, username: str) -> str:
    result = app.acquire_token_interactive(
        ["User.ReadWrite"],
        login_hint=username,
    )

    if "access_token" in result:
        assert type(result["access_token"]) is str
        return result["access_token"]
    else:
        raise ValueError(
            "Authentication error while trying to interactively acquire a token"
        )

def acquire_token_password(app: msal.PublicClientApplication, username: str, password: str) -> str:
    result = app.acquire_token_by_username_password(
        username=username,
        password=password,
        scopes=["User.ReadWrite"],
    )

    if "access_token" in result:
        assert type(result["access_token"]) is str
        return result["access_token"]
    else:
        raise ValueError(
            "Authentication error while trying to acquire a token using a password"
        )

def update_profile_photo(token: str, user_id: str, photo_path: str) -> None:
    graph_endpoint = "https://graph.microsoft.com/v1.0"
    url = f"{graph_endpoint}/users/{user_id}/photo/$value"

    with open(photo_path, "rb") as photo_file:
        photo_data = photo_file.read()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": mimetypes.guess_type(photo_path)[0],
    }

    response = requests.put(url, data=photo_data, headers=headers)

    print(response.status_code)
    print(response.content)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("email", help="username@ykpaoschool.cn")
    parser.add_argument("photo", help="path to avatar")
    parser.add_argument('-p', '--password-var', help="environment variable containing the password")
    args = parser.parse_args()
    app = msal.PublicClientApplication(
        "14f8346d-98c9-4f12-875f-3b2cabe7110a",
        authority="https://login.microsoftonline.com/organizations",
    )
    if args.password_var is None:
        token = acquire_token_interactive(app, args.email)
    else:
        token = acquire_token_password(app, args.email, os.environ[args.password_var])
    update_profile_photo(token, args.email, args.photo)


if __name__ == "__main__":
    main()

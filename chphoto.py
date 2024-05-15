#!/usr/bin/env python3

from __future__ import annotations
import logging
import msal  # type: ignore
import requests
from pprint import pprint
from typing import Any
import argparse
import mimetypes

# logging.basicConfig(level=logging.DEBUG)
# logging.getLogger("msal").setLevel(logging.INFO)


def acquire_token_interactive(
        app: msal.PublicClientApplication, username: str
) -> str:
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
    args = parser.parse_args()
    app = msal.PublicClientApplication(
        "14f8346d-98c9-4f12-875f-3b2cabe7110a",
        authority="https://login.microsoftonline.com/organizations",
    )
    token = acquire_token_interactive(app, args.email)
    update_profile_photo(token, args.email, args.photo)

if __name__ == "__main__":
    main()


#!/usr/bin/env python3

# This program is public domain, or under the terms of Creative Commons
# Zero 1.0 Universal, at your choice. In addition, a Waiver of Patent
# Rights apply. See the LICENSE file for details.

from __future__ import annotations
import requests
import time
import sys
import os


def rc4(plain: str, rc4key: str) -> str:
    plain = plain.strip()
    key_length = len(rc4key)
    sbox = list(range(256))
    key = [ord(rc4key[i % key_length]) for i in range(256)]

    j = 0
    for i in range(256):
        j = (j + sbox[i] + key[i]) % 256
        sbox[i], sbox[j] = sbox[j], sbox[i]

    a = b = 0
    output = []

    for char in plain:
        a = (a + 1) % 256
        b = (b + sbox[a]) % 256
        sbox[a], sbox[b] = sbox[b], sbox[a]
        c = (sbox[a] + sbox[b]) % 256
        temp = ord(char) ^ sbox[c]
        output.append(f"{temp:02x}")

    return "".join(output).lower()


def login(username: str, password: str) -> bytes:

    ts = str(int(time.time() * 100))
    r = requests.post(
        url="http://sjauth.ykpaoschool.cn/ac_portal/login.php",
        params={
            "opr": "pwdLogin",
            "userName": username,
            "pwd": rc4(password, ts),
            "rc4Key": ts,
            "auth_tag": ts,
            "rememberPwd": "1",
        },
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:104.0) Gecko/20100101 Firefox/104.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US.en;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "null",
            "Connection": "keep-alive",
        },
    )
    assert type(r.content) is bytes
    return r.content


def main() -> None:
    if len(sys.argv) != 3:
        print(
            "%s: Invalid arguments.  The first argument shall be your username, and the second shall be the name of the environment variable containing your password."
            % sys.argv[0],
            file=sys.stderr,
        )
        sys.exit(22)

    username = sys.argv[1]
    try:
        password = os.environ[sys.argv[2]]
    except KeyError:
        print(
            "%s: Environment variable %s does not exist.  You shall cause the variable identified by %s to contain your password."
            % (sys.argv[0], sys.argv[2], sys.argv[2]),
            file=sys.stderr,
        )
        sys.exit(22)

    print(login(username, password))


if __name__ == "__main__":
    main()

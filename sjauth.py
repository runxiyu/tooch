#!/usr/bin/env python3

from __future__ import annotations
import requests
import time
import sys
import os


def crypt(thing: str, rc4: str) -> str:
    thing = thing.strip()
    i = 0  # loop iterator
    j = 0
    a = 0
    b = 0
    c = 0
    temp = 0  # no idea what this is supposed to be

    key = 256 * [0]
    sbox = 256 * [0]
    output = len(thing) * ["\0"]

    for i in range(256):
        key[i] = ord(rc4[i % len(rc4)])
        sbox[i] = i

    for i in range(256):
        j = (j + sbox[i] + key[i]) % 256
        temp = sbox[i]
        sbox[i] = sbox[j]
        sbox[j] = temp

    for i in range(len(thing)):
        a = (a + 1) % 256
        b = (b + sbox[a]) % 256
        temp = sbox[a]
        sbox[a] = sbox[b]
        sbox[b] = temp
        c = (sbox[a] + sbox[b]) % 256
        temp = ord(thing[i]) ^ sbox[c]  # bitwise XOR
        temp1 = "%0.2X" % temp
        if len(temp1) == 1:
            temp1 = "0" + temp1
        elif len(temp1) == 0:
            temp1 = "00"
        output[i] = temp1

    return "".join(output).lower()


def login(username: str, password: str) -> bytes:

    ts = str(int(time.time() * 100))
    r = requests.post(
        url="http://sjauth.ykpaoschool.cn/ac_portal/login.php",
        params={
            "opr": "pwdLogin",
            "userName": username,
            "pwd": crypt(password, ts),
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

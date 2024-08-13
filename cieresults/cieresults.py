#!/usr/bin/env python3
#
# Poll myresults.cie.org.uk and announce the availability of results to an IRC channel.
#
# Copyright (c) 2024 Runxi Yu <https://runxiyu.org>
# SPDX-License-Identifier: BSD-2-Clause
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#     2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import miniirc  # type: ignore
import requests
import bs4
import time

initial_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "TE": "trailers",
    "Origin": "https://myresults.cie.org.uk",
    "Host": "myresults.cie.org.uk",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "DNT": "1",
    "Sec-GPC": "1",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Priority": "u=0, i",
}

ping = "runxiyu, rx"

irc_config = {
    "nick": "cieresults",
    "ip": "irc.runxiyu.org",
    "port": 6697,
    "channels": ["#chat"],
    "ssl": True,
    "ident": "cieresults",
    "realname": "Bot to poll CIE results",
    "quit_message": "Leaving",
}

print("[*] Creating IRC object")
irc = miniirc.IRC(**irc_config)

def main() -> int:
    print("[*] Connecting to IRC")
    irc.connect()
    return 0


@irc.Handler("001", colon=False)  # type: ignore
def handle(irc, hostmask, args) -> None:
    print("[*] Initialized connection to IRC (001 received)")
    while True:
        print("[*] --------------- Polling --------------------")
        with open("cieauth.txt", "r") as fd:
            e = fd.readlines()
        username = e[0].strip()
        password = e[1].strip()

        s = requests.Session()
        s.headers.update(initial_headers)
        r = s.get("https://myresults.cie.org.uk/cie-candidate-results/login")
        if r.status_code != 200:
            print("[!] Login page returned status code %d" % r.status_code)
            continue
        print("[*] Fetched login page to consume the cookies")
        r = s.post(
            "https://myresults.cie.org.uk/cie-candidate-results/j_spring_security_check",
            data={"j_username": username, "j_password": password},
        )
        if r.status_code != 200:
            print("[!] Results page returned status code %d" % r.status_code)
            continue
        print("[*] Fetched results web page")

        soup = bs4.BeautifulSoup(r.text, features="html.parser")

        # soup = bs4.BeautifulSoup(open("bs.html", "r").read())

        div_yourresults = soup.find(id="yourresults")
        table = div_yourresults.find(  # type: ignore
            "table", summary="Your examination results for June 2024"
        )
        tbody = table.find("tbody") # type: ignore
        rows = tbody.find_all("tr") # type: ignore

        out_subjects = []
        not_out_subjects = []

        for row in rows:
            td1, td2, td3 = row.find_all("td")
            span1, span2 = td1.find_all("span")
            subject = "%s %s" % (span1.string.strip(), span2.string.strip())
            results = td3.string.strip()

            if results == "Results to be released":
                print("[-] %s: %s" % (subject, results))
                not_out_subjects.append(subject)
            else:
                print("[+] %s: %s\a" % (subject, results))
                out_subjects.append(subject)


        if out_subjects:
            for channel in irc_config["channels"]: # type: ignore
                irc.msg(
                    channel, "%s: Results out for %s" % (ping, ", ".join(out_subjects))
                )
        # if not_out_subjects:
        #     for channel in irc_config["channels"]: # type: ignore
        #         irc.msg(
        #             channel,
        #             "%s: Results NOT out for %s" % (ping, ", ".join(not_out_subjects)),
        #         )

        print("[*] Waiting for 300 seconds before polling again")
        time.sleep(300)


if __name__ == "__main__":
    exit(main())

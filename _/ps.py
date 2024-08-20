# this is really hacky please don't use it
# copyright (c) 2024 runxi yu
# SPDX-License-Identifier: BSD-2-Clause

import requests
import os
import sys
import time
import base64

while True:
    ss = requests.Session()
    rq = ss.post(
        "https://powerschool.ykpaoschool.cn/guardian/home.html",
        data={
            "request_locale": "en_US",
            "account": sys.argv[1],
            "pw": os.environ[sys.argv[2]],
            "ldappassword": os.environ[sys.argv[2]],
        },
    )
    t = (
        ss.get("https://powerschool.ykpaoschool.cn/guardian/home.html")
        .text.replace("ISO-8859-1", "utf-8")
        .encode("utf-8")
        .decode("utf-8", "replace")
    )
    tl = t.lower()
    if "英文" in tl or "Math" in tl:
        print("\a\a\aSending email")
        with open("ekekek.eml", "w") as p:
            p.write(
                "To: me@runxiyu.org\r\n"
                + "From: me@runxiyu.org\r\n"
                + "Subject: Timetable results\r\n"
                + 'Content-Type: text/html; charset="utf-8"\r\n'
                + "Content-Transfer-Encoding: base64\r\n"
                + "\r\n"
                + base64.standard_b64encode(
                    (
                        "<style>body{min-width:60rem;}%s</style>"
                        % open("screen.css").read()
                        + t
                    ).encode("utf-8")
                ).decode("utf-8", "error")
            )
            p.close()
            print(
                "\a\a\aDone! Sendmail finished with %s"
                % repr(os.system("/sbin/sendmail -i me@runxiyu.org < ekekek.eml"))
            )
        break
    else:
        print(t)
    time.sleep(600)

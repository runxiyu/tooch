#!/usr/bin/env python3
#
# Script to turn PowerSchool calendars to iCalendar
#
# Copyright (c) 2023, 2024 Runxi Yu <https://runxiyu.org>
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

import requests
import bs4
import os
import ics  # type: ignore
from pprint import pprint
from datetime import datetime

username = input("Username: ")
password = input("Password: ")

ss = requests.Session()

rq = ss.post(
    "https://powerschool.ykpaoschool.cn/guardian/home.html",
    data={
        "request_locale": "en_US",
        "account": username,
        "pw": password,
        "ldappassword": password,
    },
)

# TODO: Handle failed logins

cs = [
    (
        se[-3].contents[0].strip("\xa0"),
        se[-3].contents[4].contents[0].replace("Email ", ""),
        se[-3].contents[5].replace("\xa0-\xa0Rm: ", ""),
        se[0].contents[0],
        se[-3].contents[4]["href"].replace("mailto:", "")
    )
    for se in [
        [tx for tx in cz.contents if type(tx) is bs4.element.Tag]
        for cz in bs4.BeautifulSoup(
            ss.get("https://powerschool.ykpaoschool.cn/guardian/home.html").text,
            features="lxml",
        )
        .find("table", class_="linkDescList grid")
        .find_all("tr", class_="center", recursive=False)
        if cz.get("id", "").startswith("ccid_")
    ]
]


cycle = {
    "A": [None, None, None, None, None, None],
    "B": [None, None, None, None, None, None],
    "C": [None, None, None, None, None, None],
    "D": [None, None, None, None, None, None],
    "E": [None, None, None, None, None, None],
    "F": [None, None, None, None, None, None],
}

datemap = {
    "A": [],
    "B": [],
    "C": [],
    "D": [],
    "E": [],
    "F": [],
}

periodtimes = [("00:00:00","01:00:00"),
               ("01:05:00","02:05:00"),
               ("02:20:00","03:20:00"),
               ("03:25:00","04:25:00"),
               ("05:40:00","06:40:00"),
               ("06:45:00","07:45:00")]

periodtimesfri = [("00:00:00","00:55:00"),
                  ("01:00:00","01:55:00"),
                  ("02:10:00","03:05:00"),
                  ("03:10:00","04:05:00"),
                  ("05:05:00","06:00:00"),
                  ("06:05:00","07:00:00")]

datemapst = [l.rstrip("\n").split(",") for l in open("cycle2024.csv", "r").readlines()]
for dme in datemapst:
    try:
        datemap[dme[0]].append(dme[1])
    except KeyError:
        print("[SKIPPING] Invalid datemap %s" % dme)

cal = ics.Calendar()
for course in cs:
    for pset in course[3].split(" "):
        pset = pset.rstrip(")")
        pset = pset.split("(", 1)
        try:
            period_number = int(pset[0])
        except ValueError:
            continue
        try:
            assert 1 <= period_number <= 6
        except AssertionError:
            print("[SKIPPING] Period number %d not from 1 to 6" % period_number)
        for day in pset[1].split(","):
            cycle[day][period_number - 1] = (course[0], course[1], course[2])
            for date in datemap[day]:
                ev = ics.Event()
                ev.name = course[0]
                ev.organizer = ics.Organizer(course[4], common_name = course[1])
                ev.location = course[2]
                dow = datetime.strptime(date, "%Y-%m-%d").weekday()
                if dow == 4:
                    ev.begin = date + " " + periodtimesfri[period_number - 1][0]
                    ev.end = date + " " + periodtimesfri[period_number - 1][1]
                else:
                    ev.begin = date + " " + periodtimes[period_number - 1][0]
                    ev.end = date + " " + periodtimes[period_number - 1][1]
                cal.events.add(ev)
    
with open("%s.ics" % username, "w") as wc:
    wc.writelines(cal.serialize_iter())
    wc.close()

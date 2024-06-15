#!/usr/bin/env python3
#
# Generate timetables from YKPS PowerSchool
# Copyright (C) 2023  Runxi Yu <a@andrewyu.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import requests
from flask import Flask
from flask import render_template, request, redirect, abort, send_from_directory
from flask.wrappers import Response
import rtfunicode
import bs4
import os
import ics
from datetime import datetime


app = Flask(__name__)

def get_rtf_and_ical(username, password):
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
    
    try:
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
    except AttributeError:
        return False 
    
    
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
    
    datemapst = [l.rstrip("\n").split(",") for l in open("cycle2023.csv", "r").readlines()]
    for dme in datemapst:
        try:
            datemap[dme[0]].append(dme[1])
        except KeyError:
            raise ValueError("Datemap includes invalid cycle day identifier %s" % dme[0])
    
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
                raise ValueError("Period number %d not from 1 to 6" % period_number)
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
    
    with open("gen/%s.ics" % username, "w") as wc:
        wc.writelines(cal.serialize_iter())
        wc.close()

    return True

def sane_username(u):
    if not u.startswith("s"): return False
    if len(u) != 6: return False
    try:
        int(u[1:])
    except ValueError:
        return False
    return True

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('front.html')
    elif request.method == 'POST':
        if "username" in request.form and sane_username(request.form["username"]) and "password" in request.form:
            if get_rtf_and_ical(request.form["username"], request.form["password"]):
                return render_template('back.html', username=request.form["username"])
            else:
                return render_template("fail.html"), 401
        else:
            return render_template("stupid.html"), 401
    return "405 Method Not Allowed\n", 405

@app.route('/gen/<path:path>')
def sg(path):
    return send_from_directory('gen', path)

if __name__ == "__main__":
    app.run(port=8000)

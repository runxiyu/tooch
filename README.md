# Scripts, utilities, and other files related to life at YK Pao School

| Name           | Description                                            | Language | Dependencies                                                                                                                                                          |
| -------------- | ------------------------------------------------------ | -------- | ---------------------------------------                                                                                                                               |
| `chphoto`      | Change Outlook profile photos                          | Go       | [MSAL](https://github.com/AzureAD/microsoft-authentication-library-for-go)                                                                                            |
| `pdfutils`     | Scripts to manipulate PDFs                             | Shell    | [Ghostscript](https://www.ghostscript.com), [Chromium](https://www.chromium.org)                                                                                      |
| `sjauth`       | Log on to [STUWIRELESS](https://ykps.runxiyu.org/wifi) | C        | [libcurl](https://curl.se/libcurl/)                                                                                                                                   |
| `ykpsmuttauth` | Get Outlook XOAUTH2 tokens for mutt/aerc               | Go       |                                                                                                                                                                       |
| `cieresults`   | Poll the IGCSE results page to IRC                     | Python   | [requests](http://docs.python-requests.org/), [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/), [miniirc](https://github.com/luk3yx/miniirc)      |
| `calgen`       | Generate iCalendar from PowerSchool timetables         | Python   | [requests](http://docs.python-requests.org/), [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/), [Ics.py](https://icspy.readthedocs.io/en/stable/) |
| `paoprint`     | LPD/PDL student printer driver for the SJ Campus       | C        | [Ghostscript](https://www.ghostscript.com)                                                                                                                            |

## Build

There is a Makefile in each subdirectory that builds the relevant program, for
programs written in compiled languages. They should support both BSD Make and
GNU Make.

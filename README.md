# Scripts, utilities, and other files related to life at YK Pao School

| Name           | Language | Description                                            | Dependencies                                                                                                                                                          |
| -------------- | -------- | ------------------------------------------------------ | ---------------------------------------                                                                                                                               |
| `chphoto`      | Go       | Change Outlook profile photos                          | [MSAL](https://github.com/AzureAD/microsoft-authentication-library-for-go)                                                                                            |
| `memch`        | C        | Help memorize classical Chinese texts                  | [ncursesw](https://invisible-island.net/ncurses/)                                                                                                                     |
| `pdfutils`     | Shell    | Scripts to manipulate PDFs                             | [Ghostscript](https://www.ghostscript.com), [Chromium](https://www.chromium.org)                                                                                      |
| `sjauth`       | C        | Log on to [STUWIRELESS](https://ykps.runxiyu.org/wifi) | [libcurl](https://curl.se/libcurl/)                                                                                                                                   |
| `ykpsmuttauth` | Go, C    | Get Outlook XOAUTH2 tokens for mutt/aerc               | [libcurl](https://curl.se/libcurl/), [json-c](https://github.com/json-c/json-c), [OpenSSL](https://www.openssl.org)                                                   |
| `cieresults`   | Python   | Poll the IGCSE results page to IRC                     | [requests](http://docs.python-requests.org/), [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/), [miniirc](https://github.com/luk3yx/miniirc)      |
| `calgen`       | Python   | Generate iCalendar from PowerSchool timetables         | [requests](http://docs.python-requests.org/), [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/), [Ics.py](https://icspy.readthedocs.io/en/stable/) |
| `paoprint`     | C        | LPD/PDL student printer driver for the SJ Campus       | [Ghostscript](https://www.ghostscript.com)                                                                                                                            |

## Build

There is a Makefile in each subdirectory that builds the relevant program, for
programs written in compiled languages. They should support both BSD Make and
GNU Make.

## Contributing

Issues and post requests submitted via the
[Codeberg](https://codeberg.org/runxiyu/tooch) and
[Github](https://github.com/runxiyu/tooch) repositories are accepted. However,
the maintainer prefers [emailed patches](https://git-send-email.io) and emailed
bug reports, to the [mailing list](https://lists.sr.ht/~runxiyu/ykps). The
[sr.ht](https://git.sr.ht/~runxiyu/tooch) and
[git.runxiyu.org](https://git.runxiyu.org/runxiyu/tooch.git) repositories are
the "official" copies.

# Scripts, utilities, and other files related to life at YK Pao School

| Name           | Language | Description                                            | Dependencies                        |
| -------------- | -------- | ------------------------------------------------------ | ----------------------------------- |
| `chphoto`      | Go       | Change Outlook profile photos                          | `msal`                              |
| `memch`        | C        | Help memorize classical Chinese texts                  | `ncursesw`                          |
| `pdfutils`     | Shell    | Scripts to manipulate PDFs                             | (Various)                           |
| `sjauth`       | C        | Log on to [STUWIRELESS](https://ykps.runxiyu.org/wifi) | `libcurl`                           |
| `ykpsmuttauth` | Go, C    | Get Outlook XOAUTH2 tokens for mutt/aerc               | `libcurl`, `c-json`, `openssl`      |
| `cieresults`   | Python   | Poll the IGCSE results page                            | `requests`, `beautifulsoup4`        |
| `calgen`       | Python   | Generate iCalendar from PowerSchool timetables         | `requests`, `beautifulsoup4`, `ics` |

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

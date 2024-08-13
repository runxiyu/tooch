# Scripts, utilities, and other files related to life at YK Pao School

While I try to make things portable, sometimes I might foget, so there is no guarantee that any of this would run on macOS. They should, however, at least work on Alpine and Fedora, and on most other Linux-based systems too.

## Contents

|   Program    |Language|                      Description                     |
|--------------|--------|------------------------------------------------------|
|`chphoto`     |Go      |Change Outlook profile photos                         |
|`memch`       |C       |Help memorize classical Chinese texts                 |
|`pdfutils`    |Shell   |Help manipulate PDFs                                  |
|`sjauth`      |C       |Log on to [STUWIRELESS](https://ykps.runxiyu.org/wifi)|
|`ykpsmuttauth`|Go, C   |Get XOAUTH2 tokens for mutt/aerc for Outlook          |
|`cieresults`  |Python  |Poll the IGCSE results page                           |

## Build

There is a Makefile in each subdirectory that builds the relevant program.

Only GNU Make is supported. Users on BSD systems should call `gmake` instead of `make`.

## Contributing

Issues and post requests submitted via the [Codeberg](https://codeberg.org/runxiyu/tooch) and [Github](https://github.com/runxiyu/tooch) repositories are accepted. However, the maintainer prefers [emailed patches](https://git-send-email.io) and emailed bug reports, to the [mailing list](https://lists.sr.ht/~runxiyu/ykps). The [sr.ht](https://git.sr.ht/~runxiyu/tooch) and [git.runxiyu.org](https://git.runxiyu.org/runxiyu/tooch.git) repositories are the "official" copies.

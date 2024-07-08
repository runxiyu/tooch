# Scripts, utilities, and other files related to life at YK Pao School

Most of these are written in C, Go, shell script, and occasionally prototypes in Python. While I try to make things portable, sometimes I might foget, or sometimes GNU Bash extensions are just too convenient, so there is no guarantee that any of this would run on macOS. But they should at least work on Asahi/Fedora.

## Contents

|Program|Language|Description|
|--|--|--|
|`chphoto`|Go|Change Outlook profile photos|
|`memch`|C|Help memorize classical Chinese texts|
|`pdfutils`|Shell|Help manipulate PDFs|
|`sjauth`|C|Log on to [STUWIRELESS](https://ykps.runxiyu.org/wifi)|
|`ykpsmuttauth`|Go|Get XOAUTH2 tokens for mutt/aerc for Outlook|

## Build

Only GNU Make is supported. Users on BSD systems should call `gmake` instead of `make`.

The top-level makefile simply builds subdirectories. Each subdirectory is a phony target, so you could type `make sjauth` to build `sjauth`. The resulting binary is copied to `bin/sjauth`. The `install` target *additionally* causes the binaries to be copied over to `~/.local/bin/`.

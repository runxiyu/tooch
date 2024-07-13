# ykpsmuttauth

This simple program allows you to obtain an XOAUTH2 token for your YK Pao School Microsoft account. This is useful as a replacement for [`mutt_oauth2.py`](https://raw.githubusercontent.com/muttmua/mutt/master/contrib/mutt_oauth2.py).

There are two implementations. One is a rather complete Go implementation, `ykpsmuttauth`, and one is a not really complete C implementation, `ykpsmuttauth2`.

|Feature|Go|C|
|-------|--|-|
|Authorize an account for the first time|Yes|No|
|Retrieve a new access token from a refresh token|Yes|Yes|
|Print an already-valid access token|Yes|Yes|

The C implementation can read files produced by the Go implementation. It doesn't work the other way around because of some broken timezone handling.

The Go implementation has no dependencies other than the Go standard library. The C implementation depends on a POSIX standard library, and `openssl` for hashing, `libcurl` for HTTP requests, and `json-c` for JSON parsing and writing.

## Usage

```
Usage of ./ykpsmuttauth:
  -authorize string
    	email to newly authorize
  -tokenfile string
    	(required) persistent token storage
```

```
Usage: ./ykpsmuttauth2 <tokenfile>
```

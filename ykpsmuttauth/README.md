# ykpsmuttauth

This simple program allows you to obtain an XOAUTH2 token for your YK Pao School Microsoft account. This is useful as a replacement for [`mutt_oauth2.py`](https://raw.githubusercontent.com/muttmua/mutt/master/contrib/mutt_oauth2.py).

## Usage

```
Usage of ./ykpsmuttauth:
  -authorize string
    	email to newly authorize
  -tokenfile string
    	(required) persistent token storage
```


## Using with [`aerc`](https://sr.ht/~rjarry/aerc/)

First run `ykpsmuttauth -tokenfile ~/.cache/aerc/token.txt -authorize s65535@ykpaoschool.cn`.

```ini
[school]
from              = Your Name <s65535@ykpaoschool.cn>
default           = INBOX
copy-to           = Sent Items
source            = imaps+xoauth2://s65535%40ykpaoschool.cn@outlook.office365.com
outgoing          = smtp+xoauth2://s65535%40ykpaoschool.cn@outlook.office365.com:587
# To use the Go implementation:
source-cred-cmd   = ykpsmuttauth -tokenfile ~/.cache/aerc/token.txt
outgoing-cred-cmd = ykpsmuttauth -tokenfile ~/.cache/aerc/token.txt
# Or to use the C implementation:
# source-cred-cmd   = ykpsmuttauth2 ~/.cache/aerc/token.txt
# outgoing-cred-cmd = ykpsmuttauth2 ~/.cache/aerc/token.txt
```

# cieresults

This is an IRC bot that polls [the CIE results
page](https://myresults.cie.org.uk/cie-candidate-results/results) and announces
the prescence of results to an IRC channel.

Available under the 2-clause BSD license.

## Usage

Install dependencies (BeautifulSoup4, miniirc, requests):
```sh
python3 -m pip install -r requirements.txt
```

Add your myresults.cie.org.uk username and password to `cieauth.txt`, separated
by newlines:
```
username
passwod
```

Then, modify `cieresuts.py` and modify the `irc_config` dictionary to your
liking:
```python
irc_config = {
    "nick": "cieresults",
    "ip": "irc.runxiyu.org",
    "port": 6697,
    "channels": ["#chat"],
    "ssl": True,
    "ident": "cieresults",
    "realname": "Bot to poll CIE results",
    "quit_message": "Leaving",
}
```

# chphoto

This simple program allows you to change profile pictures on the YK Pao School outlook directory.

## Authentication

Please run without `-passvar` when using for the first time, as interactive authentication is required for the application to receive consent. Subsequent runs may use pasword authentication, for example, for automation purposes.

## Usage

```
Usage of ./chphoto:
  -email string
    	(required) username@ykpaoschool.cn
  -passvar string
    	environment variable containing the password
  -photo string
    	(required) path to avatar
```

## Note on daily reset

The profile pictures are reset approximately every day. Use a cron job, or otherwise run this script frequently, to make the change persist.

```crontab
0 * * * * $HOME/cronstuff/chphoto.sh
```

```sh
cd $HOME/cronstuff/
pass=XXXXXXXXXXXXXXX ./tooch/chphoto/chphoto -passvar pass -email sXXXXX@ykpaoschool.cn -photo ./tooch/sjdb-avatar.png
```

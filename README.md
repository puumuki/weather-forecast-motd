# MOTD - Message of the day 

Script prints message of the day when a user logs in Rabsberry PI via SSH connection.

Output print example:

```
Tassukka - Tampere - 26.1.2020 15:45
Lämpötila 1.68°C tuntuu -2.5°C
Korkein lämpötila 2.22°C matalin 0.56°C
Paine 997Pa kosteus 84%
Aurinko nousee 09:03 laskee 16:10
```

# Wheather forecast

Weather forecast is read from `api.openweathermap.org`, to use it you need to create an account to theyr web site. Ohterwise the weather forecast data could not be downloaded.

# Setup & installing

Ideally setting and updating the package is easy as running next command:

```
pip install weather-forecast-motd
```

But like in a real world it not that easy, but fear not my young Padavan! There is more! Next you need to create a `.modtrc` file. Ideally this is located `/etc/.motdrc`.`.

File looks something like this:

```
[Default]
API_KEY = <api key>
CACHE_TIME = 60
CITY = Tampere
```

After `.modtrc` is created under `/etc/` directory you can try to run the script by typin `motd` and it should print something like in the example output. 

Configuraton file is searched from `~/.motdrc`, `~/motdrc`, `/etc/.motdrc` or `/etc/motdrc`

# Final installation

Search for the file called `motd.tlc` under `/etc` directory. This is a file that is executed every sign in by the system. File is accessed by the `root` user. So it's use this at your own risk! 

Insert this text to some where in the motd.tlc file:
```
motd
```


Only direct dependency of this package is `pystache` that handle those nice `Mustache` templates. But yes, if there is a security vulnerability on somewhere in the code there might be a way to exploit it. Use this packages by you own risk! This script is probaly excecuted by `root` user. :/

__Configurations__

 * `API_KEY` is `api.openweathermap.org` api key that you can obtain from theyr website.
 * `CACHE_TIME` is cache expiration time in seconds. This is time in seconds how long the weather forecast information is hold in cache. Before the cache expires date is returned from the cache.
 * `CITY` Place where you the forecast is read from. 

# Custom templating

Note: `not implemented!`

The message can be changed and modified to your liking by modifying `.motdrc` file. You can create your own custom Mustache template file that you can use to print the message of the day.

__Bash Styles__

These styles can be used in the mustache template to give some color for the message.

```
BASH_STYLES = {
  'HEADER': '\033[95m',
  'OKBLUE': '\033[94m',
  'OKGREEN': '\033[92m',
  'WARNING': '\033[93m',
  'FAIL': '\033[91m',
  'ENDC': '\033[0m',
  'BOLD': '\033[1m',
  'UNDERLINE': '\033[4m'
}
```
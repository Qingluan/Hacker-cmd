# Hacker-cmd
some tools in python

#	Usage

### install
> brew install redis # mac
> apt-get install redis-server

### run service

> brew services start redis / service redis start

> pip3 install hackcmds

> # first use need to update zsh/bash_history's content to redis

> Hacker -uh 

> Hacker -c # to create a new cmds


usage:  how to use this

This is a script to make a new cmd to execute sub cmds example: -c to make a
cmd 'scan url=xxx' which include 'whois {url}' 'host {url}' --- write by
qingluan

optional arguments:
  -h, --help            show this help message and exit
  -c, --create          create mode
  -s SEARCH, --search SEARCH
                        search cmd from history and db.
  -uh, --update-history
                        search cmd from history and db.
  -D, --delete          delete some cmds in DB. [interact mode]
  -V, --console         if see console's log.
  -lm, --list-multi     show combination cmd in DB.
  -st SH, --sh SH       set sh's type , default is zsh
  -v, --verbos          more info.


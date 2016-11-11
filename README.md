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

This is a script to make a new cmd to execute sub cmds , or run Modules. #
will run Module first , then if no Module found will run cmds_comb example: -c
to make a cmd 'scan url=xxx' which include 'whois {url}' 'host {url}' ---
write by qingluan

optional arguments:
  -h, --help            show this help message and exit
  -c, --create          create mode
  -s SEARCH, --search SEARCH
                        search cmd from history and db.
  -uh, --update-history
                        search cmd from history and db.
  -D, --delete          delete some cmds in DB. [interact mode]
  --init                init this project .. to create DB.
  -V, --console         if see console's log.
  -lm, --list-multi     show combination cmd in DB.
  -A ADD_MODULE, --add-module ADD_MODULE
                        add a hacker module code .
  -st SH, --sh SH       set sh's type , default is zsh
  -v, --verbos          more info.


## Modules

	this tool can add a Module to 'site-package/Hackcmds' path by '-A' option

	when you add a option , can use it as cmd_comb

<code>
	$ Hacker -A Urls
	... if run as shell type , shell cmd
  ... like 'egrep -Inr' 'ping -f 10' 
   >>
	# you can type a cmd like 'ping -f 5' or nothing
	$ ipython
  ...
	[1] : from Hacker.Urls import Urls # you can see , this package will add a Module
	<code>
		# this module like
from Hacker.hackerlib import Module


class <name>(Module):

    def init_args(self):
        return {
            "path": "set a root path to detect code.",
        }

    def init_payload(self, **kargs):
        """
        """
        self.options.update(kargs)
        self.payloads = [i[0] for i in self.get_res("payload")]
        self.options['shell'] = "<cmd>  \"{payload}\""

    def run(self, options_and_payload, **kargs):
        sh = self.options['shell']
        return self.shell(sh.format(**options_and_payload), **kargs)
	</code>
	
</code>

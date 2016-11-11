# Hacker-cmd
some tools in python

#	Usage

### install> brew install redis # mac
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

> Hacker -A  UrlsSpy # can add a file named UrlsSpy.py to  $PYTHON/site-package/Hacker/  

    when you add a option , can use it as cmd_comb

> Hacker UrlsSpy  args=xxx  args2=xxx2 ….  
> # the ‘args ‘  you can see  by   
> Hacker  UrlsSpy help=t  
> …       path                        
> 			set a root path to detect code.  
>   

you can add payloads to  each Module by 

> Hacker  <Module> new_res=“arg,args, arg,” / “a file’s path”  

    class (Module):
    	def init_args(self):
        		return {
            		"path": "set a root path to detect code.",
        		}
    	def init_payload(self, **kargs):
        """
        """
        self.options.update(kargs)
        self.payloads = [i[0] for i in 	self.get_res("payload")]
        self.options['shell'] = "<cmd>  \"{payload}\""
    
    	def run(self, options_and_payload, **kargs):
        sh = self.options['shell']
        return self.shell(sh.format(**options_and_payload), **kargs)
    
    # this is templates:
    #	infact you just need to inherit 'Module'
    # like this
    
    class Xxx(Module):
    	def init_args(self):
    		"""
    		this function is just for 'help' terminal
    		"""
    		return {
    			'args' : 'some description for this option',
    			...
    		}
    	def init_payloads(self, **kargs):
    		"""
    		this function is a way to set options and get payloads from DB 
    		"""
    		self.options ..
    		self.payloads ...
    		self.options['shell'] = 'xxxx {payload}' #  xxxx is a key to run in local os .payload will wrap from payloads , by use 'for payload in payloads:' 
    	
    	def run(self, payload):
    		.... # how to use payload 
    		# this function will be excuted by self.ex
    		# self.ex's code
    		# 
    		#  def ex(self):
          # 	 for payload in self.payloads:
          #     	self.options['payload'] = payload
          #      	self.run(self.options)

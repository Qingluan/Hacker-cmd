import os, sys
from importlib import util

from qlib.data.sql import SqlEngine
from qlib.data import GotRedis


# some shortcut . let it easy.
J = os.path.join 
ENV = os.getenv

redis = GotRedis()

DB_PATH = J(ENV('HOME'), '.hacker_cmds')

DB_Handler = SqlEngine(database=DB_PATH)

if 'templates' not in [ i[0] for i in DB_Handler.table_list()]:
    DB_Handler.create('templates', cmd=str, keys='target', group_key='comba', output='default.log')


# ETC_FILE = J('/usr/local/etc/', 'hack.')

OUTPUT_DIR = '/tmp/HackerOutput/'
ROOT_DIR = list(util.find_spec("Hacker").submodule_search_locations).pop()
RES = J(ROOT_DIR, 'res')
TEMPLATE_PATH = J(J(ROOT_DIR, 'ini'), 'TEMPLATES.py')
MODULE_PATH = J(list(util.find_spec("Hacker").submodule_search_locations).pop(), 'modules')
try:
    os.makedirs(OUTPUT_DIR)
except FileExistsError:
    pass


def init():
    if 'templates' not in [ i[0] for i in DB_Handler.table_list()]:
        DB_Handler.create('templates', cmd=str, keys='target', goup_key='comba', output='default.log')
    if 'modules' not in [ i[0] for i in DB_Handler.table_list()]:
        DB_Handler.create('modules', name='module_name', direction="Unknow")

    for f in os.listdir(RES):
        if f.endswith('.ini'):
            with open(J(RES , f)) as fp:
                for line in fp:
                    tmp = line.split(",")
                    DB_Handler.insert('modules', ['name', 'direction'], *tmp)


MODULES_TEMPLATE = """
from Hacker.libs.hackerlib import Module, J
from Hacker.libs.hackerlib import LogControl, colored
LogControl.LOG_LEVEL = LogControl.OK
LogControl.LOG_LEVEL |= LogControl.WRN
LogControl.LOG_LEVEL |= LogControl.FAIL


class {module_name}(Module):
    \"\"\"
developer:
    asynchrouns function : Asyn( func , *args, **kargs)
        the result will pass to function: done(*args)

    network function: GET (url, **kargs), 
                      POST(url, **data)

    Module <--|name|--> : help
    \"\"\"

    def init_args(self):
        \"\"\"
        this function will generate a api.
            will use 'parser.add_argument()'
            examp: <--|
                'url' :  "set a target url"
                    ...
            |-->
            the 'url' will be parse to :
                parser.add_argument("--url", default=None, help="set a target url")
            ...
            
            examp:
            if key's all case is upcase. will gen a positional arg.
            <--|
                'URL': 'set a target url',
                ...
            |-->
            -->
                parser.add_argument("url", default=None, help="set a target url")

            examp: 
            if key startswith upcase. will be follow
            <--|
                'Url' :  "set a target url"
                    ...
            |-->
             -->
                parser.add_argument("-u", "--Url", default=None, help="set a target url")

            examp: 
            if value is boolean.
            <--|
                'ed' :  (False,  "end some ?")
                    ...
            |-->
            

            --> 
                parser.add_argument("--ed", default=False, help="end some?")

            examp: 
            if key ends with "*".
            <--|
                'ed*' :  (False,  "end some ?")
                    ...
            |-->
            

            --> 
                parser.add_argument("--ed", nargs='*',default=False, help="end some?")
        \"\"\"
        return <--|
            "doc": self.__doc__.format(name=colored(self.module_name, "green", attrs=['bold','underline'])),
        |-->

    def done(self, *args):
        \"\"\"

        this is how to dealwith each thread's result.
            by use self.Asyn(func , *targs, **kargs)
            the *args will got from func's results.
        \"\"\"
        # 
        pass

    def parser(self):
        \"\"\"
        options how to run.
        \"\"\"
        # template.
        #if 'Url' in self.options:
        #    self.options['u'] = self.options['Url']
        pass

    def init_payload(self, **kargs):
        \"\"\"
        \"\"\"
        self.options.update(kargs)
        #  get_res("xxx") will get column 'xxx' all data
        #  like :   ( ('xxx1'),   ('xxx2'), ('xxx3'))
        #  get_res("xxx","xxx2") will get data like:
        #  ( ("xxxx","xxxx"), ("xxxx","xxxx"), ("xxxx","xxxx") )

        self.payloads = [i[0] for i in self.get_res("payload")]   
        self.options['shell'] = '{exp} \"<--|payload|-->\" ' #exam: "egrep -Inr  <--|payload|--> <--|path|-->"

    def run(self, options_and_payload, **kargs):
        sh = self.options['shell']
        return self.shell(sh.format(**options_and_payload), **kargs)
"""
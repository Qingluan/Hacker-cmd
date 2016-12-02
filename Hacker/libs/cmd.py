#!/usr/bin/env python3
import os
import sys
import time
import argparse

from importlib import import_module, util

from qlib.log import LogControl
from termcolor import colored

import Hacker
from Hacker.libs.hackerlib import upload_history
from Hacker.libs.hackerlib import delete_template_in_sqlite_db
from Hacker.libs.hackerlib import create_multi_templates
from Hacker.libs.hackerlib import search_comba_cmds, search_cmd
from Hacker.libs.hackerlib import delete_mode
from Hacker.libs.hackerlib import execute, dinput
from Hacker.libs.hackerlib import str_auto, GeneratorApi
from Hacker.libs.networklib import Linkedin, Google
from Hacker.ini.settings import DB_Handler, DB_PATH
from Hacker.ini.settings import init, MODULES_TEMPLATE
from Hacker.ini.settings import J
from Hacker.ini.settings import SqlEngine, MODULE_PATH

DOC = """
     This is a script to make a new cmd to execute sub cmds , or run Modules.

     # will run Module first , then if no Module found will run cmds_comb
     
     example:  -c to make a cmd 'scan url=xxx' which include  'whois {url}' 'host {url}'
     \n--- write by qingluan

     first: 
        $ --init
        $ -uh

"""
LogControl.LOG_LEVEL = LogControl.INFO 
LogControl.LOG_LEVEL |= LogControl.OK
LogControl.LOG_LEVEL |= LogControl.FAIL
LogControl.LOG_LEVEL |= LogControl.INFO


def CheckModule(name):
    m = util.find_spec("Hacker.modules.%s" % name, "Hackers")
    if m:
        return True
    else:
        return False

def GetModule(name):
    """
    this function to load modules
    """
    LogControl.i("load module ", colored(name, "green"), end='')
    try:
        m = import_module("Hacker.modules.%s" % name)
        if m:
            LogControl.ok()
            return getattr(m, name)
    except ImportError as e:
        LogControl.fail(e)
        return False

def RunModule(name, new_res=None, D=False, help=False):
    """
    this function to ex modules
    @new_res: to add new item , can use str or file_path
    @D: delete mode to rm or list some data in DB.
    @help: can see detail info for this Module.
    """
    m = GetModule(name)
    if m:
        try:
            instance = m()
            sys.argv.pop(1)
            api_args = GeneratorApi(instance)
            # print(api_args.__dict__)
            # sys.argv
            # print(api_args.__dict__)
            # if new_res:
                # add res to Module's DB
                # instance.add_res(new_res)
            # elif D:
            #     instance.del_res()
            # elif set(args) &  set(args):

            #     help_dict = instance.init_args()

            #     doc = help_dict.pop("doc")
            #     LogControl.info(doc)
            #     # print(doc)
            #     for k in help_dict:
            #         LogControl.i("%10s %20s \n\t\t\t%s" % (k, ' ',help_dict[k]))

            # else:
                # to run Module
            LogControl.i("--  init args   --", txt_color='blue', end='')
            rkargs = api_args.__dict__
            instance.init_payload(**rkargs)
            # LogControl.i(instance.options)
            LogControl.i("\r--      run     --", txt_color='blue')
            instance.ex()
        except Exception as e:
            LogControl.err(e)
        finally:
            return True
    else:
        return None


def AddModule(name):
    """
    this function to add a new Module
    """
    # get module's path
    module_path = J(list(util.find_spec("Hacker").submodule_search_locations).pop(), 'modules')
    LogControl.ok(J(module_path, '%s.py' % name), txt_attr=['underline'])
    with open(J(module_path,'%s.py' % name) , "w") as m_fp:
        exp = dinput("if run as shell type , shell cmd\nlike 'egrep -Inr' 'ping -f 10' \n>> ",'')
        res = MODULES_TEMPLATE.format(module_name=name, exp=exp).replace("<--|", "{").replace("|-->", "}")
        m_fp.write(res)
    direction = dinput('which direction this module will be used for ?\n SqlInject? COdeDetect?  Exp? SocialEngine? ... ','UnKnow')
    DB_Handler.insert("modules", ['name', 'direction'], name, direction)
    LogControl.ok("you Can Editor this module by use  Hacker {name} '--editor' options".format(name=name))


def args():
    parser = argparse.ArgumentParser(usage=" how to use this", description=DOC)
    parser.add_argument("--init", default=False, action="store_true", help='init this project .. to create DB.')

    parser.add_argument("-cc","--create-cmdcomb", default=False, action='store_true', help=colored("create a shortcut.", "red", attrs=['underline']))
    parser.add_argument("-D", "--delete", default=False, action='store_true', help="delete some cmds in DB. [interact mode]")
    parser.add_argument("-s","--search", default=None, help="search cmd from history and db.")
    parser.add_argument("-uh","--update-history", default=False, action='store_true', help=colored("search cmd from history and db.", "blue", attrs=['underline']))
    parser.add_argument("-lc","--list-cmdcomb", default=False, action='store_true', help="show combination cmd in DB.")
    # parser.add_argument("-mt","--mail-type", default='126', help="mail type")
    # parser.add_argument('-doc', "--document", default='account', help="set mongo's document , %s " % colored("default: account", "green", attrs=['bold',]))
    # parser.add_argument("--upload", default=False, action='store_true', help="update mongo db to osc")
    
    # parser.add_argument("-d", "--db", default='', help="set mongo's db, %s "% colored("default: local", "green", attrs=['bold']) )
    # parser.add_argument("--args", default='', help="args for options")
    # parser.add_argument("--example", default=False, action="store_true", help="example how to use this")
    # parser.add_argument("-m", "--month", default=time.gmtime(time.time()).tm_mon, help="set search month time, default only can search this month")
    # parser.add_argument("-y", "--year", default=time.gmtime(time.time()).tm_year, help="set search year time")
    
    parser.add_argument("-l", "--linkedin", default=None, help='search people linkedin')
    parser.add_argument("-g", "--google", default=None, help='search people google')
    parser.add_argument("-A", "--args", default=None, help='search args , must used by -g or -l')
    
    parser.add_argument("-S", "--social-database", default=False, action="store_true", help=colored("handle local social database.", "red", attrs=['underline']))
    parser.add_argument("-lm","--list-module", default=False, action='store_true', help="show Modules in DB.")
    parser.add_argument("-um","--update-module", default=False, action='store_true', help="update modules to local.")
    parser.add_argument("-cm","--create-module", default=None, help=colored("create a module python file in PATH/site-packages/Hackers/modules Type: xxxx --Editor can vim it.", "red", attrs=['bold']))
    parser.add_argument("-dm", "--delete-module", default=None, help="delete Module's all db data.")
    parser.add_argument("-dmd", "--delete-module-data", default=None, help="delete Module in py file.")

    parser.add_argument('-st', "--sh", default='zsh', help="set sh's type , default is zsh")
    parser.add_argument("-v","--verbos", default=False, action='store_true', help="more info.")
    parser.add_argument("-V", "--console", default=False, action="store_true", help="if see console's log.")

    return parser.parse_args()




def main():
    if sys.argv[1][0] != '-':
        cmd_args = sys.argv[1:]
        kargs = dict()
        console = False
        for id, arg in enumerate(cmd_args):
            if '=' in arg:
                v = arg.split('=')
                kargs[v[0]] = v[1]
                if v[1].lower() is 'false':
                    kargs[v[0]] = False
                elif v[1].lower() is 'true':
                    kargs[v[0]] = True
            # elif (arg.startswith('-') or arg.startswith('--')):
            #     kargs[arg] = cmd_args


            elif '-h' == arg:
                if not CheckModule(cmd_args[0]):
                    print("Usage: ", cmd_args[0])
                    execute(cmd_args[0], help=True)
                    return False
            elif arg == '-v':
                console = True
        print(cmd_args[0])
        # will run Module first , then if no Module found will run cmds_comb
        if not RunModule(cmd_args[0]):
            LogControl.i("load cmd-comb", colored(cmd_args[0], "green"), end='')
            execute(cmd_args[0], console=True, **kargs)

        
    else:
        ar = args()
        
        if ar.init:
            init()
            sys.exit(0)

        if ar.linkedin:
            l = Linkedin(ar.linkedin)
            l.parse()
            if ar.args:
                for i in l[ar.args]:
                    i.show()
            else:
                l.show()
            sys.exit(0)

        if ar.google:
            l = Google(ar.google)
            # print(l.format())
            l.parse()
            if ar.args:
                for i in l[ar.args]:
                    i.show()
            else:
                l.show()
            sys.exit(0)

        if ar.social_database:
            from Hacker.libs.socialdatalib import Social
            s = Social()
            s.cmdloop()
            sys.exit(0)

        if ar.delete_module_data:
            s = SqlEngine(database=DB_PATH)
            s.delete(ar.delete_module_data)
            sys.exit(0)

        if ar.delete_module:
            m_p = J(MODULE_PATH, ar.delete_module + '.py')
            if os.path.exists(m_p) and os.path.isfile(m_p):
                os.system("rm %s" % m_p)
            s = SqlEngine(database=DB_PATH)
            
            s.delete('modules', name=ar.delete_module)
            if (ar.delete_module,) in s.table_list():
                s.drop_table(ar.delete_module)
            sys.exit(0)

        if ar.create_module:
            AddModule(ar.create_module)
            sys.exit(0)

        if ar.create_cmdcomb:
            create_multi_templates(debug=ar.verbos)
            sys.exit(0)

        if ar.update_history:
            upload_history(ar.sh)
            sys.exit(0)

        if ar.search:
            res = search_cmd(ar.search)
            for k in res:
                LogControl.i(res[k].decode('utf8').strip(), txt_color='green')
            sys.exit(0)

        if ar.delete:
            delete_mode()
            sys.exit(0)

        if ar.list_cmdcomb:
            for k,cm in DB_Handler.select("templates", 'group_key', 'cmd'):
                LogControl.i(k, cm)
            sys.exit(0)

        if ar.list_module:
            for k,cm in DB_Handler.select("modules", 'name', 'direction'):
                LogControl.i(k, cm)
            sys.exit(0)




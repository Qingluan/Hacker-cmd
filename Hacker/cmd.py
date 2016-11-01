#!/usr/bin/env python3
import os
import sys
import time
import argparse

from qlib.log import LogControl
from Hacker.hackerlib import upload_history
from Hacker.hackerlib import rlocal
from Hacker.hackerlib import delete_template_in_sqlite_db
from Hacker.hackerlib import create_multi_templates
from Hacker.hackerlib import search_comba_cmds, search_cmd
from Hacker.hackerlib import delete_mode
from Hacker.hackerlib import execute
from Hacker.settings import DB_Handler

DOC = """
     This is a script to make a new cmd to execute sub cmds 
      example:  -c to make a cmd 'scan url=xxx' which include  'whois {url}' 'host {url}'
     \n--- write by qingluan

"""
LogControl.LOG_LEVEL = LogControl.INFO 
LogControl.LOG_LEVEL |= LogControl.OK



def args():
    parser = argparse.ArgumentParser(usage=" how to use this", description=DOC)
    parser.add_argument("-c","--create", default=False, action='store_true', help="create mode")
    parser.add_argument("-s","--search", default=None, help="search cmd from history and db.")
    parser.add_argument("-uh","--update-history", default=False, action='store_true', help="search cmd from history and db.")
    
    # parser.add_argument("-mt","--mail-type", default='126', help="mail type")
    # parser.add_argument('-doc', "--document", default='account', help="set mongo's document , %s " % colored("default: account", "green", attrs=['bold',]))
    # parser.add_argument("--upload", default=False, action='store_true', help="update mongo db to osc")
    parser.add_argument("-D", "--delete", default=False, action='store_true', help="delete some cmds in DB. [interact mode]")
    # parser.add_argument("-d", "--db", default='', help="set mongo's db, %s "% colored("default: local", "green", attrs=['bold']) )
    # parser.add_argument("--args", default='', help="args for options")
    # parser.add_argument("--example", default=False, action="store_true", help="example how to use this")
    # parser.add_argument("-m", "--month", default=time.gmtime(time.time()).tm_mon, help="set search month time, default only can search this month")
    # parser.add_argument("-y", "--year", default=time.gmtime(time.time()).tm_year, help="set search year time")
    # parser.add_argument("--raw-text", default=False, action="store_true")
    # parser.add_argument("--setting", default=None, help='add setting items: \n@example: Index acc --setting proxy http=socks5://127.0.0.1:1080 https=socks5://127.0.0.1:1080')
    parser.add_argument("-V", "--console", default=False, action="store_true", help="if see console's log.")
    parser.add_argument("-lm","--list-multi", default=False, action='store_true', help="show combination cmd in DB.")
    # parser.add_argument("-uf","--upload-file", default=None, help="upload file to DB.")
    # parser.add_argument("-lf","--pull-file", default=None, help="pull file from DB .")
    parser.add_argument('-st', "--sh", default='zsh', help="set sh's type , default is zsh")
    parser.add_argument("-v","--verbos", default=False, action='store_true', help="more info.")
    return parser.parse_args()




def main():
    if sys.argv[1][0] != '-':
        cmd_args = sys.argv[1:]
        kargs = dict()
        console = False
        for arg in cmd_args:
            if '=' in arg:
                v = arg.split('=')
                kargs[v[0]] = v[1]
            elif '-h' == arg:
                print("Usage: ", cmd_args[0])
                execute(cmd_args[0], help=True)
                return False
            elif arg == '-v':
                console = True
        print(kargs)
        execute(cmd_args[0], console=True, **kargs)
        

        
    else:
        ar = args()
        
        if ar.create:
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

        if ar.list_multi:
            for k,cm in DB_Handler.select("templates", 'group_key', 'cmd'):
                LogControl.i(k, cm)
            sys.exit(0)



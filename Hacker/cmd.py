#!/usr/bin/env python3
import os
import sys
import time
import argparse

from qlib.log import LogControl

DOC = """
     this is script for gen account \n--- write by qingluan
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
    # parser.add_argument("--load", default=False, action='store_true', help="load db from  osc")
    # parser.add_argument("-D", "--db", default='local', help="set mongo's db, %s "% colored("default: local", "green", attrs=['bold']) )
    # parser.add_argument("--args", default='', help="args for options")
    # parser.add_argument("--example", default=False, action="store_true", help="example how to use this")
    # parser.add_argument("-m", "--month", default=time.gmtime(time.time()).tm_mon, help="set search month time, default only can search this month")
    # parser.add_argument("-y", "--year", default=time.gmtime(time.time()).tm_year, help="set search year time")
    # parser.add_argument("--raw-text", default=False, action="store_true")
    # parser.add_argument("--setting", default=None, help='add setting items: \n@example: Index acc --setting proxy http=socks5://127.0.0.1:1080 https=socks5://127.0.0.1:1080')
    # parser.add_argument("-A", "--account", default=False, action="store_true", help="reading account info")
    # parser.add_argument("-sf","--show-file", default=False, action='store_true', help="show files in DB.")
    # parser.add_argument("-uf","--upload-file", default=None, help="upload file to DB.")
    # parser.add_argument("-lf","--pull-file", default=None, help="pull file from DB .")
    return parser.parse_args()




def main():
    if sys.argv[1][0] != '-':
        LogControl.ok("some")
        pass
    else:
        ar = args()
    
        if ar.create:
            pass
            sys.exit(0)

        if ar.update_history:
            pass
            sys.exit(0)

        if ar.search:
            pass
            sys.exit(0)



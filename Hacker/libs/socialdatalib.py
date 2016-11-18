import cmd,time,os

from termcolor import colored
from qlib.data.sql import SqlEngine
from qlib.log import LogControl
from qlib.io.console import dict_cmd
from qlib.io import input_default
from qlib.file import zip_64, unzip_64
from Hacker.ini.settings import RES, J, TEMPLATE_PATH
from Hacker.ini.TEMPLATES import SOCIAL


SOCIAL_DB_PATH =  J(RES, ".social.db")
LogControl.LOG_LEVEL = LogControl.OK

def file_check(dic):
    new_d = {}
    for k in dic:
        if os.path.isfile(dic[k]):
            new_d[k] = zip_64(dic[k])
        else:
            new_d[k] = dic[k]
    return new_d



class Social(cmd.Cmd):
    intro =  colored("Social DB", "red")
    prompt = colored("<Social>", "red")
     
    def __init__(self):
        super().__init__()
        self.db = SqlEngine(database=SOCIAL_DB_PATH)
        for k in SOCIAL:
            if (k,) not in self.db.table_list():
                self.db.create(k, **SOCIAL[k])
        self.social = SOCIAL

    def do_add(self, name):
        m = SOCIAL[name]
        res = dict_cmd(m)
        res = file_check(res)

        self.db.insert(name, list(res.keys()), *res.values())

    def do_change(self, name):
        self.do_search(name)
        tm1 = {
            'title': str,
            'new':str,
            'id': str,
        }

        tm1 = dict_cmd(tm1)
        self.db.update(name, {tm1['title']: tm1['new']}, id=int(tm1['id']))

    def do_setting(self, args):
        for k in SOCIAL:
            LogControl.i(k, txt_color='red')
        m = dict_cmd({"which table":None})
        for k in SOCIAL[m["which table"]]:
            LogControl.i(k, txt_color='red', tag=m["which table"])
        res = dict_cmd({
            'Title': None,
            'Value': None,
        })
        new_cols = {res['Title']: res['Value']}
        self.db.alter(m["which table"], **new_cols)

    def do_clear(self, arg):
        os.system("tput cl")

    def do_vi_setting(self,arg):
        os.system("vim " + TEMPLATE_PATH)

    def do_search(self, name):
        data_tmp = SOCIAL[name]
        tmp = {
            "set search key": str,
        }
        tmp = dict_cmd(tmp)

        keys = dict.fromkeys(tmp['set search key'].split(',') if tmp['set search key'].find(",") != -1 else tmp['set search key'].split() )
        keys = dict_cmd(keys)
        cols = input_default("which interesting?\n %s\n>" % ' '.join([colored(i, attrs=['underline']) for i in data_tmp.keys() ]) )
        cols = cols.split(",") if cols.find(",") != -1 else cols.split()
        res = self.db.search(name, *cols, **keys)
        for i in res:

            v = dict(zip(cols, i))
            for k in v:
                print("\t", end='')
                LogControl.i(v[k], tag=k, txt_color='yellow')
        

    def do_quit(self, some):
        return True



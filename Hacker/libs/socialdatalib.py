import cmd,time,os

from termcolor import colored
from qlib.data.sql import SqlEngine
from qlib.log import LogControl
from qlib.io.console import dict_cmd
from qlib.io import input_default
from qlib.file import file264, b642file
from qlib.file.pdf import output_to_pdf
from Hacker.ini.settings import RES, J, TEMPLATE_PATH
from Hacker.ini.TEMPLATES import SOCIAL


SOCIAL_DB_PATH =  J(RES, ".social.db")
LogControl.LOG_LEVEL = LogControl.OK

def file_check(dic):
    new_d = {}
    for k in dic:
        if os.path.isfile(dic[k]):
            new_d[k] = '[*b64*][' + dic[k] + ']' + file264(dic[k])
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
        if 'all' in cols:
            cols = ' '.join(list(data_tmp.keys()))
        cols = cols.split(",") if cols.find(",") != -1 else cols.split()
        res = self.db.search(name, *cols, **keys)
        for i in res:

            v = dict(zip(cols, i))
            for k in v:
                print("\t", end='')
                v[k] = v[k][:90] + '...' if len(v[k]) > 90 else v[k]
                LogControl.i(v[k], tag=k, txt_color='yellow')

    def do_list(self, name):
        data_tmp = SOCIAL[name]
        cols = list(data_tmp.keys())
        res = self.db.search(name, *cols)

        for i in res:
            v = dict(zip(cols, i))
            for k in v:
                print("\t", end='')
                v[k] = v[k][:90] + '...' if len(v[k]) > 90 else v[k]
                LogControl.i(v[k], tag=k, txt_color='yellow')
            print( "---------------------")


    def export(self, name):
        tmp = SOCIAL[name]
        keys = list(tmp.keys())
        data = self.db.select(name, *keys)
        for item in data:
            for i,v in enumerate(item):
                if v.startswith('[*b64*]'):
                    v = b642file(v[7:])
                    r = v.find("]") + 1
                    v_name = v[1: r-1]
                    v = v[r:]
                str_tmp = "%s:  %s" % (keys[i] , v)
                yield str_tmp
            yield "--------------------------------------------------------"

    def do_export(self, name):
        data = self.export(name)

        output = dict_cmd({'output[path to save]': "./pdf.pdf"})
        fpath = output['output[path to save]']
        LogControl.title('to',output_to_pdf(data, fpath))
        

    def do_quit(self, some):
        return True



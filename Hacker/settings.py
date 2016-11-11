from qlib.data.sql import SqlEngine
from qlib.data import GotRedis
import os, sys

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

try:
    os.makedirs(OUTPUT_DIR)
except FileExistsError:
    pass


def init():
    if 'templates' not in [ i[0] for i in DB_Handler.table_list()]:
        DB_Handler.create('templates', cmd=str, keys='target', goup_key='comba', output='default.log')


MODULES_TEMPLATE = """
from Hacker.hackerlib import Module


class {module_name}(Module):

    def init_args(self):
        return <--|
            "path": "set a root path to detect code.",
        |-->

    def init_payload(self, **kargs):
        \"\"\"
        \"\"\"
        self.options.update(kargs)
        self.payloads = self.get_res("payload")
        self.options['shell'] = '{exp} \"<--|payload|-->\" ' #exam: "egrep -Inr  <--|payload|--> <--|path|-->"

    def run(self, options_and_payload, **kargs):
        sh = self.options['shell']
        return self.shell(sh.format(**options_and_payload), **kargs)
"""
from qlib.data.sql import SqlEngine
import os, sys

# some shortcut . let it easy.
J = os.path.join 
ENV = os.getenv


DB_PATH = J(ENV('HOME'), '.hacker_cmds')

DB_Handler = SqlEngine(database=DB_PATH)

if 'templates' not in [ i[0] for i in DB_Handler.table_list()]:
    DB_Handler.create('templates', cmd=str, keys='target', goup_key='comba', output='default.log')

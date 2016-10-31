from fabric.api import local, output, parallel
from qlib.log import LogControl
from qlib.data import GotRedis

from Hacker.settings import DB_Handler
from termcolor import colored
import os, sys

# some shortcut . let it easy.
J = os.path.join 
ENV = os.getenv

# setting log
LogControl.LOG_LEVEL = LogControl.INFO
LogControl.LOG_LEVEL |= LogControl.OK


DOC = """

    The cmd will save in redis db.
    data from ~/.{bash/zsh}_history.
    use a hash format. 
        got by redis.hget(group, key)
        set by redis.hset(group, key, val)
        list by redis.key()
        list detail in group by redis.key(group)

        data format like :     {
                            'sqlmap': {
                                '1' : 'sqlmap -u http://xx.xxx.x.xxx --dbs',
                                '2' : 'sqlmap -u http://xxx.xxx.xxx --dbms mysql --dbs',
                                ...
                            }
                        }

"""



@parallel
def rlocal(cmd, **options):
    """
    @cmd run in local shell
    @**options include:
        shell=False,
        captures=False,

    """
    return local(cmd, **options)


def upload_history(sh='zsh', debug=False):
    """
    find cmd in sh's history

    @sh='zsh' / can choose bash
    """
    redis = GotRedis()
    history_file = J(ENV("HOME"), '.%s_history' % sh)
    keys_dict = dict()
    with open(history_file, 'rb') as fp:
        for line in fp:

            
            # filter some unused cmd
            try:
                # remove prompt and decode as utf-8
                cmd_str = line.decode('utf8').split(";")[1]

                args = cmd_str.split()

                # count cmd
                cmd_title = args[0]
                if cmd_title not in keys_dict:
                    keys_dict.setdefault(cmd_title, 1)
                else:
                    keys_dict[cmd_title] += 1
                
                ID = keys_dict[cmd_title]
                
                if len(cmd_title) > 20:
                    continue
                if cmd_title.find("/") != -1:
                    continue
            except IndexError as e:
                LogControl.err(e, '\n', '\t', line) if debug else ''
                continue
            except UnicodeDecodeError as e:
                continue


            redis(cmd_title, ID, cmd_str)
            LogControl.ok(cmd_title, end='\r')
            sys.stdout.flush()
    redis.redis.save()


def list_cmd_titles():
    """
    list all cmd keys in redis.
    """
    redis = GotRedis()
    return redis.keys()


def list_cmd():
    """
    list all load in redis's cmd
    """
    redis = GotRedis()
    cmd_groups = redis.keys()
    for group in cmd_groups:
        LogControl.info(group, '\n\t', redis.redis.hgetall(group))


def choose_a_cmd_as_template(cmd_name, id_key):
    """
    return a set of cmd in redis's DB.
    """
    redis = GotRedis()
    return redis.redis.hget(cmd_name, id_key)


class CmdMakeException(Exception):
    pass



def save_template_to_sqlite_db(group_key ,cmd_str, debug=False, **args_map):
    """
    example: 
        @cmd_str:  'ls  some | grep some'
        @args_map: { 'dir':   1} 

        will make a  : 'ls {dir} | grep some' str to save to db. 
            then will save  data: 
            {
                cmd : 'ls {dir} | grep some' ,
                keys: 'dir'
            }
    """
    # check
    cmd_str = cmd_str.decode('utf-8')
    cmd_args = cmd_str.split()
    for arg in args_map:
        # if cmd_str.find(arg) == -1:
        #     LogControl.err("No such args can be replace")
        #     raise CmdMakeException("No arg %s can be replace in %s" %(arg, cmd_str))
        try:
            cmd_args[args_map[arg]] = '{%s}' % arg
        except IndexError as e:
            LogControl.err("No such args can be replace")
            raise CmdMakeException("No arg %s can be replace in %s" %(arg, cmd_str))
            return False

    replaced_cmd = ' '.join(cmd_args)
    keys = ' '.join(list(args_map.keys()))
    LogControl.info(replaced_cmd, keys, txt_color='white') if debug else ''
    DB_Handler.insert('templates', ['group_key', 'cmd', 'keys', 'output'], group_key, replaced_cmd, keys, '%s.log' % cmd_args[0])
    return True


def dinput(string, default=None):
    m = input(string)
    if m: 
        return m
    else:
        return default


def search_cmd(*keys):
    redis = GotRedis()
    cmd = keys[0]
    if_options = False
    if len(keys) > 1:
        if_options = True

    result = {}
    for title in redis.keys():
        title = title.decode('utf8')
        if title.find(cmd) != -1:
            if not if_options:
                return redis.redis.hgetall(cmd)
            else:
                for exe_str in redis.redis.hgetall(title):
                    # exe_str = exe_str.decode('utf8')
                    for k in keys[1:]:
                        tmp_r = redis.redis.hget(title, exe_str).decode('utf8')
                        if tmp_r.find(k) != -1:
                            if title not in result:
                                result[title] = [tmp_r]
                            else:
                                result[title] += [tmp_r]
    return result





def create_cmd():
    redis = GotRedis()
    while 1:
        cmd_group_name = dinput("cmd group's name?\n[q: exit]>", default='q')
        if cmd_group_name == 'q':
            break
        while 1:
            cmd_t = dinput('which cmd?\n[q :exit]>', default='q').split()
            if cmd_t[0] == 'q':
                break
            # print(cmd_t)
            vals = list(search_cmd(*cmd_t).values())
            for i, v in enumerate(vals):
                LogControl.ok(i, v, txt_color='cyan')
            cmd_d = vals[int(dinput('choose a ID , (deafult 0)', default=0))]
            kv = dinput('\n%s\n[default 1=url] set :' % cmd_d, default='1=url').split()

            # cmd_args = cmd_d.decode('utf8').split()
            # cmd_args[k] = colored(cmd_args[k], attrs=['underline'])
            # v = dinput('%s | %d=' % (' '.join(cmd_args), k))
            print(cmd_d, kv)





    
    


    

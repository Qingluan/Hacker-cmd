import os, sys, time

from fabric.api import local, output, parallel
from qlib.log import LogControl
from qlib.data.sql import SqlEngine
from Hacker.settings import DB_Handler, redis, DB_PATH, OUTPUT_DIR
from termcolor import colored


# some shortcut . let it easy.
J = os.path.join 
ENV = os.getenv

# setting log
LogControl.LOG_LEVEL = LogControl.INFO
LogControl.LOG_LEVEL |= LogControl.OK
LogControl.LOG_LEVEL |= LogControl.FAIL
output.running = False


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
def rlocal(cmd, dir, output, **options):
    """
    @cmd run in local shell
    @**options include:
        shell=False,
        captures=False,

    """
    return local(cmd + ' 1> %s/%s  2> %s/error.log'  % (dir, output, dir), **options)

def rrun(cmd, dir, output, **options):
    cmd_str = cmd + ' 1> %s/%s  2> %s/error.log'  % (dir, output, dir)
    LogControl.i(cmd_str)
    return os.popen(cmd_str, **options)


def upload_history(sh='zsh', debug=False):
    """
    find cmd in sh's history

    @sh='zsh' / can choose bash
    """

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
            LogControl.i(cmd_title, end='\r')
            sys.stdout.flush()
    redis.redis.save()


def list_cmd_titles():
    """
    list all cmd keys in redis.
    """
    return redis.keys()


def list_cmd():
    """
    list all load in redis's cmd
    """
    cmd_groups = redis.keys()
    for group in cmd_groups:
        LogControl.info(group, '\n\t', redis.redis.hgetall(group))


def choose_a_cmd_as_template(cmd_name, id_key):
    """
    return a set of cmd in redis's DB.
    """
    return redis.redis.hget(cmd_name, id_key)


class CmdMakeException(Exception):
    pass


def create_single_template(cmd_str, debug=False, **args_map):
    """
    create single-cmd templates
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
    cmd_str = cmd_str.decode('utf-8') if isinstance(cmd_str, bytes) else cmd_str
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
    return replaced_cmd, keys, '%s.log' % cmd_args[0]


def save_template_to_sqlite_db(group_key, cmd_str, keys, output):
    
    """
    save value to db which from create_template
    """
    DB_Handler.insert('templates', ['group_key', 'cmd', 'keys', 'output'], group_key, cmd_str, keys, output)
    return True


def delete_template_in_sqlite_db(group_key):
    DB_Handler.delete('templates', group_key=group_key)
    return True


def dinput(string, default=None):
    """
    default input
    """
    m = input(string)
    if m: 
        return m
    else:
        return default


def search_cmd(*keys):
    """
    search cmd in redis.
    """

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





def create_multi_templates(debug=False):
    """
    create a multi-cmd template.
    """
    cmd_group_name = dinput("cmd group's name?\n[q: exit]>", default='q')
    if cmd_group_name == 'q':
        return False
    while 1:
        cmd_t = dinput('which cmd?\n[q :exit]>', default='q').split()
        if cmd_t[0] == 'q':
            break
        # print(cmd_t)
        vals = list(search_cmd(*cmd_t).values())
        if len(vals) == 0:
            continue

        if isinstance(vals[0], list) :
            vals = [i.strip() for i in vals[0]]

        if not vals:
            continue
        for i, v in enumerate(vals):
            LogControl.ok(i, v, txt_color='cyan')
        cmd_d = vals[int(dinput('choose a ID , (deafult 0)', default=0))]

        k_in = 2
        while 1:
            k_in = dinput('\n%s\nchoose parts to replace ,separate by ' ' [default 2] set :' % colored(cmd_d, attrs=['bold']), default='1')
            k = [int(i) for i in k_in.split()]
            cmd_args = cmd_d.decode('utf8').split() if isinstance(cmd_d, bytes) else cmd_d.split()
            mvals = {}
            for kv in k:
                cmd_args[kv] = colored(cmd_args[kv], attrs=['underline'])
                v = dinput('%s |[-r: reset parts, default: -r] %d=' % (' '.join(cmd_args), kv), default='-r')
                if v == '-r':
                    LogControl.fail("reset")
                    continue
                mvals[v] = kv
                st, key, out = create_single_template(cmd_d, debug=debug, **mvals)
                save_template_to_sqlite_db(cmd_group_name, st, key, out)
            break



def search_comba_cmds(tag=False):
    """
    list multi-templates.
    """
    DB_Handler = SqlEngine(database=DB_PATH)
    for key in DB_Handler.select('templates', 'group_key'):
        if not tag:
            yield key[0], list(DB_Handler.select('templates', group_key=key[0]))
        else:
            if key[0].find(tag) != -1:
                yield key[0], list(DB_Handler.select('templates', group_key=key[0]))
    
    
def delete_mode():
    """
    delete some cmds.
    """
    while 1:
        c = dinput("[l:list all comba-cmds, q:exit, s:search cmd, d xxx :delete xxx comba cmd] \n>", default='q')
        if c == 'q':
            LogControl.i('~ by')
            break
        elif c == 'l':
            for m,res in search_comba_cmds():
                LogControl.i(m, res)
        else:
            if c[0] == 's':
                cc = ''
                try:
                    cc = c.split()[1]
                except Exception as e:
                    LogControl.err(e)
                    continue
                for m,res in search_comba_cmds(cc):
                    LogControl.i(m, res)

            elif c[0] == 'd':
                cc = ''
                try:
                    cc = c.split()[1]
                except Exception as e:
                    LogControl.err(e)
                    continue

                delete_template_in_sqlite_db(cc)
                LogControl.ok("delete it.")
            else:
                continue

def dir_gen():
    return J(OUTPUT_DIR, time.asctime()[:11].replace(' ', '_'))


def execute(cmd, help=False, console=False, **args):
    t_dir = dir_gen()
    try:
        os.makedirs(t_dir)
    except Exception as e:
        pass
    DB_Handler = SqlEngine(database=DB_PATH)
    cmds = []
    options = set()
    for i in DB_Handler.select("templates", 'cmd', 'keys', 'output', group_key=cmd):
        cmds.append([i[0], i[2]])
        [ options.add(m) for m in i[1].split()]
    
    if help:
        LogControl.i("need to set options: ", options)
        for cmd, out in cmds:
            LogControl.i(cmd, ' -> ', out, txt_color='yellow')
        return True

    else:
        for cmd, out in cmds:
            try:
                rrun(cmd.format(**args), t_dir, out)
            except Exception as e:
                LogControl.err(e,cmd)
                LogControl.i("need to set options: ", options)
                continue

        if console:
            local('sleep 2 && tail -f %s/*' % t_dir)
            
    

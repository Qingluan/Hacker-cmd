import os
from Hacker.libs.hackerlib import Module,J
from Hacker.libs.hackerlib import LogControl, colored
from Hacker.ini.settings import RES
from urllib.parse import urljoin

import requests
LogControl.LOG_LEVEL = LogControl.OK
LogControl.LOG_LEVEL |= LogControl.WRN
LogControl.LOG_LEVEL |= LogControl.FAIL


class U(Module):
    """
info:
    asynchrouns function : Asyn( func , *args, **kargs)
        the result will pass to function: done(*args)

    network function: GET (url, **kargs), 
                      POST(url, **data)

    """

    def init_args(self):
        """
        this function will generate a api.
            will use 'parser.add_argument()'
            examp: {
                'url' :  "set a target url"
                    ...
            }
            the 'url' will be parse to :
                parser.add_argument("--url", default=None, help="set a target url")
            ...
            
            examp:
            if key's all case is upcase. will gen a positional arg.
            {
                'URL': 'set a target url',
                ...
            }
            -->
                parser.add_argument("url", default=None, help="set a target url")

            examp: 
            if key startswith upcase. will be follow
            {
                'Url' :  "set a target url"
                    ...
            }
             -->
                parser.add_argument("-u", "--Url", default=None, help="set a target url")

            examp: 
            if value is boolean.
            {
                'ed' :  (False,  "end some ?")
                    ...
            }
            

            --> 
                parser.add_argument("--ed", default=False, help="end some?")
        """
        return {
            "doc": self.__doc__.format(name=colored(self.module_name, "green", attrs=['bold','underline'])),
            "Url": "set a target url",
            'Type': "set type to check , [php, asp, aspx, cgi, dir , mdb]",
        }

    def done(self, code, url):
        # print(code)
        if round(code / 200) == 1:
            LogControl.ok(code, url, txt_color='green')
        elif round(code/ 300) == 1:
            LogControl.wrn(code, colored(url, 'yellow', attrs=['underline']))
        elif round(code/ 400) == 1:
            LogControl.err(code, colored(url, 'red', attrs=['underline', 'bold']))
        else:
            LogControl.err(code, url)

    def parser(self):
        """
        options how to run.
        """
        if 'Url' in self.options:
            self.options['u'] = self.options['Url']

    def load_res(self, name):
        for f in  os.listdir(self.RES_DIR):
            if f.lower().find(name) != -1:
                LogControl.title("load file", f)
                return J(self.RES_DIR, f)
        

    def test_url(self, url):
        try:
            res = self.GET(url)
        except ConnectionRefusedError as e:
            return -1, url
        except requests.exceptions.InvalidURL as e:
            return -1, url
        return res.status_code, url

    def init_payload(self, **kargs):
        """
        """

        self.options.update(kargs)
        # self.options['thread'] = self.options['t']
        # files = [ self.load_res(i[0]) for i in self.get_res("payload", type=self.options['Type'])]

        urls = []
        files = [self.load_res(name) for name in self.options['Type'].split(",")]
        for file in files:
            with open(file, 'rb') as fp:
                for line in fp:
                    urls.append(line.decode("utf8","ignore").strip())
        self.payloads = urls


        # self.options['shell'] = ' "{payload}" ' #exam: "egrep -Inr  {payload} {path}"

    def run(self, options_and_payload, **kargs):
        # sh = self.options['shell']
        # return self.shell(sh.format(**options_and_payload), **kargs)
        p = options_and_payload['payload']
        p = p[1:] if p[0] == '/' else p
        url = J(self.options['u'], p)
        # LogControl.i('\n',url)
        self.Asyn(self.test_url, url)

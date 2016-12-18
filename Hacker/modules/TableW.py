import pandas
from Hacker.libs.hackerlib import Module
from Hacker.libs.hackerlib import LogControl as L
from Hacker.libs.hackerlib import colored
from Hacker.libs.networklib import Analyze
L.LOG_LEVEL = L.OK
L.LOG_LEVEL |= L.WRN
L.LOG_LEVEL |= L.FAIL



class TableW(Module):
    """
    {name}
    Scrap a web's info , like ,link/table/forms
    """

    def init_args(self):
        return {
            "doc": self.__doc__.format(name=colored(self.module_name, "green", attrs=['bold','underline'])),
            "Url": "target to scrab",
            "Save": "save or not",
            "Type": "csv/ dict",
            "Proxy": "set proxy like 'socks5://127.0.0.1:1080'",
            "Index": "see the columns like 'xxx,xxx,xx' ",
            "Local": "load from local file",
        }

    def parser(self):
        """
        options how to run.
        """
        pass

    def init_payload(self, **kargs):
        """
        """
        self.options.update(kargs)
        if not self.options.get("Type"):
            self.options["Type"] = "dict"
        # self.payloads = kargs["URLS"]
        # self.options['shell'] = "egrep -Inr \"{payload}\" {path}"

    def run(self, options_and_payload, **kargs):
        # L.i(options_and_payload)
        # sh = self.options['shell']
        # return self.shell(sh.format(**options_and_payload), **kargs)
        L.i("run in ", options_and_payload["thread"])
        if options_and_payload.get('Local'):
            t = pandas.DataFrame.from_csv(options_and_payload.get('Local'))
        else:
            z = Analyze(options_and_payload['Url'], proxy=options_and_payload["Proxy"])

            t = z.table(options_and_payload['Type'])

        if options_and_payload.get("Save"):
            if isinstance(t, pandas.DataFrame):
                t.to_csv(options_and_payload['Save'])
                # z.save(options_and_payload['Save'])
            else:
                z.save(options_and_payload['Save'])
        
        if options_and_payload.get("Index"):
            i = options_and_payload.get("Index").split(",")
            L.i(t[i])
        else:
            L.i(t)

        # L.ok("key:", t.head)


        
from Hacker.libs.hackerlib import Module
from Hacker.libs.hackerlib import LogControl, colored

LogControl.LOG_LEVEL = LogControl.OK
LogControl.LOG_LEVEL |= LogControl.WRN
LogControl.LOG_LEVEL |= LogControl.FAIL



class Code(Module):
    """
    {name}
    Code Detect by regex. use shell 'egrep -Inr <payload> <path>'
    """

    def init_args(self):
        return {
            "doc": self.__doc__.format(name=colored(self.module_name, "green", attrs=['bold','underline'])),
            "PATH": "set a root path to detect code.",
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
        self.payloads = [i[0] for i in self.get_res("payload")]
        self.options['shell'] = "egrep -Inr \"{payload}\" {path}"

    def run(self, options_and_payload, **kargs):
        sh = self.options['shell']
        return self.shell(sh.format(**options_and_payload), **kargs)
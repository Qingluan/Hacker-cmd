from Hacker.hackerlib import Module


class CodeDetect(Module):

    def init_args(self):
        return {
            "path": "set a root path to detect code.",
        }

    def init_payload(self, **kargs):
        """
        """
        self.options.update(kargs)
        self.payloads = [i[0] for i in self.get_res("payload")]
        self.options['shell'] = "egrep -Inr \"{payload}\" {path}"

    def run(self, options_and_payload, **kargs):
        sh = self.options['shell']
        return self.shell(sh.format(**options_and_payload), **kargs)
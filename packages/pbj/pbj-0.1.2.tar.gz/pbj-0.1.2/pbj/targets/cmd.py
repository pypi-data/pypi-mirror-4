from target import Target
from reg import register

from subprocess import Popen, PIPE
import os

def cmd(*command, **kw):
    out, err = Popen(command, shell=kw.get('shell', False),
            cwd=kw.get('cwd', None), stdin=PIPE, stdout=PIPE,
            stderr=PIPE, close_fds=True).communicate()
    # print out, err
    return out, err

@register('cmd', required=2)
class CmdTarget(Target):
    def __init__(self, name, command, shell=False, echo=True, cwd=None, **kwargs):
        Target.__init__(self, name, **kwargs)
        self.command = command
        self.cwd = cwd
        self.echo = echo
        self.shell = shell

    def __call__(self, function):
        raise Exception('CmdTarget is not a function wrapper')

    def run(self):
        if self.echo:
            print ' '.join(self.command)
        o, e = cmd(*self.command, shell=self.shell, cwd=self.cwd)
        self.has_run = True
        self.return_value = o
        if o:
            print o,
        if e:
            raise Exception(e)

# vim: et sw=4 sts=4

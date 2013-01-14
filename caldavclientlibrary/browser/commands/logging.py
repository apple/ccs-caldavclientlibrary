##
# Copyright (c) 2007-2013 Apple Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##

from caldavclientlibrary.browser.command import Command
from caldavclientlibrary.browser.command import WrongOptions
import getopt
import shlex

class Cmd(Command):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("logging",)


    def execute(self, cmdname, options):
        opts, args = getopt.getopt(shlex.split(options), '')
        if len(opts) or len(args) > 1:
            print self.usage(cmdname)
            raise WrongOptions()
        if args and args[0] not in ("on", "off",):
            print self.usage(cmdname)
            raise WrongOptions()

        if args:
            state = args[0]
        else:
            state = ("off" if self.shell.account.session.loghttp else "on")
        if state == "on":
            self.shell.account.session.loghttp = True
            print "HTTP logging turned on"
        else:
            self.shell.account.session.loghttp = False
            print "HTTP logging turned off"
        return True


    def usage(self, name):
        return """Usage: %s [on|off]
on  - turn HTTP protocol logging on
off - turn HTTP protocol logging off
without either argument - toggle the state of logging
""" % (name,)


    def helpDescription(self):
        return "Changes the current state of HTTP logging."

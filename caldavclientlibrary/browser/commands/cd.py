##
# Copyright (c) 2007-2010 Apple Inc. All rights reserved.
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
import os
import getopt
import shlex

class Cmd(Command):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("cd",)


    def execute(self, name, options):
        opts, args = getopt.getopt(shlex.split(options), '')
        if len(opts) or len(args) != 1:
            print self.usage(name)
            raise WrongOptions()

        newpath = args[0]
        oldpath = self.shell.wd
        result = True

        if newpath == "..":
            result = self.shell.setWD(os.path.dirname(oldpath))
        elif newpath == ".":
            pass
        elif newpath.startswith("/"):
            result = self.shell.setWD(newpath)
        else:
            result = self.shell.setWD(os.path.normpath(os.path.join(oldpath, newpath)))

        if not result:
            print "%s: %s No such directory" % (name, options,)

        return result


    def complete(self, text):
        return self.shell.wdcomplete(text)


    def usage(self, name):
        return """Usage: %s PATH
PATH is a relative or absolute path.
""" % (name,)


    def helpDescription(self):
        return "Change working directory."

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
from caldavclientlibrary.protocol.url import URL
import os
import getopt
import shlex

class Cmd(Command):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("cat", "more",)
        self.do_wd_complete = True


    def execute(self, cmdname, options):
        opts, args = getopt.getopt(shlex.split(options), '')
        if len(opts) or len(args) != 1:
            print self.usage(cmdname)
            raise WrongOptions()

        path = args[0]

        if not path.startswith("/"):
            path = os.path.join(self.shell.wd, path)
        resource = URL(url=path)

        result = self.shell.account.session.readData(resource)
        if result:
            data, _ignore_etag = result
            print data

        return True


    def usage(self, name):
        return """Usage: %s PATH
PATH is a relative or absolute path.
""" % (name,)


    def helpDescription(self):
        return "Display contents of a file or directory."

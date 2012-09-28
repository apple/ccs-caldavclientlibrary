##
# Copyright (c) 2007-2011 Apple Inc. All rights reserved.
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


    def execute(self, name, options):
        opts, args = getopt.getopt(shlex.split(options), '')
        if len(opts) or len(args) != 1:
            print self.usage(name)
            raise WrongOptions()

        path = args[0]

        if not path.startswith("/"):
            path = os.path.join(self.shell.wd, path)
        resource = URL(url=path)

        data, _ignore_etag = self.shell.account.session.readData(resource)
        print data

        return True


    def complete(self, text):
        return self.shell.wdcomplete(text)


    def usage(self, name):
        return """Usage: %s PATH
PATH is a relative or absolute path.
""" % (name,)


    def helpDescription(self):
        return "Display contents of a file or directory."

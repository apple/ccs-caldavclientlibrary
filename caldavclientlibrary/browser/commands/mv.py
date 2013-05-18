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
import getopt
import os
import readline
import shlex

class Cmd(Command):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("mv", "move",)
        self.do_wd_complete = True


    def execute(self, cmdname, options):

        opts, args = getopt.getopt(shlex.split(options), 'n')

        doURLDecode = False
        for name, _ignore_value in opts:

            if name == "-n":
                doURLDecode = True
            else:
                print "Unknown option: %s" % (name,)
                print self.usage(cmdname)
                raise WrongOptions

        if len(args) != 2:
            print "Wrong number of arguments: %d" % (len(args),)
            print self.usage(cmdname)
            raise WrongOptions

        while True:
            result = raw_input("Really move resource '%s' to '%s' [y/n]: " % (args[0], args[1],))
            if readline.get_current_history_length():
                readline.remove_history_item(readline.get_current_history_length() - 1)
            if not result:
                continue
            if result[0] == "n":
                return True
            elif result[0] == "y":
                break

        fromResource = args[0]
        if not fromResource.startswith("/"):
            fromResource = os.path.join(self.shell.wd, fromResource)
        toResource = args[1]
        if not toResource.startswith("/"):
            toResource = os.path.join(self.shell.wd, toResource)

        resourceFrom = URL(url=fromResource, decode=doURLDecode)
        resourceTo = URL(url=self.shell.server + toResource, decode=doURLDecode)
        self.shell.account.session.moveResource(resourceFrom, resourceTo)

        return True


    def usage(self, name):
        return """Usage: %s PATH PATH
PATH is a relative or absolute path.

""" % (name,)


    def helpDescription(self):
        return "Moves a resource."

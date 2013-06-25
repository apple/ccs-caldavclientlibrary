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

synctokens = [{}, {}]

class Cmd(Command):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("sync",)
        self.do_wd_complete = True


    def execute(self, cmdname, options):

        force = False
        infinite = False
        synctoken = None

        opts, args = getopt.getopt(shlex.split(options), 'fit:')

        for name, value in opts:

            if name == "-f":
                force = True
            elif name == "-i":
                infinite = True
            elif name == "-t":
                synctoken = value
            else:
                print "Unknown option: %s" % (name,)
                print self.usage(cmdname)
                raise WrongOptions

        if len(args) > 1:
            print "Wrong number of arguments: %d" % (len(args),)
            print self.usage(cmdname)
            raise WrongOptions
        elif args:
            path = args[0]
            if not path.startswith("/"):
                path = os.path.join(self.shell.wd, path)
        else:
            path = self.shell.wd
        if not path.endswith("/"):
            path += "/"
        resource = URL(url=path)
        if synctoken is None:
            synctoken = synctokens[0 if infinite else 1].get(path, "") if not force else ""
        newsyctoken, changed, removed, other = self.shell.account.session.syncCollection(resource, synctoken, infinite=infinite)
        synctokens[0 if infinite else 1][path] = newsyctoken

        for item in changed:
            print "Changed: %s" % (item,)
        for item in removed:
            print "Removed: %s" % (item,)
        for item in other:
            print "Error: %s" % (item,)
        if newsyctoken:
            print "Current token: %s" % (newsyctoken,)
        print ""

        return True


    def usage(self, name):
        return """Usage: %s [OPTIONS] [PATH]
PATH is a relative or absolute path.

Options:
-f       force full sync
-i       depth:infinite [DEFAULT depth:1]
-t TEXT  the token to use
""" % (name,)


    def helpDescription(self):
        return "Sync the contents of a directory."

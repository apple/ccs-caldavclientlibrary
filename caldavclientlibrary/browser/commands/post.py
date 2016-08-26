##
# Copyright (c) 2007-2016 Apple Inc. All rights reserved.
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
        self.cmds = ("post",)
        self.do_wd_complete = True

    def execute(self, cmdname, options):

        fname = None
        content_type = "text/plain"
        path = None
        data = None

        opts, args = getopt.getopt(shlex.split(options), 'd:f:t:')

        for name, value in opts:

            if name == "-d":
                data = value
            elif name == "-f":
                fname = value
            elif name == "-t":
                content_type = value
            else:
                print "Unknown option: %s" % (name,)
                print self.usage(cmdname)
                raise WrongOptions

        if data and fname:
            print "Only one of -d or -f is allowed"
            print self.usage(cmdname)
            raise WrongOptions
        elif len(args) > 1:
            print "Wrong number of arguments: %d" % (len(args),)
            print self.usage(cmdname)
            raise WrongOptions
        elif args:
            path = args[0]
            if not path.startswith("/"):
                path = os.path.join(self.shell.wd, path)
        else:
            print "Path to POST must be provided"
            print self.usage(cmdname)
            raise WrongOptions

        # Read in data
        if fname:
            fname = os.path.expanduser(fname)
            try:
                with open(fname, "r") as f:
                    data = f.read()
            except IOError:
                print "Unable to read data from file: %s" % (fname,)
                print self.usage(cmdname)
                raise WrongOptions

        resource = URL(url=path)
        self.shell.account.session.writeData(resource, data, content_type, method="POST")

        return True

    def usage(self, name):
        return """Usage: %s OPTIONS PATH
PATH is a relative or absolute path.

Options:
-f   file name of data to put [OPTIONAL]
-d   string containing data to send [OPTIONAL]
-t   content-type of data being put [DEFAULT: text/plain]

Notes:
Only one of -f or -d is allowed.
""" % (name,)

    def helpDescription(self):
        return "Post data to a resource on the server."

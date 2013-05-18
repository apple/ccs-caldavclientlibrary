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
from caldavclientlibrary.browser import utils
import os
import getopt
import shlex

class Cmd(Command):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("props",)
        self.do_wd_complete = True


    def execute(self, cmdname, options):

        names = False
        all_props = False
        xmllist = False
        prop = None
        path = None

        opts, args = getopt.getopt(shlex.split(options), 'alnp:')

        for name, value in opts:

            if name == "-a":
                all_props = True
            elif name == "-l":
                xmllist = True
            elif name == "-n":
                names = True
            elif name == "-p":
                prop = value
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

        if names:
            results = self.shell.account.session.getPropertyNames(resource)
            print "    Properties: %s" % (utils.printList(results),)
        else:
            if all_props:
                props = None
            elif prop:
                props = (prop,)
            else:
                props = self.shell.account.session.getPropertyNames(resource)
            results, bad = self.shell.account.session.getProperties(resource, props, xmllist)
            print "OK Properties:"
            utils.printProperties(results)
            if bad:
                print "Failed Properties:"
                utils.printProperties(bad)

        return True


    def usage(self, name):
        return """Usage: %s [OPTIONS] [PATH]
PATH is a relative or absolute path.

Options:
-n    list property names only
-a    list all properties via allprop
-l    list actual property XML values
-p    list a specific property using the format "{NS}name"
    if neither -n nor -a are set then property names are first listed, and then values of those looked up.
    only one of -n and -a can be set.
""" % (name,)


    def helpDescription(self):
        return "List the properties of a directory or file."

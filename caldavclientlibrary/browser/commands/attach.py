# #
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
# #

from caldavclientlibrary.browser.command import Command
from caldavclientlibrary.browser.command import WrongOptions
from caldavclientlibrary.protocol.url import URL
import os
import getopt
import shlex

class Cmd(Command):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("attach",)
        self.do_wd_complete = True


    def execute(self, cmdname, options):

        fname = None
        content_type = "text/plain"
        adding = False
        updating = None
        removing = None
        return_representation = False
        path = None

        opts, args = getopt.getopt(shlex.split(options), 'f:t:au:r:x')

        for name, value in opts:

            if name == "-f":
                fname = value
            elif name == "-t":
                content_type = value
            elif name == "-a":
                if updating is not None or removing is not None:
                    print "Only one of -a, -u or -r can be specified"
                    print self.usage(cmdname)
                    raise WrongOptions
                adding = True
            elif name == "-u":
                if adding or removing is not None:
                    print "Only one of -a, -u or -r can be specified"
                    print self.usage(cmdname)
                    raise WrongOptions
                updating = value
            elif name == "-r":
                if adding or updating is not None:
                    print "Only one of -a, -u or -r can be specified"
                    print self.usage(cmdname)
                    raise WrongOptions
                removing = value
            elif name == "-x":
                return_representation = True
            else:
                print "Unknown option: %s" % (name,)
                print self.usage(cmdname)
                raise WrongOptions

        if (adding or updating) and not fname:
            print "File name must be provided"
            print self.usage(cmdname)
            raise WrongOptions
        elif not (adding or updating) and fname:
            print "File name must not be provided"
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
            if path.endswith("/"):
                print "Cannot attach to a directory: %s" % (path,)
                print self.usage(cmdname)
                raise WrongOptions
        else:
            print "Path to attach to must be provided"
            print self.usage(cmdname)
            raise WrongOptions

        # Read in data
        if fname:
            fname = os.path.expanduser(fname)
            try:
                data = open(fname, "r").read()
            except IOError:
                print "Unable to read data from file: %s" % (fname,)
                print self.usage(cmdname)
                raise WrongOptions

        resource = URL(url=path)
        if adding:
            self.shell.account.session.addAttachment(resource, os.path.basename(fname), data, content_type, return_representation)
        elif updating:
            self.shell.account.session.updateAttachment(resource, updating, os.path.basename(fname), data, content_type, return_representation)
        elif removing:
            self.shell.account.session.removeAttachment(resource, removing)

        return True


    def usage(self, name):
        return """Usage: %s OPTIONS PATH
PATH is a relative or absolute path.

Options:
-f   file name of data to put [REQUIRED]
-t   content-type of data being attached [DEFAULT: text/plain]
-a   adding new attachment
-u   updating managed-id
-r   removing managed-id
""" % (name,)


    def helpDescription(self):
        return "Add, update or remove an attachment for a calendar object resource on the server."

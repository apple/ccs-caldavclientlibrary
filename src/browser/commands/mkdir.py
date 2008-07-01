##
# Copyright (c) 2007-2008 Apple Inc. All rights reserved.
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

from browser.command import Command
from browser.command import WrongOptions
from protocol.url import URL
import getopt
import os

class Cmd(Command):
    
    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("mkdir",)
        
    def execute(self, name, options):

        opts, args = getopt.getopt(options.split(), '')

        for name, _ignore_value in opts:
            
            print "Unknown option: %s" % (name,)
            print self.usage(name)
            raise WrongOptions
        
        if len(args) != 1:
            print "Wrong number of arguments: %d" % (len(args),)
            print self.usage(name)
            raise WrongOptions

        path = args[0]
        if not path.startswith("/"):
            path = os.path.join(self.shell.wd, path)
        if not path.endswith("/"):
            path += "/"

        resource = URL(url=path)
        self.shell.account.session.makeCollection(resource)
        return True

    def complete(self, text):
        return self.shell.wdcomplete(text)

    def usage(self, name):
        return """Usage: %s PATH
PATH is a relative or absolute path.

""" % (name,)

    def helpDescription(self):
        return "Creates a regular collection."

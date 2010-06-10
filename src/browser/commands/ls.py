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

from browser.command import Command
from browser.command import WrongOptions
from protocol.webdav.definitions import davxml
from protocol.url import URL
import os
import getopt
import shlex

class Cmd(Command):
    
    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("ls",)
        
    def execute(self, name, options):
        
        longlist = False
        path = None
        displayname = False

        opts, args = getopt.getopt(shlex.split(options), 'adl')

        for name, _ignore_value in opts:
            
            if name == "-a":
                pass
            elif name == "-d":
                displayname = True
                longlist = True
            elif name == "-l":
                longlist = True
            else:
                print "Unknown option: %s" % (name,)
                print self.usage(name)
                raise WrongOptions
        
        if len(args) > 1:
            print "Wrong number of arguments: %d" % (len(args),)
            print self.usage(name)
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

        props = (davxml.resourcetype,)
        if longlist:
            props += (davxml.displayname, davxml.getcontentlength, davxml.getlastmodified,)
        results = self.shell.account.session.getPropertiesOnHierarchy(resource, props)
        items = results.keys()
        items.sort()
        for rurl in items:
            if rurl == path:
                continue
            if longlist:
                props = results[rurl]
                size = props.get(davxml.getcontentlength, "-")
                if not size:
                    size = "0"
                modtime = props.get(davxml.getlastmodified, "-")
                if displayname:
                    print "% 8s %s %s '%s'" % (size, modtime, rurl[len(path):], props.get(davxml.displayname, ''))
                else:
                    print "% 8s %s %s" % (size, modtime, rurl[len(path):])
            else:
                print rurl[len(path):]
            
        return True

    def complete(self, text):
        return self.shell.wdcomplete(text)

    def usage(self, name):
        return """Usage: %s [OPTIONS] [PATH]
PATH is a relative or absolute path.

Options:
-d   long listing + DAV:displayname
-l   long listing
""" % (name,)

    def helpDescription(self):
        return "List the contents of a directory."

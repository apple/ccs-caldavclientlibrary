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
from protocol.caldav.definitions import csxml
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
        ctag = False
        etag = False
        synctoken = False

        opts, args = getopt.getopt(shlex.split(options), 'acdels')

        for name, _ignore_value in opts:
            
            if name == "-a":
                pass
            elif name == "-c":
                ctag = True
                longlist = True
            elif name == "-d":
                displayname = True
                longlist = True
            elif name == "-e":
                etag = True
                longlist = True
            elif name == "-l":
                longlist = True
            elif name == "-s":
                synctoken = True
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
            props += (davxml.getcontentlength, davxml.getlastmodified,)
        if ctag:
            props += (csxml.getctag,)
        if etag:
            props += (davxml.getetag,)
        if synctoken:
            props += (davxml.synctoken,)
        results = self.shell.account.session.getPropertiesOnHierarchy(resource, props)
        items = results.keys()
        items.sort()
        lines = []
        for rurl in items:
            if rurl == path:
                continue
            line = []
            if longlist:
                props = results[rurl]
                size = props.get(davxml.getcontentlength, "-")
                if not size:
                    size = "0"
                line.append("%s" % (size,))
                modtime = props.get(davxml.getlastmodified, "-")
                line.append(modtime)
                line.append(rurl[len(path):])
                if displayname:
                    line.append("name:'%s'" % (props.get(davxml.displayname, '-'),))
                if ctag:
                    line.append("ctag:'%s'" % (props.get(csxml.getctag, '-'),))
                if etag:
                    line.append("etag:'%s'" % (props.get(davxml.getetag, '-'),))
                if synctoken:
                    line.append("sync:'%s'" % (props.get(davxml.synctoken, '-'),))
            else:
                line.append(rurl[len(path):])
            lines.append(line)
        
        if lines:
            # Get column widths
            widths = [0] * len(lines[0]) 
            for line in lines:
                for ctr, col in enumerate(line):
                    widths[ctr] = max(widths[ctr], len(col))
            
            # Write out each one
            for line in lines:
                for ctr, col in enumerate(line):
                    if ctr in (0, 1):
                        print col.rjust(widths[ctr] + 2),
                    else:
                        print col.ljust(widths[ctr] + 2),
                print
        return True

    def complete(self, text):
        return self.shell.wdcomplete(text)

    def usage(self, name):
        return """Usage: %s [OPTIONS] [PATH]
PATH is a relative or absolute path.

Options:
-c   long listing + CS:getctag
-d   long listing + DAV:displayname
-e   long listing + DAV:getetag
-l   long listing
-s   long listing + DAV:sync-token
""" % (name,)

    def helpDescription(self):
        return "List the contents of a directory."

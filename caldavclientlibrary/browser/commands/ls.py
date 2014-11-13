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
from caldavclientlibrary.protocol.caldav.definitions import csxml, caldavxml
from caldavclientlibrary.protocol.webdav.definitions import davxml
from caldavclientlibrary.protocol.url import URL
import os
import getopt
import shlex
import urllib

class Cmd(Command):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("ls",)
        self.do_wd_complete = True


    def execute(self, cmdname, options):

        longlist = False
        path = None
        rtype = False
        displayname = False
        ctag = False
        etag = False
        supported_components = False
        synctoken = False

        opts, args = getopt.getopt(shlex.split(options), 'acdeilrs')

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
            elif name == "-i":
                supported_components = True
                longlist = True
            elif name == "-l":
                longlist = True
            elif name == "-r":
                rtype = True
                longlist = True
            elif name == "-s":
                synctoken = True
                longlist = True
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

        props = (davxml.resourcetype,)
        if longlist:
            props += (davxml.getcontentlength, davxml.getlastmodified,)
        if ctag:
            props += (csxml.getctag,)
        if displayname:
            props += (davxml.displayname,)
        if etag:
            props += (davxml.getetag,)
        if supported_components:
            props += (caldavxml.supported_calendar_component_set,)
        if synctoken:
            props += (davxml.synctoken,)
        results = self.shell.account.session.getPropertiesOnHierarchy(resource, props)
        items = results.keys()
        items.sort()
        lines = []
        for rurl in items:
            rurl = urllib.unquote(rurl)
            if rurl == path:
                continue
            line = []
            if longlist:
                props = results[urllib.quote(rurl)]
                size = props.get(davxml.getcontentlength, "-")
                if not size:
                    size = "0"
                line.append("%s" % (size,))
                modtime = props.get(davxml.getlastmodified, "-")
                line.append(modtime)
                line.append(rurl[len(path):])
                if rtype:
                    if isinstance(props.get(davxml.resourcetype), str):
                        line.append("type:-")
                    else:
                        line.append("type:%s" % (",".join([child.tag.split("}")[1] for child in props.get(davxml.resourcetype).getchildren()])))
                if displayname:
                    line.append("name:'%s'" % (props.get(davxml.displayname, '-'),))
                if ctag:
                    line.append("ctag:'%s'" % (props.get(csxml.getctag, '-'),))
                if etag:
                    line.append("etag:'%s'" % (props.get(davxml.getetag, '-'),))
                if supported_components and props.get(caldavxml.supported_calendar_component_set) is not None:
                    line.append("comp:%s" % (",".join([child.get("name", "") for child in props.get(caldavxml.supported_calendar_component_set).getchildren()])))
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
                    if ctr in (0, 1) and longlist:
                        print col.rjust(widths[ctr] + 2),
                    else:
                        print col.ljust(widths[ctr] + 2),
                print
        return True


    def usage(self, name):
        return """Usage: %s [OPTIONS] [PATH]
PATH is a relative or absolute path.

Options:
-c   long listing + CS:getctag
-d   long listing + DAV:displayname
-e   long listing + DAV:getetag
-i   long listing + CALDAV:supported-calendar-component-set
-l   long listing
-r   long listing + DAV:resourcetype
-s   long listing + DAV:sync-token
""" % (name,)


    def helpDescription(self):
        return "List the contents of a directory."

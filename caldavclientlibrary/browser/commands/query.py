##
# Copyright (c) 2012-2013 Apple Inc. All rights reserved.
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
from caldavclientlibrary.protocol.webdav.definitions import davxml
import getopt
import os
import shlex
import time
from caldavclientlibrary.protocol.caldav.definitions import caldavxml

class Cmd(Command):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("query",)
        self.do_wd_complete = True


    def execute(self, cmdname, options):

        timerange = False
        start = None
        end = None
        expand = False
        data = False

        opts, args = getopt.getopt(shlex.split(options), 'ts:e:xd')

        for name, value in opts:

            if name == "-t":
                timerange = True
            elif name == "-s":
                start = value
            elif name == "-e":
                end = value
            elif name == "-x":
                expand = True
            elif name == "-d":
                data = True
            else:
                print "Unknown option: %s" % (name,)
                print self.usage(cmdname)
                raise WrongOptions

        if len(args) > 1:
            print "Wrong number of arguments: %d" % (len(args),)
            print self.usage(cmdname)
            raise WrongOptions

        path = args[0] if len(args) else self.shell.wd
        if not path.startswith("/"):
            path = os.path.join(self.shell.wd, path)
        if not path.endswith("/"):
            path += "/"

        resource = URL(url=path)

        now = time.time()
        if timerange and start is None:
            now_tm = time.gmtime(now)
            start = "%04d%02d%02dT000000Z" % (now_tm.tm_year, now_tm.tm_mon, now_tm.tm_mday,)
        if timerange and end is None:
            tomorrow_tm = time.gmtime(now + 24 * 60 * 60)
            end = "%04d%02d%02dT000000Z" % (tomorrow_tm.tm_year, tomorrow_tm.tm_mon, tomorrow_tm.tm_mday,)

        props = (davxml.getetag,)
        if data and not expand:
            props += (caldavxml.calendar_data,)
        results = self.shell.account.session.queryCollection(resource, timerange, start, end, expand, props=props)
        for href in results:
            print href

        return True


    def usage(self, name):
        return """Usage: %s OPTIONS PATH
PATH is a relative or absolute path.

Options:
-t        do time-range query
-s        start time [DEFAULT today]
-e        end time [DEFAULT tomorrow]
-x        expand components
-d        return data
""" % (name,)


    def helpDescription(self):
        return "Query a calendar for data."

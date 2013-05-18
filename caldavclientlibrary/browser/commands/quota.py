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
import shlex
from caldavclientlibrary.protocol.webdav.definitions import davxml

class Cmd(Command):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("quota",)
        self.do_wd_complete = True


    def execute(self, cmdname, options):

        opts, args = getopt.getopt(shlex.split(options), '')

        for name, _ignore_value in opts:

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
        results, bad = self.shell.account.session.getProperties(resource, (davxml.quota_available_bytes, davxml.quota_used_bytes))
        if davxml.quota_available_bytes in bad:
            print "Could not retrieve DAV:quota-available-bytes property, status=%d" % (bad[davxml.quota_available_bytes],)
        elif davxml.quota_used_bytes in bad:
            print "Could not retrieve DAV:quota-used-bytes property, status=%d" % (bad[davxml.quota_used_bytes],)
        else:
            quota_available = int(results[davxml.quota_available_bytes])
            quota_used = int(results[davxml.quota_used_bytes])


        def _printSmartSize(size):

            if size < 1024:
                return "%d bytes" % (size,)
            elif size < 1024 * 1024:
                return "%.1f KB" % (size / 1024.0,)
            elif size < 1024 * 1024 * 1024:
                return "%.1f MB" % (size / (1024.0 * 1024.0),)
            else:
                return "%.1f GB" % (size / (1024.0 * 1024.0 * 1024.0),)

        print "Used %s of %s (free: %s)" % (
            _printSmartSize(quota_used),
            _printSmartSize(quota_used + quota_available),
            _printSmartSize(quota_available),
        )

        return True


    def usage(self, name):
        return """Usage: %s [PATH]
PATH is a relative or absolute path.

""" % (name,)


    def helpDescription(self):
        return "Checks quota on the specified PATH."

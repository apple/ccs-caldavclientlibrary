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

from caldavclientlibrary.browser.command import Command, CommandError
from caldavclientlibrary.browser.command import WrongOptions
from caldavclientlibrary.protocol.url import URL
import getopt
import shlex

class Cmd(Command):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("calendars",)
        self.do_wd_complete = True


    def execute(self, cmdname, options):
        opts, args = getopt.getopt(shlex.split(options), '')
        if len(opts) != 0:
            print self.usage(cmdname)
            raise WrongOptions

        if len(args) > 1:
            print "Wrong number of arguments: %d" % (len(args),)
            print self.usage(cmdname)
            raise WrongOptions
        pid = args[0] if args else None
        if pid and pid.find("/") == -1:
            pid = "/principals/__uids__/%s/" % pid
        ppath = URL(url=pid) if pid else None
        principal = self.shell.account.getPrincipal(ppath)
        if principal is None:
            print "No principal found for %s" % (ppath if ppath else "current principal")
            raise CommandError

        homeset = principal.homeset
        if not homeset:
            print "No calendar home set found for %s" % (principal.principalPath,)
            raise CommandError

        newpath = homeset[0].path
        result = self.shell.setWD(newpath)

        if not result:
            print "%s: No such directory" % (newpath,)

        return result


    def usage(self, name):
        return """Usage: %s [PRINCIPAL]
PRINCIPAL is a principal-URL or principal UID.
""" % (name,)


    def helpDescription(self):
        return "Change working directory to calendar home for current or specified principal."

##
# Copyright (c) 2007-2015 Apple Inc. All rights reserved.
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
from caldavclientlibrary.protocol.url import URL
import json

class Cmd(Command):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("gettrash",)


    def execute(self, cmdname, options):

        principal = self.shell.account.getPrincipal()
        homeset = principal.homeset
        if not homeset:
            print "No calendar home set found for %s" % (principal.principalPath,)
            raise CommandError

        homepath = homeset[0].path

        resource = URL(url="{}?action=gettrashcontents".format(homepath))
        result = self.shell.account.session.writeData(resource, None, None, method="POST")
        jresult = json.loads(result)

        if "trashedcollections" in jresult and jresult["trashedcollections"]:
            print
            print "Trashed Calendar Collections:"
            for calendar in jresult["trashedcollections"]:
                print "  Name: {}  - trashed: {} - children: {} - RecoveryID: {}".format(calendar["displayName"], calendar["whenTrashed"], len(calendar["children"]), calendar["recoveryID"],)

        if "untrashedcollections" in jresult and jresult["untrashedcollections"]:
            print
            print "Trashed Calendar Objects:"
            for calendar in jresult["untrashedcollections"]:
                print
                print "  Calendar Collection: {} - children: {}".format(calendar["displayName"], len(calendar["children"]))
                for child in calendar["children"]:
                    print "    Title: {} - Start: {} - Trashed: {} - RecoveryID: {}".format(child["summary"], child["starttime"], child["whenTrashed"], child["recoveryID"])

        return True


    def usage(self, name):
        return """Usage: %s
""" % (name,)


    def helpDescription(self):
        return "Get the contents of the trash of the current user."

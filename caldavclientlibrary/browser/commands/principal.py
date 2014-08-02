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
import getopt
import shlex

class Cmd(Command):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("principal",)


    def execute(self, cmdname, options):
        refresh = False
        resolve = True
        principal = None
        print_proxies = False

        opts, args = getopt.getopt(shlex.split(options), 'fnp:x')

        for name, value in opts:

            if name == "-f":
                refresh = True
            elif name == "-n":
                resolve = False
            elif name == "-p":
                principal = self.shell.account.getPrincipal(URL(url=value), refresh=refresh)
            elif name == "-x":
                print_proxies = True
            else:
                print "Unknown option: %s" % (name,)
                print self.usage(cmdname)
                raise WrongOptions

        if len(args) > 0:
            print "Wrong number of arguments: %d" % (len(args),)
            print self.usage(cmdname)
            raise WrongOptions

        if not principal:
            principal = self.shell.account.getPrincipal(refresh=refresh)

        print """
    Principal Path    : %s
    Display Name      : %s
    Principal URL     : %s
    Alternate URLs    : %s
    Group Members     : %s
    Memberships       : %s
    Calendar Homes    : %s
    Outbox URL        : %s
    Inbox URL         : %s
    Calendar Addresses: %s
    Address Book Homes: %s
""" % (
            principal.principalPath,
            principal.getSmartDisplayName(),
            principal.principalURL,
            utils.printList(principal.alternateURIs),
            utils.printPrincipalPaths(self.shell.account, principal.memberset, resolve, refresh),
            utils.printPrincipalPaths(self.shell.account, principal.memberships, resolve, refresh),
            utils.printList(principal.homeset),
            principal.outboxURL,
            principal.inboxURL,
            utils.printList(principal.cuaddrs),
            utils.printList(principal.adbkhomeset),
        ),

        if print_proxies:
            utils.printProxyPrincipals(self.shell.account, principal, True, True, resolve, False, refresh)

        print ""

        return True


    def usage(self, name):
        return """Usage: %s [OPTIONS]
Options:
    -f force reload of all cached principals to be returned
    -p principal path to request proxies for [OPTIONAL]
        if not present, the current user's principal is used.
    -n do not resolve references to other principals.
    -x print proxy details as well.
""" % (name,)


    def helpDescription(self):
        return "Get details on principals."

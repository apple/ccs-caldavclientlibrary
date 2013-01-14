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
from caldavclientlibrary.browser.subshell import SubShell
from caldavclientlibrary.browser import commands
import getopt
import shlex

class Cmd(Command):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("proxies",)
        self.subshell = None


    def execute(self, cmdname, options):

        interactive = False
        read = False
        write = False
        principal = self.shell.account.getPrincipal()

        try:
            opts, args = getopt.getopt(shlex.split(options), 'irwp:')
        except getopt.GetoptError, e:
            print str(e)
            print self.usage(cmdname)
            raise WrongOptions

        for name, value in opts:

            if name == "-i":
                interactive = True
            elif name == "-r":
                read = True
            elif name == "-w":
                write = True
            elif name == "-p":
                principal = self.shell.account.getPrincipal(URL(url=value))
            else:
                print "Unknown option: %s" % (name,)
                print self.usage(cmdname)
                raise WrongOptions

        if len(args) > 0:
            print "Wrong number of arguments: %d" % (len(args),)
            print self.usage(cmdname)
            raise WrongOptions

        if interactive:
            self.doInteractiveMode(principal)
        else:
            utils.printProxyPrincipals(self.shell.account, principal, read or not write, write or not read, True)

        return True


    def doInteractiveMode(self, principal):

        print "Entering Proxy edit mode on principal: %s (%s)" % (principal.getSmartDisplayName(), principal.principalURL)
        if not self.subshell:
            self.subshell = SubShell(self.shell, "Proxy", (
                commands.help.Cmd(),
                commands.logging.Cmd(),
                commands.quit.Cmd(),
                Add(),
                Remove(),
                List(),
            ))
        self.subshell.principal = principal
        self.subshell.account = self.shell.account
        self.subshell.run()


    def usage(self, name):
        return """Usage: %s [OPTIONS]
PRINCIPAL - principal path to request proxies for.

Options:
    -i interactive mode for adding, changing and deleting proxies.
    -r read proxies [OPTIONAL]
    -w write proxies [OPTIONAL]
        if neither is present, both are displayed.

    -p principal path to request proxies for [OPTIONAL]
        if not present, the current user's principal is used.
""" % (name,)


    def helpDescription(self):
        return "Displays the delegates for the chosen user."



class CommonProxiesCommand(Command):

    def parseOptions(self, name, options):
        read = False
        write = False

        try:
            opts, args = getopt.getopt(options.split(), 'rw')
        except getopt.GetoptError, e:
            print str(e)
            print self.usage(name)
            raise WrongOptions

        for name, _ignore_value in opts:

            if name == "-r":
                read = True
                if write:
                    print "Only one of -r and -w may be specified."
                    print self.usage(name)
                    raise WrongOptions
            elif name == "-w":
                write = True
                if read:
                    print "Only one of -r and -w may be specified."
                    print self.usage(name)
                    raise WrongOptions
            else:
                print "Unknown option: %s" % (name,)
                print self.usage(name)
                raise WrongOptions

        if not read and not write:
            print "One of -r and -w must be specified."
            print self.usage(name)
            raise WrongOptions

        if len(args) > 0:
            print "Wrong number of arguments: %d" % (len(args),)
            print self.usage(name)
            raise WrongOptions

        return read


    def printProxyList(self, read):

        if read:
            principals = self.shell.principal.getReadProxies()
        else:
            principals = self.shell.principal.getWriteProxies()
        if principals:
            print utils.printPrincipalList(principals)
        else:
            print "There are no proxies of the specified type."
        return principals



class Add(CommonProxiesCommand):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("add",)


    def execute(self, name, options):

        read = self.parseOptions(name, options)

        principals = self.printProxyList(read)

        choice = utils.textInput("New principal [q - quit]: ")
        if choice == "q":
            return None
        principal = self.shell.account.getPrincipal(URL(url=choice))
        if principal:
            principals.append(principal)
            principals = [principal.principalURL for principal in principals]
            if read:
                self.shell.principal.setReadProxies(principals)
            else:
                self.shell.principal.setWriteProxies(principals)


    def usage(self, name):
        return """Usage: %s [OPTIONS]

Options:
    -r add to read-only proxy list
    -w add to read-write proxy list
        one of -r or -w must be present.
""" % (name,)


    def helpDescription(self):
        return "Add proxies on principal."



class Remove(CommonProxiesCommand):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("remove",)


    def execute(self, name, options):

        read = self.parseOptions(name, options)

        principals = self.printProxyList(read)

        choice = utils.numericInput("Select principal: ", 1, len(principals), allow_q=True)
        if choice == "q":
            return None
        del principals[choice - 1]
        principals = [principal.principalURL for principal in principals]
        if read:
            self.shell.principal.setReadProxies(principals)
        else:
            self.shell.principal.setWriteProxies(principals)


    def usage(self, name):
        return """Usage: %s [OPTIONS]

Options:
    -r remove from read-only proxy list
    -w remove from read-write proxy list
        one of -r or -w must be present.
""" % (name,)


    def helpDescription(self):
        return "Remove proxies on principal."



class List(CommonProxiesCommand):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("list",)


    def execute(self, name, options):

        utils.printProxyPrincipals(self.shell.account, self.shell.principal, True, True, True, True)
        return True


    def usage(self, name):
        return """Usage: %s
""" % (name,)


    def helpDescription(self):
        return "List current ACLs on existing resource."

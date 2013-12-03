##
# Copyright (c) 2013 Apple Inc. All rights reserved.
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

from caldavclientlibrary.browser import commands
from caldavclientlibrary.browser import utils
from caldavclientlibrary.browser.command import Command
from caldavclientlibrary.browser.command import WrongOptions
from caldavclientlibrary.browser.subshell import SubShell
from caldavclientlibrary.protocol.url import URL
import getopt
import os
import readline
import shlex

class Cmd(Command):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("share",)
        self.subshell = None
        self.do_wd_complete = True


    def execute(self, cmdname, options):

        interactive = False
        path = None

        try:
            opts, args = getopt.getopt(shlex.split(options), 'i')
        except getopt.GetoptError, e:
            print str(e)
            print self.usage(cmdname)
            raise WrongOptions

        for name, _ignore_value in opts:

            if name == "-i":
                interactive = True
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

        invites = self.shell.account.session.getInvites(resource)
        if invites is None:
            print "Could not retrieve CS:invite property."
        else:
            if interactive:
                self.doInteractiveMode(resource, invites)
            else:
                print utils.printInviteList(invites, self.shell.account)

        return True


    def doInteractiveMode(self, resource, invites):

        print "Entering sharing edit mode on resource: %s" % (resource.relativeURL(),)
        if not self.subshell:
            self.subshell = SubShell(self.shell, "Share", (
                commands.help.Cmd(),
                commands.logging.Cmd(),
                commands.quit.Cmd(),
                Add(),
                Change(),
                Remove(),
                List(),
            ))
        self.subshell.resource = resource
        self.subshell.account = self.shell.account
        self.subshell.run()


    def usage(self, name):
        return """Usage: %s [OPTIONS] [PATH]
PATH is a relative or absolute path.

Options:
-i    interactive mode for adding, changing and deleting invitees.
    if not present, existing invitees will be printed.
""" % (name,)


    def helpDescription(self):
        return "Manage sharing of an address book, calendar or address book group."



class CommonSharingCommand(Command):

    def displayInviteList(self):
        # First list the current set
        invites = self.shell.shell.account.session.getInvites(self.shell.resource)
        if invites is None:
            print "Could not retrieve CS:invite property."
        else:
            print utils.printInviteList(invites, self.shell.account)
        return invites


    def createInvite(self, oldinvite=None):

        if oldinvite is None:
            href = utils.textInput("Enter principal id: ", None)
            if href.startswith("user") or href.startswith("puser"):
                href = "/principals/users/%s" % (href,)
            principal = self.shell.shell.account.getPrincipal(URL(url=href))
            user_uid = principal.principalURL.relativeURL()
        else:
            user_uid = oldinvite.user_uid

        oldmode = "w" if oldinvite is None else ("w" if oldinvite.access == "read-write" else "r")
        read_write = utils.choiceInput("Read or Read-Write Mode [r/w]: ", ("r", "w",), insert=oldmode)
        read_write = (read_write == "w")

        summary = utils.textInput("Summary: ", insert=(oldinvite.summary if oldinvite else "Shared"))

        return user_uid, read_write, summary



class Add(CommonSharingCommand):

    def __init__(self):
        super(Add, self).__init__()
        self.cmds = ("add",)


    def execute(self, name, options):

        # Try and get the new details
        user_uid, read_write, summary = self.createInvite()

        # Now execute
        self.shell.shell.account.session.addInvitees(self.shell.resource, [user_uid, ], read_write, summary)


    def usage(self, name):
        return """Usage: %s
""" % (name,)


    def helpDescription(self):
        return "Add invite to existing resource."



class Change(CommonSharingCommand):

    def __init__(self):
        super(Change, self).__init__()
        self.cmds = ("change",)


    def execute(self, name, options):

        # First list the current set
        invites = self.displayInviteList()
        if len(invites.invitees):
            # Ask user which one to delete
            while True:
                result = raw_input("Change invite at [1 - %d] or cancel [q]: " % (len(invites.invitees),))
                if readline.get_current_history_length():
                    readline.remove_history_item(readline.get_current_history_length() - 1)
                if not result:
                    continue
                if result[0] == "q":
                    break
                try:
                    number = int(result) - 1
                except ValueError:
                    print "Invalid input, try again."
                    continue

                # Try and get the new details
                user_uid, read_write, summary = self.createInvite(invites.invitees[number])

                # Now execute
                self.shell.shell.account.session.addInvitees(self.shell.resource, [user_uid, ], read_write, summary)
                break


    def usage(self, name):
        return """Usage: %s
""" % (name,)


    def helpDescription(self):
        return "Change invite on existing resource."



class Remove(CommonSharingCommand):

    def __init__(self):
        super(Remove, self).__init__()
        self.cmds = ("remove",)


    def execute(self, name, options):

        # First list the current set
        invites = self.displayInviteList()
        if len(invites.invitees):
            # Ask user which one to delete
            while True:
                result = raw_input("Remove invite [1 - %d] or cancel [q]: " % (len(invites.invitees),))
                if readline.get_current_history_length():
                    readline.remove_history_item(readline.get_current_history_length() - 1)
                if not result:
                    continue
                if result[0] == "q":
                    break
                try:
                    number = int(result) - 1
                except ValueError:
                    print "Invalid input, try again."
                    continue

                # Now execute
                self.shell.shell.account.session.removeInvitee(self.shell.resource, invites.invitees[number])
                break


    def usage(self, name):
        return """Usage: %s
""" % (name,)


    def helpDescription(self):
        return "Remove invite on existing resource."



class List(CommonSharingCommand):

    def __init__(self):
        super(List, self).__init__()
        self.cmds = ("list",)


    def execute(self, name, options):

        self.displayInviteList()
        return True


    def usage(self, name):
        return """Usage: %s
""" % (name,)


    def helpDescription(self):
        return "List current invitees on existing resource."

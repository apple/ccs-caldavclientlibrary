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
import getopt
import readline
import shlex

class Cmd(Command):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("notifications",)
        self.subshell = None


    def execute(self, cmdname, options):

        interactive = False

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

        if len(args) != 0:
            print "Wrong number of arguments: %d" % (len(args),)
            print self.usage(cmdname)
            raise WrongOptions

        principal = self.shell.account.getPrincipal(None)
        resource = principal.notification_URL

        notifications = self.shell.account.session.getNotifications(resource)
        if interactive:
            self.doInteractiveMode(resource, notifications)
        else:
            print utils.printNotificationsList(notifications, self.shell.account)

        return True


    def doInteractiveMode(self, resource, invites):

        print "Entering notifications edit mode on resource: %s" % (resource.relativeURL(),)
        if not self.subshell:
            self.subshell = SubShell(self.shell, "Notifications", (
                commands.help.Cmd(),
                commands.logging.Cmd(),
                commands.quit.Cmd(),
                Accept(),
                Decline(),
                Delete(),
                List(),
            ))
        self.subshell.resource = resource
        self.subshell.account = self.shell.account
        self.subshell.run()


    def usage(self, name):
        return """Usage: %s [OPTIONS] [PATH]
PATH is a relative or absolute path.

Options:
-i    interactive mode for accepting or declining invites.
    if not present, existing notifications will be printed.
""" % (name,)


    def helpDescription(self):
        return "Manage sharing notifications of an address book, calendar or address book group."



class CommonNotificationsCommand(Command):

    def displayNotificationsList(self):
        # First list the current set
        notifications = self.shell.shell.account.session.getNotifications(self.shell.resource)
        if not notifications:
            print "No notifications."
        else:
            print utils.printNotificationsList(notifications, self.shell.account)
        return notifications



class Process(CommonNotificationsCommand):

    def __init__(self, accept):
        super(Command, self).__init__()
        self.accept = accept


    def execute(self, name, options):

        # First list the current set
        notifications = self.displayNotificationsList()
        if notifications:
            # Ask user which one to delete
            while True:
                result = raw_input("%s invite at [1 - %d] or cancel [q]: " % (self.cmds[0].title(), len(notifications),))
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

                # Now execute and delete the notification if processed OK
                if self.shell.shell.account.session.processNotification(self.shell.account.getPrincipal(None), notifications[number], self.accept):
                    self.shell.shell.account.session.deleteResource(notifications[number].url)
                break



class Accept(Process):

    def __init__(self):
        super(Accept, self).__init__(True)
        self.cmds = ("accept",)


    def usage(self, name):
        return """Usage: %s
""" % (name,)


    def helpDescription(self):
        return "Accept an invite."



class Decline(Process):

    def __init__(self):
        super(Decline, self).__init__(False)
        self.cmds = ("decline",)


    def usage(self, name):
        return """Usage: %s
""" % (name,)


    def helpDescription(self):
        return "Decline an invite."



class Delete(CommonNotificationsCommand):

    def __init__(self):
        super(Delete, self).__init__()
        self.cmds = ("delete",)


    def execute(self, name, options):

        # First list the current set
        notifications = self.displayNotificationsList()
        if notifications:
            # Ask user which one to delete
            while True:
                result = raw_input("%s invite at [1 - %d] or cancel [q]: " % (self.cmds[0].title(), len(notifications),))
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

                # Now delete the notification
                self.shell.shell.account.session.deleteResource(notifications[number].url)
                break


    def usage(self, name):
        return """Usage: %s
""" % (name,)


    def helpDescription(self):
        return "Delete notification resource."



class List(CommonNotificationsCommand):

    def __init__(self):
        super(List, self).__init__()
        self.cmds = ("list",)


    def execute(self, name, options):

        self.displayNotificationsList()
        return True


    def usage(self, name):
        return """Usage: %s
""" % (name,)


    def helpDescription(self):
        return "List current invites for user."

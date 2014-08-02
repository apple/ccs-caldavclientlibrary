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
from caldavclientlibrary.protocol.webdav.definitions import davxml
from caldavclientlibrary.browser.subshell import SubShell
from caldavclientlibrary.browser import commands
from caldavclientlibrary.protocol.webdav.ace import ACE
from caldavclientlibrary.browser import utils
from caldavclientlibrary.protocol.caldav.definitions import caldavxml
from xml.etree.ElementTree import QName
import readline
import os
import getopt
import shlex

class Cmd(Command):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("acl",)
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

        results, bad = self.shell.account.session.getProperties(resource, (davxml.acl,))
        if davxml.acl in bad:
            print "Could not retrieve DAV:acl property, status=%d" % (bad[davxml.acl],)
        else:
            if interactive:
                self.doInteractiveMode(resource, results[davxml.acl])
            else:
                aces = ACE.parseFromACL(results[davxml.acl])
                print utils.printACEList(aces, self.shell.account)

        return True


    def doInteractiveMode(self, resource, acls):

        print "Entering ACL edit mode on resource: %s" % (resource.relativeURL(),)
        if not self.subshell:
            self.subshell = SubShell(self.shell, "ACL", (
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
-i    interactive mode for adding, changing and deleting ACLs.
    if not present, existing ACLs will be printed.
""" % (name,)


    def helpDescription(self):
        return "Manage the access privileges of a directory or file."



class CommonACLCommand(Command):

    def displayACEList(self):
        # First list the current set
        results, bad = self.shell.shell.account.session.getProperties(self.shell.resource, (davxml.acl,))
        if davxml.acl in bad:
            print "Could not retrieve DAV:acl property, status=%d" % (bad[davxml.acl],)
            return None
        else:
            aces = ACE.parseFromACL(results[davxml.acl])
            print utils.printACEList(aces, self.shell.shell.account)
            return aces


    def createACE(self, oldace=None):

        ace = ACE()
        print "Principal Type:"
        print "  1. Principal path"
        print "  2. All"
        print "  3. Authenticated"
        print "  4. Unauthenticated"
        print "  5. Property"
        insert = None
        if oldace:
            mapper = {
                str(davxml.href): "1",
                str(davxml.all): "2",
                str(davxml.authenticated): "3",
                str(davxml.unauthenticated): "4",
                str(davxml.property): "5",
            }
            insert = mapper.get(oldace.principal)
        choice = utils.numericInput("Select type: ", 1, 5, insert=insert)
        if choice == "q":
            return None

        if choice == 1:
            href = utils.textInput("Enter principal path: ", insert=oldace.data if oldace else None)
            principal = self.shell.shell.account.getPrincipal(URL(url=href))
            ace.principal = str(davxml.href)
            ace.data = principal.principalURL.relativeURL()
        elif choice == 2:
            ace.principal = str(davxml.all)
        elif choice == 3:
            ace.principal = str(davxml.authenticated)
        elif choice == 4:
            ace.principal = str(davxml.unauthenticated)
        elif choice == 5:
            prop = utils.textInput("Enter property qname: ", insert=str(oldace.data) if oldace else None)
            ace.principal = str(davxml.property)
            ace.data = QName(prop)

        invert = utils.yesNoInput("Invert principal [y/n]: ", insert=("y" if oldace.invert else "n") if oldace else None)
        ace.invert = (invert == "y")

        grant = utils.choiceInput("Grant or Deny privileges [g/d]: ", ("g", "d",), insert=("g" if oldace.grant else "d") if oldace else None)
        ace.grant = (grant == "g")

        print "Privileges:"
        print "  a. {DAV}read"
        print "  b. {DAV}write"
        print "  c. {DAV}write-properties"
        print "  d. {DAV}write-content"
        print "  e. {DAV}read-acl"
        print "  f. {DAV}read-current-user-privilege-set"
        print "  g. {DAV}write-acl"
        print "  h. {DAV}bind"
        print "  i. {DAV}unbind"
        print "  j. {DAV}all"
        print "  k. {CALDAV}read-free-busy"
        print "  l. {CALDAV}schedule"
        print "  q. quit without changes"
        choice = utils.multiChoiceInput(
            "Select multiple items: ",
            [char for char in "abcdefghijklq"],
        )
        if "q" in choice:
            return None

        mappedPrivs = {
            'a': davxml.read,
            'b': davxml.write,
            'c': davxml.write_properties,
            'd': davxml.write_content,
            'e': davxml.read_acl,
            'f': davxml.read_current_user_privilege_set,
            'g': davxml.write_acl,
            'h': davxml.bind,
            'i': davxml.unbind,
            'j': davxml.all,
            'k': caldavxml.read_free_busy,
            'l': caldavxml.schedule,
        }
        ace.privs = ()
        for char in choice:
            ace.privs += (mappedPrivs[char],)

        return ace



class Add(CommonACLCommand):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("add",)


    def execute(self, name, options):

        # First list the current set
        aces = self.displayACEList()
        if aces:
            # Ask user which one to delete
            while True:
                result = raw_input("Add ACL before [1 - %d] or cancel [q]: " % (len(aces) + 1,))
                if readline.get_current_history_length():
                    readline.remove_history_item(readline.get_current_history_length() - 1)
                if not result:
                    continue
                if result[0] == "q":
                    break
                try:
                    number = int(result)
                    if number > len(aces):
                        number = len(aces)
                except ValueError:
                    print "Invalid input, try again."
                    continue

                # Try and get the new ace
                ace = self.createACE()
                if not ace:
                    break
                aces.insert(number, ace)

                # Now remove those that cannot be edited
                aces = [ace for ace in aces if ace.canChange()]

                # Now execute
                self.shell.shell.account.session.setACL(self.shell.resource, aces)
                break


    def usage(self, name):
        return """Usage: %s
""" % (name,)


    def helpDescription(self):
        return "Add ACL to existing resource."



class Change(CommonACLCommand):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("change",)


    def execute(self, name, options):

        # First list the current set
        aces = self.displayACEList()
        if aces:
            # Ask user which one to delete
            while True:
                result = raw_input("Change ACL at [1 - %d] or cancel [q]: " % (len(aces),))
                if readline.get_current_history_length():
                    readline.remove_history_item(readline.get_current_history_length() - 1)
                if not result:
                    continue
                if result[0] == "q":
                    break
                try:
                    number = int(result)
                except ValueError:
                    print "Invalid input, try again."
                    continue

                # Check that the targeted ace is editable
                if not aces[number - 1].canChange():
                    print "You cannot change a protected or inherited ace."
                    break

                # Try and get the new ace
                ace = self.createACE(oldace=aces[number - 1])
                if not ace:
                    break
                aces[number - 1] = ace

                # Now remove those that cannot be edited
                aces = [ace for ace in aces if ace.canChange()]

                # Now execute
                self.shell.shell.account.session.setACL(self.shell.resource, aces)
                break


    def usage(self, name):
        return """Usage: %s
""" % (name,)


    def helpDescription(self):
        return "Change ACL on existing resource."



class Remove(CommonACLCommand):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("remove",)


    def execute(self, name, options):

        # First list the current set
        aces = self.displayACEList()
        if aces:
            # Ask user which one to delete
            while True:
                result = raw_input("Remove ACL [1 - %d] or cancel [q]: " % (len(aces),))
                if readline.get_current_history_length():
                    readline.remove_history_item(readline.get_current_history_length() - 1)
                if not result:
                    continue
                if result[0] == "q":
                    break
                try:
                    number = int(result)
                except ValueError:
                    print "Invalid input, try again."
                    continue

                # Check that the targeted ace is editable
                if not aces[number - 1].canChange():
                    print "You cannot remove a protected or inherited ace."
                    break

                # Remove the one we are removing
                del aces[number - 1]

                # Now remove those that cannot be edited
                aces = [ace for ace in aces if ace.canChange()]

                # Now execute
                self.shell.shell.account.session.setACL(self.shell.resource, aces)
                break


    def usage(self, name):
        return """Usage: %s
""" % (name,)


    def helpDescription(self):
        return "Remove ACL on existing resource."



class List(CommonACLCommand):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("list",)


    def execute(self, name, options):

        self.displayACEList()
        return True


    def usage(self, name):
        return """Usage: %s
""" % (name,)


    def helpDescription(self):
        return "List current ACLs on existing resource."

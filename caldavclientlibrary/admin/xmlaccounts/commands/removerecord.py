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

from caldavclientlibrary.admin.xmlaccounts.commands.command import Command
import getopt

class RemoveRecord(Command):

    CMDNAME = "remove"

    def __init__(self):
        super(RemoveRecord, self).__init__(self.CMDNAME, "Remove a record of the specified type.")
        self.uid = None


    def usage(self):
        print """USAGE: %s TYPE [OPTIONS]

TYPE: One of "users", "groups", "locations" or "resources". Also,
"u", "g", "l" or "r" as shortcuts.

Options:
    -f    file path to accounts.xml
    --uid UID to remove
""" % (self.cmdname,)


    def execute(self, argv):
        """
        Execute the command specified by the command line arguments.

        @param argv: command line arguments.
        @type argv: C{list}

        @return: 1 for success, 0 for failure.
        @rtype: C{int}
        """

        # Check first argument for type
        argv = self.getTypeArgument(argv)
        if argv is None:
            return 0

        opts, args = getopt.getopt(argv, 'f:h', ["help", "uid=", ])

        for name, value in opts:
            if name == "-f":
                self.path = value
            elif name in ("-h", "--help"):
                self.usage()
                return 1
            elif name == "--uid":
                self.uid = value
            else:
                print "Unknown option: %s." % (name,)
                self.usage()
                return 0

        if not self.path:
            print "Must specify a path."
            self.usage()
            return 0
        if not self.uid:
            print "Must specify a UID."
            self.usage()
            return 0
        if args:
            print "Arguments not allowed."
            self.usage()
            return 0

        if not self.loadAccounts():
            return 0
        return self.doCommand()


    def doCommand(self):
        """
        Run the command.
        """
        if self.doRemove():
            return self.writeAccounts()
        return 0


    def doRemove(self):
        """
        Removes an existing record from the directory.
        """

        # First check record exists
        record = self.directory.getRecord(self.recordType, self.uid)
        if record is None:
            print "No '%s' record matching uid '%s'" % (self.recordType, self.uid,)
            return 0

        confirm = raw_input("Really delete the record for '%s' in '%s' [y/n]?" % (self.uid, self.recordType,))
        if confirm != "y":
            return 0

        self.directory.removeRecord(self.recordType, self.uid)
        return 1

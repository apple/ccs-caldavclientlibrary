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

from caldavclientlibrary.admin.xmlaccounts.directory import XMLDirectory
from xml.etree.ElementTree import XML
from StringIO import StringIO
from caldavclientlibrary.protocol.utils.xmlhelpers import BetterElementTree
from caldavclientlibrary.admin.xmlaccounts import recordtypes
from getpass import getpass

import getopt

class Command(object):

    def __init__(self, cmdname, description):
        self.path = None
        self.cmdname = cmdname
        self.description = description
        self.recordType = None


    def usage(self):
        if self.allRecordsAllowed():
            print """USAGE: %s [TYPE] [OPTIONS]

TYPE: One of "all", "users", "groups", "locations" or "resources". Also,
"a", "u", "g", "l" or "r" as shortcuts. Invalid or missing type is
treated as "all".

Options:
    -f  file path to accounts.xml
""" % (self.cmdname,)
        else:
            print """USAGE: %s TYPE [OPTIONS]

TYPE: One of "users", "groups", "locations" or "resources". Also,
"u", "g", "l" or "r" as shortcuts.

Options:
    -f  file path to accounts.xml
""" % (self.cmdname,)


    def allRecordsAllowed(self):
        """
        Indicates whether a command is able to operate on all record types in addition to
        individual record types. Sub-classes should override this if they can handle all
        record in one go.
        """
        return False


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

        opts, args = getopt.getopt(argv, 'f:h', ["help", ])

        for name, value in opts:
            if name == "-f":
                self.path = value
            elif name in ("-h", "--help"):
                self.usage()
                return 1
            else:
                print "Unknown option: %s." % (name,)
                self.usage()
                return 0

        if not self.path:
            print "Must specify a path."
            self.usage()
            return 0
        if args:
            print "Arguments not allowed."
            self.usage()
            return 0

        if not self.loadAccounts():
            return 0
        return self.doCommand()


    def getTypeArgument(self, argv):
        """
        Extract the user specified record type argument from the command line arguments.

        @param argv: command line arguments.
        @type argv: C{list}

        @return: the modified arguments (if a record type is found the corresponding argument is
            removed from the argv passed in).
        @rtype: C{list}
        """
        # Check first argument for type
        if len(argv) == 0:
            print "Must specify a record type."
            self.usage()
            return None
        type = argv[0]
        type = self.mapType(type)
        if not type and not self.allRecordsAllowed():
            print "Invalid type '%s'." % (argv[0],)
            self.usage()
            return None
        self.recordType = type if type else recordtypes.recordType_all
        if type:
            return argv[1:]
        else:
            return argv


    def mapType(self, type):
        """
        Map the specified user record type input to the actual record type identifier.

        @param type: user input from the command line.
        @type type: C{str}

        @return: identifier matching the user input, or C{None} if no match.
        @rtype: L{admin.xmlaccounts.recordtypes}
        """
        return {
            "users"    : recordtypes.recordType_users,
            "u"        : recordtypes.recordType_users,
            "groups"   : recordtypes.recordType_groups,
            "g"        : recordtypes.recordType_groups,
            "locations": recordtypes.recordType_locations,
            "l"        : recordtypes.recordType_locations,
            "resources": recordtypes.recordType_resources,
            "r"        : recordtypes.recordType_resources,
            "all"      : recordtypes.recordType_all,
            "a"        : recordtypes.recordType_all,
        }.get(type, None)


    def loadAccounts(self):
        """
        Load the entire directory from the XML file.
        """

        f = open(self.path, "r")
        if not f:
            print "Could not open file: %s" % (self.path,)
            return 0
        xmldata = f.read()
        f.close()
        self.directory = XMLDirectory()
        self.directory.parseXML(XML(xmldata))
        return 1


    def writeAccounts(self):
        """
        Write the entire directory to the XML file.
        """

        node = self.directory.writeXML()
        os = StringIO()
        xmldoc = BetterElementTree(node)
        xmldoc.writeUTF8(os)
        f = open(self.path, "w")
        if not f:
            print "Could not open file: %s for writing" % (self.path,)
            return 0
        f.write(os.getvalue())
        f.close()
        return 1


    def doCommand(self):
        """
        Run the command. Sub-classes must implement this.
        """
        raise NotImplementedError


    def promptPassword(self):
        """
        Prompt the user for a password.
        """
        while True:
            password = getpass("Password: ")
            temp = getpass("Password (again): ")
            if temp != password:
                print "Passwords do not match. Try again."
            else:
                return password


    def getMemberList(self, prompt, title, type):
        """
        Prompt the user for a list of members.
        """
        results = []
        print prompt
        while True:
            memberType = raw_input("%s type [u/g/l/r or leave empty to stop adding %s]: " % (title, type,))
            if memberType in ("u", "g", "l", "r",):
                memberUid = raw_input("%s uid [leave empty to stop adding %s]: " % (title, type,))
                if memberUid:
                    # Verify that member type exists
                    recordType = self.mapType(memberType)
                    if self.directory.containsRecord(recordType, memberUid):
                        results.append((recordType, memberUid,))
                    else:
                        print "Record uid: '%s 'of type: '%s' does not exist in the directory." % (memberUid, recordType,)
                else:
                    break
            elif memberType:
                print "Member type must be one of 'u' (users), 'g' (groups), 'l' (locations) or 'r' (resources)."
            else:
                break
        return results

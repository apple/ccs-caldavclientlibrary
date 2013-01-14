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
from caldavclientlibrary.admin.xmlaccounts import recordtypes
import itertools

class ListRecords(Command):

    CMDNAME = "list"

    def __init__(self):
        super(ListRecords, self).__init__(self.CMDNAME, "List all records of the specified type.")


    def allRecordsAllowed(self):
        """
        Indicate that this command can list all records in one go as well as each
        individual record type.
        """
        return True


    def doCommand(self):
        """
        Run the command.
        """
        self.listRecords(self.recordType)


    def listRecords(self, recordType):
        """
        Lists records of the specified record type from the directory.
        """

        if recordType == recordtypes.recordType_all:
            users = [l for l in self.directory.records.itervalues()]
            print "Full List\n"
        else:
            users = (self.directory.records[recordType],)
            print "%s List\n" % (recordType.capitalize(),)

        table = [
            ["UID", "GUID", "Name", "CUADDR", ]
        ]
        if recordType == recordtypes.recordType_all:
            table[0].insert(0, "TYPE")
            table[0].append("MEMBERS")
            table[0].append("PROXIES")
        elif recordType in (recordtypes.recordType_groups,):
            table[0].append("MEMBERS")
        elif recordType in (recordtypes.recordType_locations, recordtypes.recordType_resources,):
            table[0].append("PROXIES")
        for user in itertools.chain(*users):
            if len(table) > 1:
                table.append(None)
            cuaddrs = user.calendarUserAddresses if user.calendarUserAddresses else ("",)
            if user.recordType in (recordtypes.recordType_groups,):
                members = user.members if user.members else (None,)
            elif user.recordType in (recordtypes.recordType_locations, recordtypes.recordType_resources,):
                members = user.proxies if user.proxies else (None,)
            else:
                members = (None,)
            for ctr, items in enumerate(map(None, cuaddrs, members,)):
                cuaddr, member = items
                if cuaddr is None:
                    cuaddr = ""
                if member is None:
                    member = ""
                else:
                    member = "(%s) %s" % (member[0], member[1],)
                if recordType == recordtypes.recordType_all:
                    row = (user.recordType,)
                else:
                    row = ()
                row += (
                    user.uid if not ctr else "",
                    user.guid if not ctr else "",
                    user.name if not ctr else "",
                    cuaddr,
                )
                if recordType == recordtypes.recordType_all:
                    if user.recordType in (recordtypes.recordType_groups,):
                        row += (member, "")
                    elif user.recordType in (recordtypes.recordType_locations, recordtypes.recordType_resources,):
                        row += ("", member,)
                    else:
                        row += ("", "")
                elif user.recordType in (recordtypes.recordType_groups, recordtypes.recordType_locations, recordtypes.recordType_resources,):
                    row += (member,)
                table.append(row)

        self.printTable(table)
        return 1


    def printTable(self, table):

        maxWidths = [0 for _ignore in table[0]]
        for row in table:
            if row is not None:
                for ctr, col in enumerate(row):
                    maxWidths[ctr] = max(maxWidths[ctr], len(col) if col else 0)

        self.printDivider(maxWidths, False)
        for rowctr, row in enumerate(table):
            if row is None:
                self.printDivider(maxWidths)
            else:
                print "|",
                for colctr, col in enumerate(row):
                    print "%- *s" % (maxWidths[colctr], col if col else ""),
                    print "|",
                print ""
            if not rowctr:
                self.printDivider(maxWidths)
        self.printDivider(maxWidths, False)


    def printDivider(self, maxWidths, intermediate=True):
        t = "|" if intermediate else "+"
        for widthctr, width in enumerate(maxWidths):
            t += "-"
            t += "-" * width
            t += "-+" if widthctr < len(maxWidths) - 1 else ("-|" if intermediate else "-+")
        print t

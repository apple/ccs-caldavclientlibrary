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
from caldavclientlibrary.admin.xmlaccounts.record import XMLRecord
from uuid import uuid4
from caldavclientlibrary.admin.xmlaccounts import recordtypes

class AddRecord(Command):
    """
    Command that adds a record to the directory.
    """

    CMDNAME = "add"

    def __init__(self):
        super(AddRecord, self).__init__(self.CMDNAME, "Add a record of the specified type.")


    def doCommand(self):
        """
        Run the command.
        """
        if self.doAdd():
            return self.writeAccounts()
        return 0


    def doAdd(self):
        """
        Prompts the user for details and then adds a new record to the directory.
        """

        # Prompt for each thing we need in the record
        record = XMLRecord()
        record.recordType = self.recordType
        print "Enter the fields for the record (ctrl-D to stop at any time)"
        try:
            # uid
            while True:
                record.uid = raw_input("Id: ")
                if not record.uid:
                    print "A valid uid is required. Please try again."
                elif self.directory.containsRecord(self.recordType, record.uid):
                    print "Record uid: '%s' of type: '%s' does already exists in the directory." % (record.uid, self.recordType,)
                else:
                    break

            # guid
            while True:
                record.guid = raw_input("GUID [leave empty to auto-generate]: ")
                if record.guid and self.directory.containsGUID(record.guid):
                    print "GUID: '%s' already used in the directory" % (record.guid,)
                else:
                    break

            # password
            record.password = self.promptPassword()

            # name
            record.name = raw_input("Name: ")

            # members
            if self.recordType in (recordtypes.recordType_groups,):
                record.members = self.getMemberList("Enter members of this group", "Member", "members")

            # cuaddr
            while True:
                cuaddr = raw_input("Calendar user address [leave empty to stop adding addresses]: ")
                if cuaddr:
                    record.calendarUserAddresses.add(cuaddr)
                else:
                    break

            # auto-schedule
            if self.recordType in (recordtypes.recordType_locations, recordtypes.recordType_resources,):
                auto_schedule = raw_input("Turn on automatic scheduling [y/n]?: ")
                if auto_schedule == "y":
                    record.autoSchedule = True

            # enabled for calendaring
            if self.recordType in (recordtypes.recordType_users, recordtypes.recordType_groups,):
                enable_calendars = raw_input("Create calendar account rather than access-only account [y/n]?: ")
                if enable_calendars == "n":
                    record.enabledForCalendaring = False

            # proxies
            if self.recordType in (recordtypes.recordType_locations, recordtypes.recordType_resources,):
                record.proxies = self.getMemberList("Enter proxies of this location or resource", "Proxy", "proxies")

        except EOFError:
            return 0

        # Now validate the record and save it
        if not record.guid:
            record.guid = str(uuid4())

        self.directory.addRecord(record)

        return 1

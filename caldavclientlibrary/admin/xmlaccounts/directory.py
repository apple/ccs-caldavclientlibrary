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

from caldavclientlibrary.admin.xmlaccounts import recordtypes
from caldavclientlibrary.admin.xmlaccounts import tags
from caldavclientlibrary.admin.xmlaccounts.record import XMLRecord

from xml.etree.ElementTree import Element

class XMLDirectory(object):
    """
    Model object for the XML-based directory. This can parse and generate the full XML file.
    """

    def __init__(self):
        self.realm = ""
        self.records = {}
        for type in recordtypes.RECORD_TYPES:
            self.records[type] = []


    def addRecord(self, record):
        """
        Add a new principal record to the directory.

        @param record: the record to add.
        @type record: L{admin.xmlaccounts.record.XMLRecord}
        """
        self.records[record.recordType].append(record)


    def containsRecord(self, recordType, uid):
        """
        Test whether the directory contains a record of the specified type and user id.

        @param recordType: a principal record type.
        @type recordType: one of L{admin.xmlaccounts.recordtypes.RECORD_TYPES}
        @param uid: the user id to check.
        @type uid: C{str}

        @return: C{True} if present in the directory, C{False} otherwise.
        @rtype: C{boolean}
        """
        for record in self.records[recordType]:
            if record.uid == uid:
                return True
        else:
            return False


    def containsGUID(self, guid):
        """
        Test whether the directory contains a record with the specified GUID.

        @param guid: the GUID to check.
        @type guid: C{str}

        @return: C{True} if present in the directory, C{False} otherwise.
        @rtype: C{boolean}
        """
        for type in recordtypes.RECORD_TYPES:
            for record in self.records[type]:
                if record.guid == guid:
                    return True
        return False


    def getRecord(self, recordType, uid):
        """
        Return the record in the directory with the matching record type and user id.

        @param recordType: a principal record type.
        @type recordType: one of L{admin.xmlaccounts.recordtypes.RECORD_TYPES}
        @param uid: the user id to check.
        @type uid: C{str}

        @return: the matching record, or C{None} if not found.
        @rtype: L{admin.xmlaccounts.record.XMLRecord}
        """
        for record in self.records[recordType]:
            if record.uid == uid:
                return record
        else:
            return None


    def removeRecord(self, recordType, uid):
        """
        Remove the record with the matching type and user id from the directory.

        @param recordType: a principal record type.
        @type recordType: one of L{admin.xmlaccounts.recordtypes.RECORD_TYPES}
        @param uid: the user id to remove.
        @type uid: C{str}

        @return: C{True} if found and removed, C{False} otherwise.
        @rtype: C{boolean}
        """
        for record in self.records[recordType]:
            if record.uid == uid:
                self.records[recordType].remove(record)
                return True
        else:
            return False


    def parseXML(self, node):
        """
        Parse an entire XML directory.

        @param node: the XML element for the root of the directory file.
        @type node: C{xml.etree.ElementTree.Element}
        """
        if node.tag == tags.ELEMENT_ACCOUNTS:
            self.realm = node.get(tags.ATTRIBUTE_REALM, "")

            for child in node.getchildren():
                record = XMLRecord()
                record.parseXML(child)
                self.records[record.recordType].append(record)

            # TODO: Now resolve group and proxy references


    def writeXML(self):
        """
        Generate an entire XML directory.

        @return: the root element for the principal record.
        @rtype: C{xml.etree.ElementTree.Element}
        """

        root = Element(tags.ELEMENT_ACCOUNTS)
        if self.realm:
            root.set(tags.ATTRIBUTE_REALM, self.realm)
        for type in recordtypes.RECORD_TYPES:
            self.writeXMLRecords(root, self.records[type])
        return root


    def writeXMLRecords(self, root, records):
        """
        Generate the XML for all records in the specified list.

        @param root: the XML root element for the directory.
        @type root: C{xml.etree.ElementTree.Element}
        @param records: a list of L{admin.xmlaccounts.record.XMLRecord} to process.
        @type records: C{list}
        """
        for record in records:
            root.append(record.writeXML())

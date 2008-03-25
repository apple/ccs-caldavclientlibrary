##
# Copyright (c) 2007-2008 Apple Inc. All rights reserved.
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

from admin.xmlaccounts import recordtypes
from admin.xmlaccounts import tags
from admin.xmlaccounts.record import XMLRecord

from xml.etree.ElementTree import Element

class XMLDirectory(object):
    
    def __init__(self):
        self.realm = ""
        self.records = {}
        for type in recordtypes.RECORD_TYPES:
            self.records[type] = []
    
    def addRecord(self, record):
        self.records[record.recordType].append(record)
        
    def containsRecord(self, recordType, uid):
        for record in self.records[recordType]:
            if record.uid == uid:
                return True
        else:
            return False
        
    def containsGUID(self, guid):
        for type in recordtypes.RECORD_TYPES:
            for record in self.records[type]:
                if record.guid == guid:
                    return True
        return False
        
    def getRecord(self, recordType, uid):
        for record in self.records[recordType]:
            if record.uid == uid:
                return record
        else:
            return None
        
    def removeRecord(self, recordType, uid):
        for record in self.records[recordType]:
            if record.uid == uid:
                self.records[recordType].remove(record)
                return True
        else:
            return False
        
    def parseXML(self, node):
        
        if node.tag == tags.ELEMENT_ACCOUNTS:
            self.realm = node.get(tags.ATTRIBUTE_REALM, "")

            for child in node.getchildren():
                record = XMLRecord()
                record.parseXML(child)
                self.records[record.recordType].append(record)
                
            # Now resolve group and proxy references
            

    def writeXML(self):
        root = Element(tags.ELEMENT_ACCOUNTS)
        if self.realm:
            root.set(tags.ATTRIBUTE_REALM, self.realm)
        for type in recordtypes.RECORD_TYPES:
            self.writeXMLRecords(root, self.records[type])
        return root

    def writeXMLRecords(self, root, records):
        for record in records:
            root.append(record.writeXML())

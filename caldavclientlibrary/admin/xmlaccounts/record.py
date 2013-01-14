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

from caldavclientlibrary.protocol.utils.xmlhelpers import SubElementWithData

from xml.etree.ElementTree import Element

class XMLRecord(object):
    """
    Represents a single principal record. This class can parse and generate the appropriate XML.
    """

    def __init__(self):
        self.recordType = None
        self.repeat = 0
        self.uid = None
        self.guid = None
        self.password = None
        self.name = None
        self.members = set()
        self.calendarUserAddresses = set()
        self.autoSchedule = False
        self.enabledForCalendaring = True
        self.proxies = set()
        self.proxyFor = set()


    def parseXML(self, node):
        """
        Parse a single principal record from XML.

        @param node: the XML element for the principal being parsed.
        @type node: C{xml.etree.ElementTree.Element}
        """
        self.recordType = recordtypes.TAGS_TO_RECORD_TYPES[node.tag]
        self.repeat = int(node.get(tags.ATTRIBUTE_REPEAT, "0"))
        for child in node.getchildren():
            if child.tag == tags.ELEMENT_UID:
                self.uid = child.text
            elif child.tag == tags.ELEMENT_GUID:
                self.guid = child.text
            elif child.tag == tags.ELEMENT_PASSWORD:
                self.password = child.text
            elif child.tag == tags.ELEMENT_NAME:
                self.name = child.text
            elif child.tag == tags.ELEMENT_MEMBERS:
                self._parseMembers(child, self.members)
            elif child.tag == tags.ELEMENT_CUADDR:
                self.calendarUserAddresses.add(child.text)
            elif child.tag == tags.ELEMENT_AUTOSCHEDULE:
                # Only Resources & Locations
                if self.recordType not in (recordtypes.recordType_resources, recordtypes.recordType_locations,):
                    raise ValueError("<auto-schedule> element only allowed for Resources and Locations: %s" % (child.tag,))
                self.autoSchedule = True
            elif child.tag == tags.ELEMENT_DISABLECALENDAR:
                # Only Groups
                if self.recordType not in (recordtypes.recordType_users, recordtypes.recordType_groups,):
                    raise ValueError("<disable-calendar> element only allowed for Groups: %s" % (child.tag,))
                self.enabledForCalendaring = False
            elif child.tag == tags.ELEMENT_PROXIES:
                # Only Resources & Locations
                if self.recordType not in (recordtypes.recordType_resources, recordtypes.recordType_locations,):
                    raise ValueError("<proxies> element only allowed for Resources and Locations: %s" % (child.tag,))
                self._parseMembers(child, self.proxies)
            else:
                raise RuntimeError("Unknown account attribute: %s" % (child.tag,))


    def _parseMembers(self, node, addto):
        """
        Parse an XML <members> or <proxies> element list.

        @param node: the <members> or <proxies> element to parse.
        @type node: C{xml.etree.ElementTree.Element}
        @param addto: the list to add the parsed information into. The items in the list are tuples
            of the record type and record uid.
        @type addto: C{list}
        """
        for child in node.getchildren():
            if child.tag == tags.ELEMENT_MEMBER:
                recordType = child.get(tags.ATTRIBUTE_RECORDTYPE, recordtypes.recordType_users)
                addto.add((recordType, child.text))


    def writeXML(self):
        """
        Generate a single XML principal record element.

        @return: the root element for the principal record.
        @rtype: C{xml.etree.ElementTree.Element}
        """

        root = Element(recordtypes.RECORD_TYPES_TO_TAGS[self.recordType])
        if self.repeat:
            root.set(tags.ATTRIBUTE_REPEAT, str(self.repeat))

        SubElementWithData(root, tags.ELEMENT_UID, self.uid)
        SubElementWithData(root, tags.ELEMENT_GUID, self.guid)
        SubElementWithData(root, tags.ELEMENT_PASSWORD, self.password)
        SubElementWithData(root, tags.ELEMENT_NAME, self.name)
        if self.recordType == recordtypes.recordType_groups:
            members = SubElementWithData(root, tags.ELEMENT_MEMBERS)
            for member in self.members:
                SubElementWithData(members, tags.ELEMENT_MEMBER, member[1], {tags.ATTRIBUTE_RECORDTYPE: member[0]})
        if self.calendarUserAddresses:
            for cuaddr in self.calendarUserAddresses:
                SubElementWithData(root, tags.ELEMENT_CUADDR, cuaddr)
        if self.recordType in (recordtypes.recordType_resources, recordtypes.recordType_locations,) and self.autoSchedule:
            SubElementWithData(root, tags.ELEMENT_AUTOSCHEDULE)
        if self.recordType in (recordtypes.recordType_users, recordtypes.recordType_groups,) and not self.enabledForCalendaring:
            SubElementWithData(root, tags.ELEMENT_DISABLECALENDAR)
        if self.recordType in (recordtypes.recordType_resources, recordtypes.recordType_locations,):
            proxies = SubElementWithData(root, tags.ELEMENT_PROXIES)
            for proxy in self.proxies:
                SubElementWithData(proxies, tags.ELEMENT_MEMBER, proxy[1], {tags.ATTRIBUTE_RECORDTYPE: proxy[0]})

        return root

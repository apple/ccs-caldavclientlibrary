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

from StringIO import StringIO
from caldavclientlibrary.admin.xmlaccounts.record import XMLRecord
from caldavclientlibrary.protocol.utils.xmlhelpers import BetterElementTree
from xml.etree.ElementTree import XML

import unittest

class TestRecord(unittest.TestCase):

    def checkXML(self, x):

        x = x.replace("\n", "\r\n")

        # Parse the XML data
        a = XMLRecord()
        a.parseXML(XML(x))

        # Generate the XML data
        node = a.writeXML()
        os = StringIO()
        xmldoc = BetterElementTree(node)
        xmldoc.writeUTF8(os)

        # Verify data
        self.assertEqual(os.getvalue(), x)


    def test_user(self):

        self.checkXML("""<?xml version='1.0' encoding='utf-8'?>
<user>
  <uid>test</uid>
  <guid />
  <password>test</password>
  <name>Test User</name>
  <cuaddr>mailto:testuser@example.com</cuaddr>
</user>
""")


    def test_group(self):

        self.checkXML("""<?xml version='1.0' encoding='utf-8'?>
<group>
  <uid>users</uid>
  <guid>12345</guid>
  <password>users</password>
  <name>Users Group</name>
  <members>
    <member type="users">test</member>
  </members>
</group>
""")


    def test_location(self):

        self.checkXML("""<?xml version='1.0' encoding='utf-8'?>
<location>
  <uid>mercury</uid>
  <guid>12345</guid>
  <password>mercury</password>
  <name>Mecury Conference Room, Building 1, 2nd Floor</name>
  <auto-schedule />
  <proxies>
    <member type="users">test</member>
  </proxies>
</location>
""")

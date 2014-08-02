##
# Copyright (c) 2006-2013 Apple Inc. All rights reserved.
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

from caldavclientlibrary.protocol.webdav.session import Session
from caldavclientlibrary.protocol.carddav.makeaddressbook import MakeAddressBook
from StringIO import StringIO
import unittest

class TestRequest(unittest.TestCase):


    def test_Method(self):

        server = Session("www.example.com")
        request = MakeAddressBook(server, "/")
        self.assertEqual(request.getMethod(), "MKCOL")



class TestRequestHeaders(unittest.TestCase):
    pass



class TestRequestBody(unittest.TestCase):

    def test_GenerateXMLDisplayname(self):

        server = Session("www.example.com")
        request = MakeAddressBook(server, "/", "home")
        os = StringIO()
        request.generateXML(os)
        self.assertEqual(
            os.getvalue(), """<?xml version='1.0' encoding='utf-8'?>
<ns0:mkcol xmlns:ns0="DAV:">
  <ns0:set>
    <ns0:prop>
      <ns0:resourcetype>
        <ns0:collection />
        <ns1:addressbook xmlns:ns1="urn:ietf:params:xml:ns:carddav" />
      </ns0:resourcetype>
      <ns0:displayname>home</ns0:displayname>
    </ns0:prop>
  </ns0:set>
</ns0:mkcol>
""".replace("\n", "\r\n")
        )


    def test_GenerateXMLMultipleProperties(self):

        server = Session("www.example.com")
        request = MakeAddressBook(server, "/", "home", "my personal address book")
        os = StringIO()
        request.generateXML(os)
        self.assertEqual(
            os.getvalue(), """<?xml version='1.0' encoding='utf-8'?>
<ns0:mkcol xmlns:ns0="DAV:">
  <ns0:set>
    <ns0:prop>
      <ns0:resourcetype>
        <ns0:collection />
        <ns1:addressbook xmlns:ns1="urn:ietf:params:xml:ns:carddav" />
      </ns0:resourcetype>
      <ns0:displayname>home</ns0:displayname>
      <ns1:addressbook-description xmlns:ns1="urn:ietf:params:xml:ns:carddav">my personal address book</ns1:addressbook-description>
    </ns0:prop>
  </ns0:set>
</ns0:mkcol>
""".replace("\n", "\r\n")
        )



class TestResponse(unittest.TestCase):
    pass



class TestResponseHeaders(unittest.TestCase):
    pass



class TestResponseBody(unittest.TestCase):
    pass

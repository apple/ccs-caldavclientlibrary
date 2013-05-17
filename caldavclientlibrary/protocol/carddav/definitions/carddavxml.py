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

from xml.etree.ElementTree import QName

CardDAVNamespace = "urn:ietf:params:xml:ns:carddav"

# RFC 6352


addressbook_description = QName(CardDAVNamespace, "addressbook-description")
supported_addressbook_data = QName(CardDAVNamespace, "supported-addressbook-data")
address_data_type = QName(CardDAVNamespace, "address-data-type")
max_resource_size = QName(CardDAVNamespace, "max-resource-size")

addressbook_home_set = QName(CardDAVNamespace, "addressbook-home-set")

supported_collation_set = QName(CardDAVNamespace, "supported-collation-set")

addressbook = QName(CardDAVNamespace, "addressbook")
supported_collation = QName(CardDAVNamespace, "supported-collation")

addressbook_query = QName(CardDAVNamespace, "addressbook-query")
address_data = QName(CardDAVNamespace, "address-data")
allprop = QName(CardDAVNamespace, "allprop")
prop = QName(CardDAVNamespace, "prop")
filter = QName(CardDAVNamespace, "filter")
prop_filter = QName(CardDAVNamespace, "prop-filter")
param_filter = QName(CardDAVNamespace, "param-filter")
is_not_defined = QName(CardDAVNamespace, "is-not-defined")
text_match = QName(CardDAVNamespace, "text-match")
limit = QName(CardDAVNamespace, "limit")
nresults = QName(CardDAVNamespace, "nresults")

addressbook_multiget = QName(CardDAVNamespace, "addressbook-multiget")

default_addressbook_url = QName(CardDAVNamespace, "default-addressbook-URL")

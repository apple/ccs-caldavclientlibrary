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

from protocol.webdav.propfindparser import PropFindParser
from protocol.webdav.definitions import davxml

PropFindParser.textProperties.add(davxml.creationdate)
PropFindParser.textProperties.add(davxml.displayname)
PropFindParser.textProperties.add(davxml.getcontentlanguage)
PropFindParser.textProperties.add(davxml.getcontentlength)
PropFindParser.textProperties.add(davxml.getcontenttype)
PropFindParser.textProperties.add(davxml.getetag)
PropFindParser.textProperties.add(davxml.getlastmodified)

PropFindParser.hrefListProperties.add(davxml.principal_collection_set)
PropFindParser.hrefProperties.add(davxml.principal_URL)
PropFindParser.hrefListProperties.add(davxml.alternate_URI_set)
PropFindParser.hrefListProperties.add(davxml.group_member_set)
PropFindParser.hrefListProperties.add(davxml.group_membership)

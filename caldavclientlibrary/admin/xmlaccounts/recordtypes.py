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

"""
Defines the record type identifiers and various dict's to map between those and XML elements.
"""

from caldavclientlibrary.admin.xmlaccounts import tags

recordType_users = "users"
recordType_groups = "groups"
recordType_locations = "locations"
recordType_resources = "resources"
recordType_all = "all"

RECORD_TYPES = (
    recordType_users,
    recordType_groups,
    recordType_locations,
    recordType_resources,
)
"""Allowed record type identifiers."""

RECORD_TYPES_TO_TAGS = {
    recordType_users     : tags.ELEMENT_USER,
    recordType_groups    : tags.ELEMENT_GROUP,
    recordType_locations : tags.ELEMENT_LOCATION,
    recordType_resources : tags.ELEMENT_RESOURCE,
}
"""Maps between record type identifiers and their corresponding XML element names."""

TAGS_TO_RECORD_TYPES = {
    tags.ELEMENT_USER     : recordType_users,
    tags.ELEMENT_GROUP    : recordType_groups,
    tags.ELEMENT_LOCATION : recordType_locations,
    tags.ELEMENT_RESOURCE : recordType_resources,
}
"""Maps between XML element names and their corresponding record type identifiers."""

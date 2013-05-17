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

CSNamespace = "http://calendarserver.org/ns/"

calendar_proxy_read_for = QName(CSNamespace, "calendar-proxy-read-for")
calendar_proxy_write_for = QName(CSNamespace, "calendar-proxy-write-for")
getctag = QName(CSNamespace, "getctag")

notification = QName(CSNamespace, "notification")
notification_URL = QName(CSNamespace, "notification-URL")

# Are these really in this namespace?
dropbox_home = QName(CSNamespace, "dropbox-home")
dropbox_home_URL = QName(CSNamespace, "dropbox-home-URL")

# Defined by caldav-pubsubdiscovery
xmpp_server = QName(CSNamespace, "xmpp-server")
xmpp_uri = QName(CSNamespace, "xmpp-uri")
pushkey = QName(CSNamespace, "pushkey")

# Sharing
invite = QName(CSNamespace, "invite")
organizer = QName(CSNamespace, "organizer")
user = QName(CSNamespace, "user")
common_name = QName(CSNamespace, "common-name")
first_name = QName(CSNamespace, "first-name")
last_name = QName(CSNamespace, "last-name")

invite_noresponse = QName(CSNamespace, "invite-noresponse")
invite_accepted = QName(CSNamespace, "invite-accepted")
invite_declined = QName(CSNamespace, "invite-declined")
invite_invalid = QName(CSNamespace, "invite-invalid")

access = QName(CSNamespace, "access")
read = QName(CSNamespace, "read")
summary = QName(CSNamespace, "summary")

read_write = QName(CSNamespace, "read-write")

share = QName(CSNamespace, "share")
set = QName(CSNamespace, "set")
remove = QName(CSNamespace, "remove")

notification_URL = QName(CSNamespace, "notification-URL")
notification = QName(CSNamespace, "notification")
dtstamp = QName(CSNamespace, "dtstamp")
invite_notification = QName(CSNamespace, "invite-notification")
invite_reply = QName(CSNamespace, "invite-reply")
uid = QName(CSNamespace, "uid")
hosturl = QName(CSNamespace, "hosturl")
in_reply_to = QName(CSNamespace, "in-reply-to")

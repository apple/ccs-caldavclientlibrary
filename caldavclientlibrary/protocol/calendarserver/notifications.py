##
# Copyright (c) 2013 Apple Inc. All rights reserved.
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
from caldavclientlibrary.protocol.caldav.definitions import csxml
from caldavclientlibrary.protocol.webdav.definitions import davxml
from caldavclientlibrary.protocol.webdav.post import Post
from caldavclientlibrary.protocol.http.data.string import RequestDataString
from xml.etree.ElementTree import Element, SubElement
from caldavclientlibrary.protocol.utils.xmlhelpers import BetterElementTree


def userNameFromNode(node):
    cn = node.find(str(csxml.common_name))
    first = node.find(str(csxml.first_name))
    last = node.find(str(csxml.last_name))

    return cn.text if cn is not None else ("%s %s" % (first.text, last.text) if first is not None or last is not None else "")



class InviteNotification(object):
    """
    An invite notification sent to sharees.
    """

    def __init__(self):

        self.url = None
        self.shared_type = "calendar"
        self.uid = ""
        self.user_uid = ""
        self.access = "unknown"
        self.hosturl = ""
        self.organizer_uid = None
        self.organizer_cn = None
        self.summary = "-"


    def parseFromNotification(self, url, notification):

        self.url = url

        self.shared_type = notification.get("shared-type", default="calendar")
        self.uid = notification.find(str(csxml.uid)).text
        self.user_uid = notification.find(str(davxml.href)).text

        access = notification.find(str(csxml.access))
        if access.find(str(csxml.read)) is not None:
            self.access = "read"
        elif access.find(str(csxml.read_write)) is not None:
            self.access = "read-write"

        hosturl = notification.find(str(csxml.hosturl))
        if hosturl is not None:
            self.hosturl = hosturl.find(str(davxml.href)).text

        organizer = notification.find(str(csxml.organizer))
        if organizer is not None:
            self.organizer_uid = organizer.find(str(davxml.href)).text
            self.organizer_cn = userNameFromNode(organizer)

        summary = notification.find(str(csxml.summary))
        if summary is not None:
            self.summary = summary.text

        return self



class InviteReply(object):
    """
    An invite reply sent to the sharer.
    """

    def __init__(self):

        self.url = None
        self.user_uid = ""
        self.mode = "unknown"
        self.hosturl = ""
        self.in_reply_to = ""
        self.summary = "-"


    def parseFromNotification(self, url, notification):

        self.url = url

        self.user_uid = notification.find(str(davxml.href)).text

        if notification.find(str(csxml.invite_accepted)) is not None:
            self.mode = "accepted"
        elif notification.find(str(csxml.invite_declined)) is not None:
            self.mode = "declined"

        hosturl = notification.find(str(csxml.hosturl))
        if hosturl is not None:
            self.hosturl = hosturl.find(str(davxml.href)).text

        in_reply_to = notification.find(str(csxml.in_reply_to))
        if in_reply_to is not None:
            self.in_reply_to = in_reply_to.text

        summary = notification.find(str(csxml.summary))
        if summary is not None:
            self.summary = summary.text

        return self



class ProcessNotification(Post):
    """
    HTTP POST request to accept or decline a sharee's invite notification.
    """

    def __init__(self, session, url, notification, accepted):
        super(ProcessNotification, self).__init__(session, url)
        self.notification = notification
        self.accepted = accepted

        self.initRequestData()


    def initRequestData(self):
        # Write XML info to a string
        os = StringIO()
        self.generateXML(os)
        self.request_data = RequestDataString(os.getvalue(), "text/xml;charset=utf-8")


    def generateXML(self, os):
        # Structure of document is:
        #
        # <CS:invite-reply>
        #   <DAV:href>...</DAV:href>
        #   <CS:invite-accepted /> | <CS:invite-declined />
        #   <CS:hosturl>...</CS:hosturl>
        #   <CS:in-reply-to>...</CS:in-reply-to>
        # </CS:invite-reply>

        # <CS:invite-reply> element
        invite_reply = Element(csxml.invite_reply)

        # <DAV:href> element
        href = SubElement(invite_reply, davxml.href)
        href.text = self.notification.user_uid

        # <CS:invite-accepted /> | <CS:invite-declined />
        SubElement(invite_reply, csxml.invite_accepted if self.accepted else csxml.invite_declined)

        # <CS:hosturl> element
        hosturl = SubElement(invite_reply, csxml.hosturl)

        # <DAV:href> element
        href = SubElement(hosturl, davxml.href)
        href.text = self.notification.hosturl

        # <CS:in-reply-to> element
        in_reply_to = SubElement(invite_reply, csxml.in_reply_to)
        in_reply_to.text = self.notification.uid

        # Now we have the complete document, so write it out (no indentation)
        xmldoc = BetterElementTree(invite_reply)
        xmldoc.writeUTF8(os)

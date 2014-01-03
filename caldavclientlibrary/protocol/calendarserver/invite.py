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



class Invites(object):
    """
    Represents a list of invites to sharees for a shared resource.
    """

    def __init__(self):

        self.organizer_uid = None
        self.organizer_cn = ""
        self.invitees = []


    def parseFromInvite(self, invite):

        if invite is not None and len(invite) != 0:
            organizer = invite.find(str(csxml.organizer))
            if organizer is not None:
                self.organizer_uid = organizer.find(str(davxml.href)).text
                self.organizer_cn = userNameFromNode(organizer)

            for user in invite.findall(str(csxml.user)):
                self.invitees.append(InviteUser().parseFromUser(user))

        return self



class InviteUser(object):
    """
    An invite for a specific sharee.
    """

    def __init__(self):

        self.user_uid = None
        self.user_cn = ""
        self.mode = "unknown"
        self.access = "unknown"
        self.summary = "-"


    def parseFromUser(self, user):

        self.user_uid = user.find(str(davxml.href)).text
        self.user_cn = userNameFromNode(user)
        if user.find(str(csxml.invite_noresponse)) is not None:
            self.mode = "no-response"
        elif user.find(str(csxml.invite_accepted)) is not None:
            self.mode = "accepted"
        elif user.find(str(csxml.invite_declined)) is not None:
            self.mode = "declined"
        elif user.find(str(csxml.invite_invalid)) is not None:
            self.mode = "invalid"

        access = user.find(str(csxml.access))
        if access.find(str(csxml.read)) is not None:
            self.access = "read"
        elif access.find(str(csxml.read_write)) is not None:
            self.access = "read-write"

        summary = user.find(str(csxml.summary))
        if summary is not None:
            self.summary = summary.text

        return self



class AddInvitees(Post):
    """
    HTTP POST request to add an invite for a sharee.
    """

    def __init__(self, session, url, user_uids, read_write, summary=None):
        super(AddInvitees, self).__init__(session, url)
        self.user_uids = user_uids
        self.read_write = read_write
        self.summary = summary if summary is not None else "-"

        self.initRequestData()


    def initRequestData(self):
        # Write XML info to a string
        os = StringIO()
        self.generateXML(os)
        self.request_data = RequestDataString(os.getvalue(), "text/xml;charset=utf-8")


    def generateXML(self, os):
        # Structure of document is:
        #
        # <CS:share>
        #   <CS:set>
        #     <DAV:href>...</DAV:href>
        #     <CS:summary>...</CS:summary>
        #     <CS:read /> | <CS:read-write />
        #   </CS:set>
        #   <CS:set>
        #     <DAV:href>...</DAV:href>
        #     <CS:summary>...</CS:summary>
        #     <CS:read /> | <CS:read-write />
        #   </CS:set>
        #   ...
        # </CS:share>

        # <CS:share> element
        share = Element(csxml.share)

        for user_uid in self.user_uids:
            # <CS:set> element
            set = SubElement(share, csxml.set)

            # <DAV:href> element
            href = SubElement(set, davxml.href)
            href.text = user_uid

            # <CS:summary> element
            summary = SubElement(set, csxml.summary)
            summary.text = self.summary

            # <CS:read /> | <CS:read-write />
            SubElement(set, csxml.read_write if self.read_write else csxml.read)

        # Now we have the complete document, so write it out (no indentation)
        xmldoc = BetterElementTree(share)
        xmldoc.writeUTF8(os)



class RemoveInvitee(Post):
    """
    HTTP POST request to remove an invite for a sharee.
    """

    def __init__(self, session, url, invitee):
        super(RemoveInvitee, self).__init__(session, url)
        self.invitee = invitee

        self.initRequestData()


    def initRequestData(self):
        # Write XML info to a string
        os = StringIO()
        self.generateXML(os)
        self.request_data = RequestDataString(os.getvalue(), "text/xml;charset=utf-8")


    def generateXML(self, os):
        # Structure of document is:
        #
        # <CS:share>
        #   <CS:remove>
        #     <DAV:href>...</DAV:href>
        #   </CS:remove>
        # </CS:share>

        # <CS:share> element
        share = Element(csxml.share)

        # <CS:remove> element
        remove = SubElement(share, csxml.remove)

        # <DAV:href> element
        href = SubElement(remove, davxml.href)
        href.text = self.invitee.user_uid

        # Now we have the complete document, so write it out (no indentation)
        xmldoc = BetterElementTree(share)
        xmldoc.writeUTF8(os)

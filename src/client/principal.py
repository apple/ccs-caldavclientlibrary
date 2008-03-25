##
# Copyright (c) 2006-2007 Apple Inc. All rights reserved.
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

from protocol.caldav.definitions import caldavxml
from client.calendar import Calendar
from protocol.url import URL
from protocol.webdav.definitions import davxml
from protocol.caldav.definitions import headers
import types


class PrincipalCache(object):
    
    def __init__(self):
        self.cache = {}
        
    def getPrincipal(self, session, path, refresh=False):
        if path.toString() not in self.cache:
            principal = CalDAVPrincipal(session, path)
            principal.loadDetails()
            self.cache[path.toString()] = principal
            self.cache[principal.principalURL.toString()] = principal
            for uri in principal.alternateURIs:
                self.cache[uri.toString()] = principal
        elif refresh:
            self.cache[path.toString()].loadDetails(refresh=True)
        return self.cache[path.toString()]

principalCache = PrincipalCache()

class CalDAVPrincipal(object):
    
    def __init__(self, session, path):
        
        self.session = session
        self.principalPath = path
        self._initFields()

    def __str__(self):
        return """
    Principal Path    : %s
    Display Name      : %s
    Principal URL     : %s
    Alternate URLs    : %s
    Group Members     : %s
    Memberships       : %s
    Calendar Homes    : %s
    Outbox URL        : %s
    Inbox URL         : %s
    Calendar Addresses: %s
""" % (
          self.principalPath,
          self.displayname,
          self.principalURL,
          self.alternateURIs,
          self.memberset,
          self.memberships,
          self.homeset,
          self.outboxURL,
          self.inboxURL,
          self.cuaddrs
      )

    def _initFields(self):
        self.loaded = False
        self.valid = False
        self.displayname = "Invalid Principal"
        self.principalURL = ""
        self.alternateURIs = ()
        self.memberset = ()
        self.memberships = ()
        self.homeset = ()
        self.outboxURL = ""
        self.inboxURL = ""
        self.cuaddrs = ()
        
        self.proxyFor = None
        self.proxyreadURL = ""
        self.proxywriteURL = ""
        
    def loadDetails(self, refresh=False):
        if self.loaded and not refresh:
            return
        self._initFields()

        results, _ignore_bad = self.session.getProperties(
            self.principalPath,
            (
                davxml.resourcetype,
                davxml.displayname,
                davxml.principal_URL,
                davxml.alternate_URI_set,
                davxml.group_member_set,
                davxml.group_membership,
                caldavxml.calendar_home_set,
                caldavxml.schedule_outbox_URL,
                caldavxml.schedule_inbox_URL,
                caldavxml.calendar_user_address_set,
            ),
        )
        if results:
            # First check that we have a valid principal and see if its a proxy principal too
            type = results.get(davxml.resourcetype, None)
            self.valid = type.find(str(davxml.principal)) is not None
            if (self.session.hasDAVVersion(headers.calendar_proxy) and
                (type.find(str(caldavxml.calendar_proxy_read)) is not None or
                 type.find(str(caldavxml.calendar_proxy_write)) is not None)):
                parentPath = self.principalPath.dirname()
                self.proxyFor = principalCache.getPrincipal(self.session, parentPath, refresh)
                
            if self.valid:
                self.displayname = results.get(davxml.displayname, None)
                self.principalURL = results.get(davxml.principal_URL, None)
                self.alternateURIs = results.get(davxml.alternate_URI_set, None)
                self.memberset = results.get(davxml.group_member_set, None)
                self.memberships = results.get(davxml.group_membership, None)
                self.homeset = results.get(caldavxml.calendar_home_set, None)
                self.outboxURL = results.get(caldavxml.schedule_outbox_URL, None)
                self.inboxURL = results.get(caldavxml.schedule_inbox_URL, None)
                self.cuaddrs = results.get(caldavxml.calendar_user_address_set, None)

        # Get proxy resource details if proxy support is available
        if self.session.hasDAVVersion(headers.calendar_proxy) and not self.proxyFor:
            results = self.session.getPropertiesOnHierarchy(self.principalPath, (davxml.resourcetype,))
            for path, items in results.iteritems():
                if davxml.resourcetype in items:
                    rtype = items[davxml.resourcetype]
                    if rtype.find(str(caldavxml.calendar_proxy_read)) is not None:
                        self.proxyreadURL = URL(url=path)
                    elif rtype.find(str(caldavxml.calendar_proxy_write)) is not None:
                        self.proxywriteURL = URL(url=path)
                        
        self.loaded = True

    def getSmartDisplayName(self):
        if self.proxyFor:
            return "%s#%s" % (self.proxyFor.displayname, self.displayname,)
        else:
            return self.displayname

    def listCalendars(self, root=None):
        calendars = []
        home = self.homeset[0] if type(self.homeset) in (types.TupleType,) else self.homeset
        if not home.path.endswith("/"):
            home.path += "/"

        results = self.session.getPropertiesOnHierarchy(home, (davxml.resourcetype,))
        for path, items in results.iteritems():
            if davxml.resourcetype in items:
                rtype = items[davxml.resourcetype]
                if rtype.find(str(davxml.collection)) is not None and rtype.find(str(caldavxml.calendar)) is not None:
                    calendars.append(Calendar(path=path, session=self.session))
        return calendars

    def listFreeBusySet(self):
        return self._getFreeBusySet()
    
    def addToFreeBusySet(self, calendars):
        current = self._getFreeBusySet()
        for calendar in calendars:
            current.append(calendar)
        self._setFreeBusySet(current)
    
    def removeFromFreeBusySet(self, calendars):
        calendar_paths = [calendar.path for calendar in calendars]
        current = self._getFreeBusySet()
        current = [cal for cal in current if cal.path not in calendar_paths]
        self._setFreeBusySet(current)

    def cleanFreeBusySet(self):
        fbset = self.listFreeBusySet()
        badfbset = []
        for calendar in fbset:
            if not calendar.exists():
                badfbset.append(calendar)
    
        if badfbset:
            self.removeFromFreeBusySet(badfbset)

    def _getFreeBusySet(self):
        hrefs = self.session.getHrefListProperty(self.inboxURL, caldavxml.calendar_free_busy_set)
        return [Calendar(href.relativeURL(), session=self.session) for href in hrefs]
    
    def _setFreeBusySet(self, calendars):
        hrefs = [URL(url=calendar.path) for calendar in calendars]
        self.session.setProperties(self.inboxURL, ((caldavxml.calendar_free_busy_set, hrefs),))

    def getReadProxies(self, refresh=True):
        if not self.proxyreadURL:
            return ()
        
        principal = principalCache.getPrincipal(self.session, self.proxyreadURL, refresh=refresh)
        return [principalCache.getPrincipal(self.session, member) for member in principal.memberset]
            
    
    def setReadProxies(self, principals):
        if not self.proxyreadURL:
            return ()
        
        self.session.setProperties(self.proxyreadURL, ((davxml.group_member_set, principals),))            
    
    def getWriteProxies(self, refresh=True):
        if not self.proxywriteURL:
            return ()
        
        principal = principalCache.getPrincipal(self.session, self.proxywriteURL, refresh=refresh)
        return [principalCache.getPrincipal(self.session, member) for member in principal.memberset]

    def setWriteProxies(self, principals):
        if not self.proxywriteURL:
            return ()
        
        self.session.setProperties(self.proxywriteURL, ((davxml.group_member_set, principals),))            
    

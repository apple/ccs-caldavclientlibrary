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

from caldavclientlibrary.protocol.url import URL
from caldavclientlibrary.protocol.webdav.definitions import davxml
import os

class Resource(object):
    """
    Maintains data for a WebDAV resource, including list of properties,
    child resources and actual data.
    """

    def __init__(self, session, path, lastmod="", size="", type=""):

        self.session = session
        self.path = path.rstrip("/")
        self.iscollection = path.endswith("/")
        self.lastmod = lastmod
        self.size = size
        self.type = type
        self.children = None
        self.details = None
        self.data = None


    def getPath(self):
        return self.path


    def getName(self):
        return os.path.basename(self.path)


    def getLastMod(self):
        return self.lastmod


    def getSize(self):
        return self.size


    def getType(self):
        return self.type


    def isCollection(self):
        return self.iscollection


    def findPath(self, path=None, elements=None):
        if path:
            elements = path.lstrip("/").rstrip("/").split("/")
        if self.listChildren():
            for child in self.children:
                if child.getName() == elements[0]:
                    elements = elements[1:]
                    if elements:
                        return child.findPath(elements=elements)
                    else:
                        return child
        return None


    def findChild(self, name):
        if self.children:
            for child in self.children:
                if child.getName() == name:
                    return child
        return None


    def listChildren(self):
        if self.children is None:
            resource = URL(url=self.path + "/")
            props = (
                davxml.resourcetype,
                davxml.getlastmodified,
                davxml.getcontentlength,
                davxml.getcontenttype,
            )
            results = self.session.account.session.getPropertiesOnHierarchy(resource, props)
            items = results.keys()
            items.sort()
            self.children = [Resource(
                self.session,
                rurl,
                lastmod=results[rurl].get(davxml.getlastmodified, ""),
                size=results[rurl].get(davxml.getcontentlength, ""),
                type=results[rurl].get(davxml.getcontenttype, ""),
            ) for rurl in items if rurl != self.path + "/"]
        return self.children


    def getDetails(self):
        resource = URL(url=self.path + "/")
        props = (davxml.resourcetype,)
        props += (davxml.getcontentlength, davxml.getlastmodified,)
        props, _ignore_bad = self.session.account.session.getProperties(resource, props)
        size = props.get(davxml.getcontentlength, "-")
        if not size:
            size = "0"
        modtime = props.get(davxml.getlastmodified, "-")
        return ["Size: %s" % (size,), "Modtime: %s" % (modtime,)]


    def getAllDetails(self):
        if self.details is None:
            resource = URL(url=self.path + "/")
            props = self.session.account.session.getPropertyNames(resource)
            results, _ignore_bad = self.session.account.session.getProperties(resource, props)
            sorted = results.keys()
            sorted.sort()
            self.details = [(key, results[key],) for key in sorted]
        return self.details


    def getData(self):
        if self.data is None:
            resource = URL(url=self.path + "/")
            self.data, _ignore_etag = self.session.account.session.readData(resource)
        return self.data


    def getDataAsHTML(self):
        data = self.getData()
        if not self.type.startswith("text/html"):
            data = "<HTML><BODY>%s</BODY></HTML>" % (data.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>\n"),)
        return data


    def clear(self):
        self.children = None
        self.details = None
        self.data = None

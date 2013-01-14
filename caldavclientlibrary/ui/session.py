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

from caldavclientlibrary.client.account import CalDAVAccount
from caldavclientlibrary.ui.resource import Resource

class Session(object):
    """
    Maintains the basic information for a session and the root resource.
    """

    def __init__(self, server, path, user, pswd, logging):

        self.server = server
        self.path = path
        self.user = user
        self.pswd = pswd

        # Create the account
        ssl = server.startswith("https://")
        server = server[8:] if ssl else server[7:]
        paths = "/principals/users/%s/" % (self.user,)
        self.account = CalDAVAccount(server, ssl=ssl, user=self.user, pswd=self.pswd, root=paths, principal=paths, logging=logging)


    def getRoot(self):
        return Resource(self, self.path)

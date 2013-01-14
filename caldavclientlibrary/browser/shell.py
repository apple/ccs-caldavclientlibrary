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

from caldavclientlibrary.browser.baseshell import BaseShell
from caldavclientlibrary.browser.command import Command
from caldavclientlibrary.client.account import CalDAVAccount
from getpass import getpass
from caldavclientlibrary.protocol.url import URL
import caldavclientlibrary.browser.commands
import atexit
import getopt
import sys
import urlparse

class Shell(BaseShell):

    def __init__(self, server, path, user, pswd, logging):

        super(Shell, self).__init__("caldav_client")
        self.prefix = self.wd = "/"
        self.server = server
        self.user = user
        self.pswd = pswd

        self.registerCommands()

        # Create the account
        ssl = server.startswith("https://")
        server = server[8:] if ssl else server[7:]
        self.account = CalDAVAccount(server, ssl=ssl, user=self.user, pswd=self.pswd, root=path, principal=None, logging=logging)

        atexit.register(self.saveHistory)


    def registerCommands(self):
        module = caldavclientlibrary.browser.commands
        for item in module.__all__:
            mod = __import__("caldavclientlibrary.browser.commands." + item, globals(), locals(), ["Cmd", ])
            cmd_class = mod.Cmd
            if type(cmd_class) is type and issubclass(cmd_class, Command):
                self.registerCommand(cmd_class())


    def setWD(self, newwd):

        # Check that the new one exists
        resource = (newwd if newwd.endswith("/") else newwd + "/")
        if not self.account.session.testResource(URL(url=resource)):
            return False
        self.prefix = self.wd = newwd
        return True


    def setUserPswd(self, user, pswd):

        self.user = user
        self.pswd = pswd
        self.account.setUserPswd(user, pswd)



def usage():
    return """Usage: shell [OPTIONS]

Options:
-l              start with HTTP logging on.
--server=HOST   url of the server include http/https scheme and port [REQUIRED].
--user=USER     user name to login as - will be prompted if not prsent [OPTIONAL].
--pswd=PSWD     password for user - will be prompted if not prsent [OPTIONAL].
"""



def runit():
    logging = False
    server = None
    user = None
    pswd = None

    opts, _ignore_args = getopt.getopt(sys.argv[1:], 'lh', ["help", "server=", "user=", "pswd="])

    for name, value in opts:

        if name == "-l":
            logging = True
        elif name == "--server":
            server = value
        elif name == "--user":
            user = value
        elif name == "--pswd":
            pswd = value
        else:
            print usage()
            raise SystemExit()

    if not server or not (server.startswith("http://") or server.startswith("https://")):
        print usage()
        raise SystemExit()
    splits = urlparse.urlsplit(server)
    server = splits.scheme + "://" + splits.netloc
    path = splits.path
    if not path:
        path = "/"

    if not user:
        user = raw_input("User: ")
    if not pswd:
        pswd = getpass("Password: ")

    shell = Shell(server, path, user, pswd, logging)
    shell.run()


if __name__ == '__main__':

    runit()

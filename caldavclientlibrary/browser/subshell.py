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

from caldavclientlibrary.browser.command import Command
from caldavclientlibrary.browser.baseshell import BaseShell

class SubShell(BaseShell):

    def __init__(self, shell, prefix, cmds):

        super(SubShell, self).__init__("caldav_client.%s" % (prefix,))
        self.shell = shell
        self.prefix = prefix
        self.preserve_history = True
        self.registerCommands(cmds)


    def registerCommands(self, cmds):
        for cmd in cmds:
            if isinstance(cmd, Command):
                self.registerCommand(cmd)

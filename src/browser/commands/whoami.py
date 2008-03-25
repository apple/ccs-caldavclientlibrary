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

from browser.command import Command
from browser.command import WrongOptions

class Cmd(Command):
    
    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("whoami", )
        
    def execute(self, name, options):
        if options:
            print self.usage(name)
            raise WrongOptions()
        print self.shell.user
        return True

    def usage(self, name):
        return """Usage: %s
""" % (name,)

    def helpDescription(self):
        return "Displays the current server login id."

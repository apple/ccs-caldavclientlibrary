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

class Command(object):

    def __init__(self):

        self.shell = None
        self.cmds = ()
        self.do_wd_complete = False


    def execute(self, name, options):
        raise NotImplementedError


    def usage(self, name):
        raise NotImplementedError


    def hasHelp(self, name):
        return name in self.cmds


    def help(self, name):
        result = "Command: %s\n" % (name,)
        result += "Description: %s\n" % (self.helpDescription(),)
        result += self.usage(name)
        return result


    def helpListing(self, name):
        return (name, self.helpDescription())


    def helpDescription(self):
        return ""


    def setShell(self, shell):
        self.shell = shell


    def getCmds(self):
        return self.cmds


    def complete(self, text):
        return () if not self.do_wd_complete else self.shell.wdcomplete(text)



class WrongOptions(Exception):
    pass



class UnknownCommand(Exception):
    pass



class CommandError(Exception):
    pass

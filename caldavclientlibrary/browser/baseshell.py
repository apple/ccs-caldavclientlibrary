# #
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
# #

from caldavclientlibrary.browser import utils
from caldavclientlibrary.browser.command import CommandError
from caldavclientlibrary.browser.command import UnknownCommand
from caldavclientlibrary.protocol.url import URL
from caldavclientlibrary.protocol.webdav.definitions import davxml
import os
import readline
import traceback
import urllib

class BaseShell(object):

    def __init__(self, history_name):

        self.prefix = ""
        self.commands = {}
        self.history = []
        self.history_name = history_name
        self.preserve_history = False
        self.last_wd_complete = ("", ())

        self.readHistory()


    def readHistory(self):
        try:
            readline.read_history_file(os.path.expanduser("~/.%s" % (self.history_name,)))
        except IOError:
            pass


    def saveHistory(self):
        readline.write_history_file(os.path.expanduser("~/.%s" % (self.history_name,)))


    def registerCommands(self, cmds):
        raise NotImplementedError


    def registerCommand(self, command):
        for cmd in command.getCmds():
            self.commands[cmd] = command
        command.setShell(self)


    def run(self):

        # Preserve existing history
        if self.preserve_history:
            old_history = [readline.get_history_item(index) for index in xrange(readline.get_current_history_length())]
            old_history = filter(lambda x: x is not None, old_history)
            readline.clear_history()
            map(readline.add_history, self.history)

        old_completer = readline.get_completer()
        readline.set_completer(self.complete)
        readline.parse_and_bind("bind ^I rl_complete")

        while True:
            cmdline = raw_input("%s > " % (self.prefix,))
            self.last_wd_complete = ("", ())
            if not cmdline:
                continue

            # Try to dispatch command
            try:
                self.execute(cmdline)
            except SystemExit, e:
                print "Exiting shell: %s" % (e.code,)
                break
            except UnknownCommand, e:
                print "Command '%s' unknown." % (e,)
            except Exception, e:
                traceback.print_exc()

        readline.set_completer(old_completer)

        # Restore previous history
        if self.preserve_history:
            self.saveHistory()
            readline.clear_history()
            map(readline.add_history, old_history)


    def execute(self, cmdline):

        # Check for history recall
        if cmdline == "!!" and self.history:
            cmdline = self.history[-1]
            print cmdline
            if readline.get_current_history_length():
                readline.replace_history_item(readline.get_current_history_length() - 1, cmdline)
        elif cmdline.startswith("!"):
            try:
                index = int(cmdline[1:])
                if index > 0 and index <= len(self.history):
                    cmdline = self.history[index - 1]
                    print cmdline
                    if readline.get_current_history_length():
                        readline.replace_history_item(readline.get_current_history_length() - 1, cmdline)
                else:
                    raise ValueError()
            except ValueError:
                print "%s: event not found" % (cmdline,)
                return

        # split the command line into command and options
        splits = cmdline.split(" ", 1)
        cmd = splits[0]
        options = splits[1] if len(splits) == 2 else ""

        # Find matching command
        try:
            if cmd not in self.commands:
                self.history.append(cmdline)
                raise UnknownCommand(cmd)
            else:
                self.commands[cmd].execute(cmd, options)
        finally:
            # Store in history
            self.history.append(cmdline)


    def help(self, cmd=None):

        if cmd:
            if cmd in self.commands:
                cmds = ((cmd, self.commands[cmd]),)
                full_help = True
            else:
                raise CommandError("Command could not be found: %s" % (cmd,))
        else:
            cmds = self.commands.keys()
            cmds.sort()
            cmds = [(cmd, self.commands[cmd]) for cmd in cmds]
            full_help = False

        if full_help:
            if self.commands[cmd].hasHelp(cmd):
                print self.commands[cmd].help(cmd)
        else:
            results = []
            for name, cmd in cmds:
                if cmd.hasHelp(name):
                    results.append(cmd.helpListing(name))
            utils.printTwoColumnList(results)


    def complete(self, text, state):

        # If there is no space in the text we complete a command
        # print "complete: %s %d" % (text, state)
        results = []
        check = readline.get_line_buffer()[:readline.get_endidx()].lstrip()
        checklen = len(check)
        if " " not in check:
            for cmd in self.commands:
                if cmd[:checklen] == check:
                    results.append(cmd + " ")
        else:
            cmd, rest = check.split(" ", 1)
            if cmd in self.commands:
                results = self.commands[cmd].complete(rest)

        return results[state]


    def wdcomplete(self, text):

        # print "\nwdcomplete: %s" % (text,)

        # Look at cache and return that
        # if self.last_wd_complete[0] == text:
        #    return self.last_wd_complete[1]

        # Split on whitespace and use the last item as the token
        tokens = text.split()

        # Look for relative vs absolute
        if tokens[-1] and tokens[-1][0] == "/":
            dirname, _ignore_child = os.path.split(tokens[-1])
            path = dirname
            if not path.endswith("/"):
                path += "/"
            pathlen = 0
        else:
            path = self.wd
            pathlen = len(path) + (0 if path.endswith("/") else 1)
            dirname, _ignore_child = os.path.split(tokens[-1])
            if dirname:
                path = os.path.join(path, dirname)
            if not path.endswith("/"):
                path += "/"

        # print "pdc: %s, %s, %s" % (self.wd, path, dirname)
        resource = URL(url=path)

        props = (davxml.resourcetype,)
        results = self.account.session.getPropertiesOnHierarchy(resource, props)
        results = [urllib.unquote(result) for result in results.iterkeys()]
        results = [result[pathlen:] for result in results if len(result) > pathlen]
        # print results
        if tokens[-1]:
            textlen = len(tokens[-1])
            results = [result for result in results if result[:textlen] == tokens[-1]]
            # print results

        self.last_wd_complete = (tokens[-1], results,)
        return results

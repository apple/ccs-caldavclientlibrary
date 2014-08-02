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

# import caldavclientlibrary.admin.xmlaccounts.commands
from caldavclientlibrary.admin.xmlaccounts.commands import registered

import sys

def usage():
    """
    Print out the command line usage.
    """
    cmds = registered.keys()
    cmds.sort()
    print """USAGE: manage CMD [OPTIONS]

CMD: one of:
%s

OPTIONS: specific to each command, use --help with the
command to see what options are supported.
""" % ("\n".join(["\t%s" % (cmd,) for cmd in cmds]),)



def runit():
    """
    Run the command based on command line arguments.
    """

    # Dispatch a command based on the first argument
    if len(sys.argv) == 1:
        usage()
        sys.exit(0)

    if sys.argv[1] in registered:
        sys.exit(registered[sys.argv[1]]().execute(sys.argv[2:]))
    else:
        print "No command called '%s' is available." % (sys.argv[1],)
        usage()
        sys.exit(0)

if __name__ == '__main__':
    runit()

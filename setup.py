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

"""
Script for building the UI app (OS X only).

Usage:
    python setup.py py2app
""" 

from distutils.core import setup
import py2app

plist = dict(NSMainNibFile="WebDAVBrowser")
setup(
    app=["src/ui/WebDAVBrowser.py"],
    data_files=["src/ui/WebDAVBrowser.nib", ],
    options=dict(py2app=dict(plist=plist, includes=["urllib", "sha", "md5",], packages=["src/client", "src/protocol", "src/ui",])),
)

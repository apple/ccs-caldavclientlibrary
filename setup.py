##
# Copyright (c) 2007-2016 Apple Inc. All rights reserved.
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
from os.path import dirname, join

"""
Script for building the UI app (OS X only).

Usage:
    python setup.py py2app
"""
import os

from distutils.core import setup
data_files = []
package_data = {}
try:
    import py2app #@UnusedImport
except ImportError:
    pass
else:
    data_files.append("caldavclientlibrary/ui/WebDAVBrowser.nib")
    package_data['caldavclientlibrary'] = [
        'ui/WebDAVBrowser.nib/*',
    ]

packages = []
for dirpath, dirnames, filenames in os.walk('caldavclientlibrary'):
    if '__init__.py' in filenames:
        packages.append(dirpath)

plist = dict(NSMainNibFile="WebDAVBrowser")

#
# Options
#

version_string = "0.1"

name = "CalDAVClientLibrary"

description = "CalDAV/CardDAV client tool"

long_description = file(join(dirname(__file__), "README")).read()

url = "https://github.com/apple/ccs-caldavclientlibrary"

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 2 :: Only",
    "Topic :: Software Development :: Testing",
]

author = "Apple Inc."

author_email = "calendarserver-dev@lists.macosforge.org"

license = "Apache License, Version 2.0"

platforms = ["all"]


#
# Dependencies
#

setup_requirements = []

install_requirements = []

extras_requirements = {}


#
# Set up Extension modules that need to be built
#

# from distutils.core import Extension

extensions = []



#
# Run setup
#

setup(
    name=name,
    version=version_string,
    description=description,
    long_description=long_description,
    url=url,
    classifiers=classifiers,
    author=author,
    author_email=author_email,
    license=license,
    platforms=platforms,
    app=["caldavclientlibrary/ui/WebDAVBrowser.py"],
    packages=packages,
    data_files=data_files,
    package_data=package_data,
    scripts=['runshell.py', 'runadmin.py'],
    options=dict(py2app=dict(plist=plist, includes=["urllib", "sha", "md5", ],
                             packages=["caldavclientlibrary/client",
                                       "caldavclientlibrary/protocol",
                                       "caldavclientlibrary/ui",
                                       "caldavclientlibrary/admin",
                                       ])),
)

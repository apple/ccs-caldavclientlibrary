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

from caldavclientlibrary.admin.xmlaccounts.commands.addrecord import AddRecord
from caldavclientlibrary.admin.xmlaccounts.commands.changepassword import ChangePassword
from caldavclientlibrary.admin.xmlaccounts.commands.listrecords import ListRecords
from caldavclientlibrary.admin.xmlaccounts.commands.removerecord import RemoveRecord

# Commands register themselves in this dict
registered = {}

registered[AddRecord.CMDNAME] = AddRecord
registered[ChangePassword.CMDNAME] = ChangePassword
registered[ListRecords.CMDNAME] = ListRecords
registered[RemoveRecord.CMDNAME] = RemoveRecord

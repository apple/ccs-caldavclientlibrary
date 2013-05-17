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

from caldavclientlibrary.protocol.calendarserver.notifications import InviteNotification, \
    InviteReply
from caldavclientlibrary.protocol.url import URL
from caldavclientlibrary.protocol.webdav.definitions import davxml
import readline
import types


def printPrincipalPaths(account, principals, resolve, refresh):

    result = ""
    if resolve:
        results = [account.getPrincipal(item, refresh=refresh) for item in principals]
        results.sort(key=lambda x: x.getSmartDisplayName())
        strlen = reduce(lambda x, y: max(x, len(y.getSmartDisplayName()) + 1), results, 0)
        results = ["%- *s (%s)" % (strlen, principal.getSmartDisplayName(), principal.principalURL) for principal in results]
    else:
        results = [item.relativeURL() for item in principals]
        results.sort()

    if len(results) == 1:
        return results[0]
    else:
        for item in results:
            result += "\n        %s" % (item,)

    return result



def printPrincipals(account, principals, resolve, refresh):

    result = ""
    if resolve:
        results = list(principals)
        if refresh:
            for principal in results:
                principal.loadDetails(True)
        results.sort(key=lambda x: x.getSmartDisplayName())
        strlen = reduce(lambda x, y: max(x, len(y.getSmartDisplayName()) + 1), results, 0)
        results = ["%- *s (%s)" % (strlen, principal.getSmartDisplayName(), principal.principalURL) for principal in results]
    else:
        results = [item.principalURL for item in principals]
        results.sort()

    if len(results) == 1:
        return results[0]
    else:
        for item in results:
            result += "\n        %s" % (item,)

    return result



def printProxyPrincipals(account, principal, read=True, write=True, resolve=True, refresh_main=False, refresh=False):
    if read:
        print "    Read-Only Proxies: %s" % printPrincipals(account, principal.getReadProxies(refresh_main), resolve, refresh)
        refresh_main = False
    if write:
        print "    Read-Write Proxies: %s" % printPrincipals(account, principal.getWriteProxies(refresh_main), resolve, refresh)



def printProperties(items):
    sorted = items.keys()
    sorted.sort()
    for key in sorted:
        value = items[key]
        if type(value) in (types.StringType, types.UnicodeType, types.IntType):
            print "    %s: %s" % (key, value,)
        elif type(value) in (types.ListType, types.TupleType,):
            print "    %s: %s" % (key, printList(value),)
        else:
            print "    %s: %s" % (key, value,)



def printList(items):
    result = ""
    if len(items) == 1:
        return items[0]
    else:
        sorted = list(items)
        sorted.sort()
        for item in sorted:
            result += "\n        %s" % (item,)
        return result



def printTwoColumnList(items, indent=0):

    strlen = reduce(lambda x, y: max(x, len(y[0]) + 1), items, 0)
    sorted = list(items)
    sorted.sort(key=lambda x: x[0])
    for col1, col2 in sorted:
        print "%s%- *s - %s" % (" " * indent, strlen, col1, col2,)



def printPrincipalList(principals):

    result = ""
    for ctr, principal in enumerate(principals):
        result += "\n% 2d. %s (%s)" % (ctr + 1, principal.getSmartDisplayName(), principal.principalURL)
    return result



def printACEList(aces, account):

    result = ""
    for ctr, ace in enumerate(aces):
        result += "\n% 2d. %s" % (ctr + 1, printACE(ace, account))
    return result



def printACE(ace, account):

    principalText = ace.principal
    if principalText == str(davxml.href):
        principal = account.getPrincipal(URL(url=ace.data))
        principalText = "%s (%s)" % (principal.getSmartDisplayName(), principal.principalURL)
    elif principalText == str(davxml.all):
        principalText = "ALL"
    elif principalText == str(davxml.authenticated):
        principalText = "AUTHENTICATED"
    elif principalText == str(davxml.unauthenticated):
        principalText = "UNAUTHENTICATED"
    elif principalText == str(davxml.property):
        principalText = "PROPERTY: %s" % (ace.data,)
    result = "Principal: %s\n" % (principalText,)
    if ace.invert or ace.protected or ace.inherited:
        result += "    Status:"
        if ace.invert:
            result += " INVERTED"
        if ace.protected:
            result += " PROTECTED"
        if ace.inherited:
            result += " INHERITED"
        result += "\n"
    result += "    Grant: " if ace.grant else "    Deny: "
    result += ", ".join(ace.privs)
    result += "\n"
    return result



def printInviteList(invites, account):

    result = "Organizer: %s (%s)" % (invites.organizer_cn, invites.organizer_uid,)
    for ctr, user in enumerate(invites.invitees):
        result += "\n% 2d. %s" % (ctr + 1, printInviteUser(user, account))
    return result



def printInviteUser(user, account):

    return "%s (%s) Invite: %s  Access: %s  Summary: %s" % (
        user.user_cn,
        user.user_uid,
        user.mode,
        user.access,
        user.summary,
    )



def printNotificationsList(notifications, account):

    result = ""
    if notifications:
        for ctr, notification in enumerate(notifications):
            result += "\n% 2d. %s" % (ctr + 1, printNotification(notification, account))
    else:
        "No notifications."
    return result



def printNotification(notification, account):

    if isinstance(notification, InviteNotification):
        return "Sharing Invite: From: %s (%s)  Access: %s  Summary: %s  Host-URL: %s" % (
            notification.organizer_cn,
            notification.organizer_uid,
            notification.access,
            notification.summary,
            notification.hosturl,
        )
    elif isinstance(notification, InviteReply):
        return "Sharing Reply: From: %s  Result: %s  Summary: %s  Host-URL: %s" % (
            notification.user_uid,
            notification.mode,
            notification.summary,
            notification.hosturl,
        )



def textInput(title, insert=None):
    if insert:
        title = "%s [%s]:" % (title, insert,)
    result = raw_input(title)
    if readline.get_current_history_length():
        readline.remove_history_item(readline.get_current_history_length() - 1)
    if not result:
        result = insert
    return result



def numericInput(title, low, high, allow_q=False, insert=None):
    if allow_q:
        result = choiceInput(title, [str(num) for num in range(low, high + 1)] + ["q", ], insert)
        if result != "q":
            result = int(result)
        return result
    else:
        return int(choiceInput(title, [str(num) for num in range(low, high + 1)], insert))



def yesNoInput(title, insert=None):
    return choiceInput(title, ("y", "n"), insert)



def choiceInput(title, choices, insert=None):
    while True:
        result = textInput(title, insert)
        if not result:
            continue
        if result in choices:
            return result
        print "Invalid input. Try again."



def multiChoiceInput(title, choices, insert=None):
    while True:
        result = textInput(title, insert)
        if not result:
            continue
        for char in result:
            if char not in choices:
                break
        else:
            return result
        print "Invalid input. Try again."

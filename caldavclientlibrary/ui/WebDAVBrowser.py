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

"""
Code based on PyObjC examples included with Apple Developer tools.
"""

import Foundation #@UnusedImport
import AppKit #@UnusedImport
import WebKit #@UnusedImport

from AppKit import * #@UnusedWildImport
from AppKit import NSApplication #@UnresolvedImport
from AppKit import NSImage #@UnresolvedImport
from AppKit import NSMenuItem #@UnresolvedImport
from AppKit import NSObject #@UnresolvedImport
from AppKit import NSPlainFileType #@UnresolvedImport
from AppKit import NSSize #@UnresolvedImport
from AppKit import NSToolbar #@UnresolvedImport
from AppKit import NSToolbarCustomizeToolbarItemIdentifier #@UnresolvedImport
from AppKit import NSToolbarFlexibleSpaceItemIdentifier #@UnresolvedImport
from AppKit import NSToolbarItem #@UnresolvedImport
from AppKit import NSToolbarPrintItemIdentifier #@UnresolvedImport
from AppKit import NSToolbarSeparatorItemIdentifier #@UnresolvedImport
from AppKit import NSToolbarSpaceItemIdentifier #@UnresolvedImport
from AppKit import NSURL #@UnresolvedImport
from AppKit import NSUserDefaults #@UnresolvedImport
from AppKit import NSWorkspace #@UnresolvedImport

from Foundation import * #@UnusedWildImport

from PyObjCTools import NibClassBuilder, AppHelper

import objc

from caldavclientlibrary.protocol.utils import xmlhelpers
from caldavclientlibrary.ui.session import Session
from xml.etree.ElementTree import _ElementInterface
import types

NibClassBuilder.extractClasses("WebDAVBrowser")

kServerToolbarItemIdentifier = "WDB: Server Toolbar Identifier"
kRefreshToolbarItemIdentifier = "WDB: Refresh Toolbar Identifier"
kBrowserViewToolbarItemIdentifier = "WDB: Browser View Toolbar Identifier"
kDataViewToolbarItemIdentifier = "WDB: Data View Toolbar Identifier"

def addToolbarItem(aController, anIdentifier, aLabel, aPaletteLabel,
                   aToolTip, aTarget, anAction, anItemContent, aMenu):
    """
    Add a toolbar button of some kind.
    """
    toolbarItem = NSToolbarItem.alloc().initWithItemIdentifier_(anIdentifier)

    toolbarItem.setLabel_(aLabel)
    toolbarItem.setPaletteLabel_(aPaletteLabel)
    toolbarItem.setToolTip_(aToolTip)
    toolbarItem.setTarget_(aTarget)
    if anAction:
        toolbarItem.setAction_(anAction)

    if type(anItemContent) == NSImage:
        toolbarItem.setImage_(anItemContent)
    else:
        toolbarItem.setView_(anItemContent)
        bounds = anItemContent.bounds()
        minSize = (bounds[1][0], bounds[1][1])
        maxSize = (bounds[1][0], bounds[1][1])
        toolbarItem.setMinSize_(minSize)
        toolbarItem.setMaxSize_(maxSize)

    if aMenu:
        menuItem = NSMenuItem.alloc().init()
        menuItem.setSubmenu_(aMenu)
        menuItem.setTitle_(aMenu.title())
        toolbarItem.setMenuFormRepresentation_(menuItem)

    aController._toolbarItems[anIdentifier] = toolbarItem

WRAPPED = {}
class Wrapper(NSObject):
    """
    NSOutlineView doesn't retain values, which means we cannot use normal
    python values as values in an outline view.
    """
    def init_(self, value):
        self.value = value
        return self


    def __str__(self):
        return '<Wrapper for %s>' % self.value


    def description(self):
        return str(self)



def wrap_object(obj):
    if obj in WRAPPED:
        return WRAPPED[obj]
    else:
        WRAPPED[obj] = Wrapper.alloc().init_(obj)
        return WRAPPED[obj]



def unwrap_object(obj):
    if obj is None:
        return obj
    return obj.value



class WebDAVBrowserDelegate(NibClassBuilder.AutoBaseClass):
    """
    Class defined in NIB file. This acts as the delegate and responder
    for the various NSViews and toolbar items. It basically our controller.
    """

    list = objc.IBOutlet()

    listView = objc.IBOutlet()

    mainSplitterView = objc.IBOutlet()

    passwordText = objc.IBOutlet()

    pathLabel = objc.IBOutlet()

    pathText = objc.IBOutlet()

    progress = objc.IBOutlet()

    propertiesView = objc.IBOutlet()

    serverText = objc.IBOutlet()

    startupSheet = objc.IBOutlet()

    table = objc.IBOutlet()

    text = objc.IBOutlet()

    toolbarBrowserViewButton = objc.IBOutlet()

    toolbarDataViewButton = objc.IBOutlet()

    userText = objc.IBOutlet()

    webView = objc.IBOutlet()

    window = objc.IBOutlet()

    browser = objc.IBOutlet()

    columnView = objc.IBOutlet()

    dataView = objc.IBOutlet()

    BROWSERVIEW_COLUMNS = 0
    BROWSERVIEW_LIST = 1

    DATAVIEW_PROPERTIES = 0
    DATAVIEW_DATA = 1
    # DATAVIEW_DELEGATES  = 2
    # DATAVIEW_ACLS       = 3

    selectedDetails = None

    def awakeFromNib(self):
        # Initialise our session and selected state parameters
        self.session = None
        self.columns = [[]]
        self.selectedResource = None
        self.selectedDetails = None
        self.selectedData = None

        # Cache some useful icons
        self.fileImage = NSWorkspace.sharedWorkspace().iconForFileType_(NSPlainFileType)
        self.fileImage.setSize_(NSSize(16, 16))
        self.directoryImage = NSWorkspace.sharedWorkspace().iconForFile_("/usr/")
        self.directoryImage.setSize_(NSSize(16, 16))

        # Initialise the toolbar
        self._toolbarItems = {}
        self._toolbarDefaultItemIdentifiers = []
        self._toolbarAllowedItemIdentifiers = []
        self.createToolbar()

        # Set up browser view
        container = self.mainSplitterView.subviews()[0]
        container.addSubview_(self.columnView)
        container.addSubview_(self.listView)
        self.currentBrowserView = None
        self.setBrowserView(self.BROWSERVIEW_COLUMNS)
        self.browser.setMaxVisibleColumns_(7)
        self.browser.setMinColumnWidth_(150)

        # Set up data view
        container = self.mainSplitterView.subviews()[1]
        container.addSubview_(self.propertiesView)
        container.addSubview_(self.dataView)
        self.currentDataView = None
        self.setDataView(self.DATAVIEW_PROPERTIES)
        self.text.setString_("")

        self.pathLabel.setStringValue_("No server specified")

        # Get preferences
        lastServer = NSUserDefaults.standardUserDefaults().stringForKey_("LastServer")
        if lastServer and len(lastServer):
            self.serverText.setStringValue_(lastServer)
        lastPath = NSUserDefaults.standardUserDefaults().stringForKey_("LastPath")
        if lastPath and len(lastPath):
            self.pathText.setStringValue_(lastPath)
        else:
            self.pathText.setStringValue_("/")
        lastUser = NSUserDefaults.standardUserDefaults().stringForKey_("LastUser")
        if lastUser and len(lastUser):
            self.userText.setStringValue_(lastUser)


    def createToolbar(self):
        """
        Create the toolbar for our app.
        """
        toolbar = NSToolbar.alloc().initWithIdentifier_("Toolbar")
        toolbar.setDelegate_(self)
        toolbar.setAllowsUserCustomization_(YES)
        toolbar.setAutosavesConfiguration_(YES)

        self.createToolbarItems()

        self.window.setToolbar_(toolbar)


    def createToolbarItems(self):
        """
        Create the toolbar item and define the default and allowed set.
        """
        addToolbarItem(self, kServerToolbarItemIdentifier,
                       "Server", "Server", "Reset Server", self,
                       "resetServer:", NSImage.imageNamed_("NSNetwork"), None,)

        addToolbarItem(self, kRefreshToolbarItemIdentifier,
                       "Refresh", "Refresh", "Refresh Display", self,
                       "refreshData:", NSImage.imageNamed_("NSRefresh"), None,)

        addToolbarItem(self, kBrowserViewToolbarItemIdentifier,
                       "Browser", "Browser", "Browser View", self,
                       "changeBrowserView:", self.toolbarBrowserViewButton, None,)

        addToolbarItem(self, kDataViewToolbarItemIdentifier,
                       "View", "View", "Data View", self,
                       "changeDataView:", self.toolbarDataViewButton, None,)

        self._toolbarDefaultItemIdentifiers = [
            kServerToolbarItemIdentifier,
            kBrowserViewToolbarItemIdentifier,
            kDataViewToolbarItemIdentifier,
            NSToolbarFlexibleSpaceItemIdentifier,
            kRefreshToolbarItemIdentifier,
        ]

        self._toolbarAllowedItemIdentifiers = [
            kServerToolbarItemIdentifier,
            kBrowserViewToolbarItemIdentifier,
            kDataViewToolbarItemIdentifier,
            kRefreshToolbarItemIdentifier,
            NSToolbarSeparatorItemIdentifier,
            NSToolbarSpaceItemIdentifier,
            NSToolbarFlexibleSpaceItemIdentifier,
            NSToolbarPrintItemIdentifier,
            NSToolbarCustomizeToolbarItemIdentifier,
        ]


    def toolbarDefaultItemIdentifiers_(self, anIdentifier):
        """
        Return the default set of toolbar items.
        """
        return self._toolbarDefaultItemIdentifiers


    def toolbarAllowedItemIdentifiers_(self, anIdentifier):
        """
        Return the allowed set of toolbar items.
        """
        return self._toolbarAllowedItemIdentifiers


    def toolbar_itemForItemIdentifier_willBeInsertedIntoToolbar_(self,
                                                                 toolbar,
                                                                 itemIdentifier, flag):
        """
        Delegate method fired when the toolbar is about to insert an
        item into the toolbar.  Item is identified by itemIdentifier.

        Effectively makes a copy of the cached reference instance of
        the toolbar item identified by itemIdentifier.
        """
        newItem = NSToolbarItem.alloc().initWithItemIdentifier_(itemIdentifier)
        item = self._toolbarItems[itemIdentifier]

        newItem.setLabel_(item.label())
        newItem.setPaletteLabel_(item.paletteLabel())
        if item.view():
            newItem.setView_(item.view())
        else:
            newItem.setImage_(item.image())

        newItem.setToolTip_(item.toolTip())
        newItem.setTarget_(item.target())
        newItem.setAction_(item.action())
        newItem.setMenuFormRepresentation_(item.menuFormRepresentation())

        if newItem.view():
            newItem.setMinSize_(item.minSize())
            newItem.setMaxSize_(item.maxSize())

        return newItem


    def setBrowserView(self, view):
        """
        Change the browser view pane to the specified list type.
        """
        newView = {
            self.BROWSERVIEW_COLUMNS: self.columnView,
            self.BROWSERVIEW_LIST   : self.listView,
        }.get(view, None)
        if self.currentBrowserView != newView:
            if self.currentBrowserView:
                self.currentBrowserView.setHidden_(YES)
            self.currentBrowserView = newView
            if self.currentBrowserView:
                self.currentBrowserView.setHidden_(NO)
            self.browserview = view
            self.refreshView()


    @objc.IBAction
    def changeBrowserView_(self, sender):
        """
        User clicked a browser toolbar button.
        """
        self.setBrowserView(sender.selectedSegment())


    def setDataView(self, view):
        """
        Change the data view pane to the specified type.
        """
        newView = {
            self.DATAVIEW_PROPERTIES: self.propertiesView,
            self.DATAVIEW_DATA      : self.dataView,
        }.get(view, None)
        if self.currentDataView != newView:
            if self.currentDataView:
                self.currentDataView.setHidden_(YES)
            self.currentDataView = newView
            if self.currentDataView:
                self.currentDataView.setHidden_(NO)
            self.dataview = view
            self.refreshView()


    @objc.IBAction
    def changeDataView_(self, sender):
        """
        User clicked a view toolbar button.
        """
        self.setDataView(sender.selectedSegment())


    @objc.IBAction
    def resetServer_(self, sender):
        """
        Display the sheet asking for server details.
        """
        NSApplication.sharedApplication().beginSheet_modalForWindow_modalDelegate_didEndSelector_contextInfo_(
            self.startupSheet,
            self.window,
            None, None, 0
        )


    def refreshData_(self, sender):
        """
        Force a refresh of the data for the current selected resource.
        """
        if self.selectedResource:
            self.selectedResource.clear()

            self.progress.startAnimation_(self)
            resources = self.selectedResource.listChildren()
            self.columns[-1] = resources
            self.progress.stopAnimation_(self)

            self.refreshView()


    def refreshView(self):
        """
        Refresh the actual data view for the selected resource.
        """
        if self.selectedResource:
            self.progress.startAnimation_(self)
            if self.dataview == self.DATAVIEW_PROPERTIES:
                self.selectedDetails = self.selectedResource.getAllDetails()
                self.table.reloadData()
                self.table.deselectAll_(self)
                self.text.setString_("")
            elif self.dataview == self.DATAVIEW_DATA:
                self.selectedData = self.selectedResource.getDataAsHTML()
                url = NSURL.alloc().initWithString_(self.serverText.stringValue())
                self.webView.mainFrame().loadHTMLString_baseURL_(self.selectedData, url)
            self.progress.stopAnimation_(self)


    @objc.IBAction
    def startupOKAction_(self, btn):
        """
        User clicked OK in the server setup sheet.
        """

        # Create the actual session.
        server = self.serverText.stringValue()
        path = self.pathText.stringValue()
        user = self.userText.stringValue()
        pswd = self.passwordText.stringValue()
        self.session = Session(server, path, user, pswd, logging=False)
        self.window.setTitle_(self.serverText.stringValue())
        self.pathLabel.setStringValue_(self.session.path)
        NSUserDefaults.standardUserDefaults().setObject_forKey_(server, "LastServer")
        NSUserDefaults.standardUserDefaults().setObject_forKey_(path, "LastPath")
        NSUserDefaults.standardUserDefaults().setObject_forKey_(user, "LastUser")

        # List the root resource.
        self.progress.startAnimation_(self)
        resources = self.session.getRoot().listChildren()
        self.progress.stopAnimation_(self)
        self.columns = [resources]

        # Done with the sheet.
        self.startupSheet.close()
        NSApplication.sharedApplication().endSheet_(self.startupSheet)

        # Force reload of browser pane views.
        self.browser.loadColumnZero()
        self.list.reloadItem_(None)


    @objc.IBAction
    def startupCancelAction_(self, btn):
        """
        User clicked the cancel button in the server sheet.
        """
        self.startupSheet.close()
        NSApplication.sharedApplication().endSheet_(self.startupSheet)


    @objc.IBAction
    def browserAction_(self, browser):
        """
        Something changed in the column browser.
        """

        # Update current path.
        self.pathLabel.setStringValue_((self.session.path if len(self.session.path) > 1 else "") + browser.path())

        # Get new selected resource and refresh the data view.
        self.selectedResource = None
        self.selectedDetails = None
        col = len(self.columns)
        row = -1
        while row == -1:
            col -= 1
            if col < 0:
                break
            row = self.browser.selectedRowInColumn_(col)
        if row >= 0:
            self.selectedResource = self.columns[col][row]

        self.refreshView()


    def browser_willDisplayCell_atRow_column_(self, browser, cell, row, col):
        """
        Delegate method to set the actual stuff displayed in a column view row.
        """
        isLeaf = not self.columns[col][row].isCollection()
        cell.setLeaf_(isLeaf)
        cell.setStringValue_(self.columns[col][row].getName())
        cell.setImage_(self.fileImage if isLeaf else self.directoryImage)


    def browser_numberOfRowsInColumn_(self, browser, col):
        """
        Delegate method that returns the number of rows in a column view column.
        """
        if col == 0:
            return len(self.columns[0])
        del self.columns[col:]
        resource = self.columns[col - 1][browser.selectedRowInColumn_(col - 1)]
        self.progress.startAnimation_(self)
        resources = resource.listChildren()
        self.progress.stopAnimation_(self)
        self.columns.append(resources)
        return len(resources)


    def outlineViewSelectionDidChange_(self, notification):
        """
        Delegate method called when the selection in the outline view changes.
        """

        # Get the new selected resource and refresh the data view.
        row = self.list.selectedRow()
        if row == -1:
            self.selectedResource = None
            self.pathLabel.setStringValue_("Nothing Selected")
        else:
            self.selectedResource = unwrap_object(self.list.itemAtRow_(row))
            self.pathLabel.setStringValue_(self.selectedResource.getPath())

        self.refreshView()


    def outlineView_numberOfChildrenOfItem_(self, outlineView, item):
        """
        Delegate method to return the number of children of an item in the outline view.
        """
        if self.session is None:
            return 0
        if item is None:
            resource = self.session.getRoot()
        else:
            resource = unwrap_object(item)
        self.progress.startAnimation_(self)
        resources = resource.listChildren()
        self.progress.stopAnimation_(self)
        return len(resources)


    def outlineView_isItemExpandable_(self, outlineView, item):
        """
        Delegate method to return the whether an item in the outline view is expandable.
        """
        if item is None:
            return YES
        else:
            resource = unwrap_object(item)
            return YES if resource.isCollection() else NO


    def outlineView_child_ofItem_(self, outlineView, index, item):
        """
        Delegate method to return the item associated with a row in the outline view.
        """
        if item is None:
            resource = self.session.getRoot()
        else:
            resource = unwrap_object(item)
        self.progress.startAnimation_(self)
        resources = resource.listChildren()
        self.progress.stopAnimation_(self)
        return wrap_object(resources[index])


    def outlineView_objectValueForTableColumn_byItem_(self, outlineView, tableColumn, item):
        """
        Delegate method to return the data displayed in the outline view.
        """
        if item is None:
            resource = self.session.getRoot()
        else:
            resource = unwrap_object(item)
        return {
            "Name"    : resource.getName(),
            "Size"    : resource.getSize(),
            "Modified": resource.getLastMod(),
        }[tableColumn.identifier()]


    @objc.IBAction
    def tableAction_(self, table):
        """
        Called when the selection in the properties list changes.
        """

        # Get the selected property and display its value.
        row = self.table.selectedRow()
        if row >= 0:
            value = self.selectedDetails[row][1]
            if type(value) in (types.ListType, types.TupleType,):
                if len(value) == 1:
                    text = self.propValueToText(value[0])
                else:
                    sorted = [self.propValueToText(v) for v in value]
                    sorted.sort()
                    text = "\r".join(sorted)
            else:
                text = self.propValueToText(value)
        else:
            text = ""
        self.text.setString_(text)


    def numberOfRowsInTableView_(self, tableView):
        """
        Delegate method to return the number of rows in the list.
        @param tableView:
        @type tableView:
        """
        if self.selectedDetails is None:
            return 0
        return len(self.selectedDetails)


    def tableView_objectValueForTableColumn_row_(self, tableView, col, row):
        """
        Delegate method to return the text for a list cell.
        """
        return str(self.selectedDetails[row][0])


    def tableView_shouldEditTableColumn_row_(self, tableView, col, row):
        """
        Delegate method to indicate whether a cell can be edited.
        """
        return 0


    def propValueToText(self, value):
        """
        Do a sensible print of a property value taking type into account.
        """
        if type(value) in (types.StringType, types.UnicodeType, types.IntType):
            text = str(value)
        elif isinstance(value, _ElementInterface):
            text = xmlhelpers.elementToString(value).replace("\n", "")
        else:
            text = str(value)
        return text

if __name__ == "__main__":
    AppHelper.runEventLoop()

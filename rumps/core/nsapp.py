# -*- coding: utf-8 -*-
"""
nsapp.py — NSApp delegate class for rumps-style macOS status bar apps.
"""

import traceback

import AppKit
from AppKit import NSStatusBar, NSWorkspace, NSWorkspaceWillSleepNotification, NSWorkspaceDidWakeNotification
from Foundation import NSObject

from ..utils.helpers import _log
from ..utils import internal as _internal
from ..events import on_notification, on_sleep, on_wake
from ..notifications import _clicked


# A tiny, local fallback for quitting if the package-level helper isn't available.
def quit_application(sender=None):
    from AppKit import NSApplication
    _log('closing application')
    NSApplication.sharedApplication().terminate_(sender)

class NSApp(NSObject):
    """Objective-C delegate class for NSApplication. Don't instantiate - use App instead."""

    _ns_to_py_and_callback = {}

    def userNotificationCenter_didActivateNotification_(self, notification_center, notification):
        _clicked(notification_center, notification)

    def initializeStatusBar(self):
        self.nsstatusitem = NSStatusBar.systemStatusBar().statusItemWithLength_(-1)  # variable dimensions
        self.nsstatusitem.setHighlightMode_(True)

        self.setStatusBarIcon()
        self.setStatusBarTitle()

        mainmenu = self._app['_menu']
        quit_button = self._app['_quit_button']
        if quit_button is not None:
            quit_button.set_callback(quit_application)
            mainmenu.add(quit_button)
        else:
            _log('WARNING: the default quit button is disabled. To exit the application gracefully, another button '
                 'should have a callback of quit_application or call it indirectly.')
        self.nsstatusitem.setMenu_(mainmenu._menu)  # mainmenu of our status bar spot (_menu attribute is NSMenu)

    def showMenu(self):
        self.nsstatusitem.button().performClick_(None)

    def setStatusBarTitle(self):
        self.nsstatusitem.setTitle_(self._app['_title'])
        self.fallbackOnName()

    def setStatusBarIcon(self):
        self.nsstatusitem.setImage_(self._app['_icon_nsimage'])
        self.fallbackOnName()

    def fallbackOnName(self):
        if not (self.nsstatusitem.title() or self.nsstatusitem.image()):
            self.nsstatusitem.setTitle_(self._app['_name'])

    def applicationDidFinishLaunching_(self, notification):
        workspace          = NSWorkspace.sharedWorkspace()
        notificationCenter = workspace.notificationCenter()
        notificationCenter.addObserver_selector_name_object_(
            self,
            self.receiveSleepNotification_,
            NSWorkspaceWillSleepNotification,
            None
        )
        notificationCenter.addObserver_selector_name_object_(
            self,
            self.receiveWakeNotification_,
            NSWorkspaceDidWakeNotification,
            None
        )

    def receiveSleepNotification_(self, ns_notification):
        _log('receiveSleepNotification')
        on_sleep.emit()

    def receiveWakeNotification_(self, ns_notification):
        _log('receiveWakeNotification')
        on_wake.emit()

    def applicationWillTerminate_(self, ns_notification):
        _log('applicationWillTerminate')
        before_quit.emit()

    @classmethod
    def callback_(cls, nsmenuitem):
        self, callback = cls._ns_to_py_and_callback[nsmenuitem]
        _log(self)
        try:
            return _internal.call_as_function_or_method(callback, self)
        except Exception:
            traceback.print_exc()

    @classmethod
    def textFieldCallback_(cls, nstextfield):
        """Callback for TextFieldMenuItem when text changes or Enter is pressed."""
        self, callback = cls._ns_to_py_and_callback[nstextfield]
        _log(self)
        try:
            return _internal.call_as_function_or_method(callback, self)
        except Exception:
            traceback.print_exc()

    @classmethod
    def imageCallback_(cls, nsimageview):
        """Callback for ImageMenuItem when image is clicked."""
        self, callback = cls._ns_to_py_and_callback[nsimageview]
        _log(self)
        try:
            return _internal.call_as_function_or_method(callback, self)
        except Exception:
            traceback.print_exc()

    @classmethod
    def listSelectionCallback_(cls, nscombobox_or_notification):
        """Callback for ListMenuItem when NSComboBox selection changes."""
        try:
            # Handle both direct NSComboBox objects and NSNotification objects
            if hasattr(nscombobox_or_notification, 'object') and nscombobox_or_notification.object():
                # This is an NSNotification, get the combo box from it
                nscombobox = nscombobox_or_notification.object()
            else:
                # This is a direct NSComboBox object
                nscombobox = nscombobox_or_notification

            self, callback = cls._ns_to_py_and_callback[nscombobox]
            _log(self)

            # Update internal tracking
            self._selected_index = nscombobox.indexOfSelectedItem()

            # Call user callback
            if callback:
                return _internal.call_as_function_or_method(callback, self)
        except Exception:
            traceback.print_exc()

    @classmethod
    def cardCallback_(cls, nsbutton):
        """Callback for CardMenuItem when card is clicked."""
        self, callback = cls._ns_to_py_and_callback[nsbutton]
        _log(self)
        try:
            if callback:
                return _internal.call_as_function_or_method(callback, self)
        except Exception:
            traceback.print_exc()

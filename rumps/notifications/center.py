#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""Notification center functionality for rumps."""

import os
import sys
import traceback
import Foundation

from .notification import Notification
from ..utils.internal import guard_unexpected_errors, require_string_or_none, string_to_objc
from ..events import on_notification as notification_event

_ENABLED = True
try:
    from Foundation import NSUserNotification, NSUserNotificationCenter
except ImportError:
    _ENABLED = False


def on_notification(f):
    """
    Decorator for registering a function to serve as a "notification center"
    for the application. This function will receive the data associated with an
    incoming macOS notification sent using notify(). This occurs whenever the
    user clicks on a notification for this application in the macOS Notification Center.

    Example:
        @rumps.notifications
        def notification_center(info):
            if 'unix' in info:
                print('i know this')
    """
    return notification_event.register(f)


def _gather_info_issue_9():  # pragma: no cover
    """Gather information about missing plist or bundle identifier."""
    missing_plist = False
    missing_bundle_ident = False
    info_plist_path = os.path.join(os.path.dirname(sys.executable), 'Info.plist')
    try:
        with open(info_plist_path) as f:
            import plistlib
            try:
                load_plist = plistlib.load
            except AttributeError:
                load_plist = plistlib.readPlist
            try:
                load_plist(f)['CFBundleIdentifier']
            except Exception:
                missing_bundle_ident = True

    except IOError as e:
        import errno
        if e.errno == errno.ENOENT:  # No such file or directory
            missing_plist = True

    info = '\n\n'
    if missing_plist:
        info += 'In this case there is no file at "%(info_plist_path)s"'
        info += '\n\n'
        confidence = 'should'
    elif missing_bundle_ident:
        info += 'In this case the file at "%(info_plist_path)s" does not contain a value for "CFBundleIdentifier"'
        info += '\n\n'
        confidence = 'should'
    else:
        confidence = 'may'
    info += 'Running the following command %(confidence)s fix the issue:\n'
    info += '/usr/libexec/PlistBuddy -c \'Add :CFBundleIdentifier string "rumps"\' %(info_plist_path)s\n'
    return info % {'info_plist_path': info_plist_path, 'confidence': confidence}


def _default_user_notification_center():
    """Get the default user notification center."""
    notification_center = NSUserNotificationCenter.defaultUserNotificationCenter()
    if notification_center is None:  # pragma: no cover
        info = (
            'Failed to setup the notification center. This issue occurs when the "Info.plist" file '
            'cannot be found or is missing "CFBundleIdentifier".'
        )
        try:
            info += _gather_info_issue_9()
        except Exception:
            pass
        raise RuntimeError(info)
    else:
        return notification_center


def _init_nsapp(nsapp):
    """Initialize the notification center with the NSApp delegate."""
    if _ENABLED:
        try:
            notification_center = _default_user_notification_center()
        except RuntimeError:
            pass
        else:
            notification_center.setDelegate_(nsapp)


@guard_unexpected_errors
def _clicked(ns_user_notification_center, ns_user_notification):
    """Handle notification click events."""
    from rumps import rumps

    ns_user_notification_center.removeDeliveredNotification_(ns_user_notification)
    ns_dict = ns_user_notification.userInfo()
    if ns_dict is None:
        data = None
    else:
        dumped = ns_dict['value']
        app = getattr(rumps.App, '*app_instance', rumps.App)
        try:
            data = app.serializer.loads(dumped)
        except Exception:
            traceback.print_exc()
            return

    # notification center function not specified => no error but log warning
    if not notification_event.callbacks:
        rumps._log(
            'WARNING: notification received but no function specified for '
            'answering it; use @notifications decorator to register a function.'
        )
    else:
        notification = Notification(ns_user_notification, data)
        notification_event.emit(notification)


def notify(title, subtitle, message, data=None, sound=True,
           action_button=None, other_button=None, has_reply_button=False,
           icon=None, ignoreDnD=False):
    """
    Send a notification to Notification Center (OS X 10.8+).

    If running on a version of macOS that does not support notifications,
    a RuntimeError will be raised.

    Apple says: "The userInfo content must be of reasonable serialized size
    (less than 1k) or an exception will be thrown."

    Args:
        title: Text in a larger font.
        subtitle: Text in a smaller font below the title.
        message: Text representing the body of the notification below the subtitle.
        data: Will be passed to the application's "notification center" when clicked.
        sound: Whether the notification should make a noise when it arrives.
        action_button: Title for the action button.
        other_button: Title for the other button.
        has_reply_button: Whether or not the notification has a reply button.
        icon: The filename of an image for the notification's icon.
        ignoreDnD: Whether the notification should ignore do not disturb.
    """
    from rumps import rumps

    if not _ENABLED:
        raise RuntimeError('OS X 10.8+ is required to send notifications')

    require_string_or_none(title, subtitle, message)

    notification = NSUserNotification.alloc().init()

    notification.setTitle_(title)
    notification.setSubtitle_(subtitle)
    notification.setInformativeText_(message)

    if data is not None:
        app = getattr(rumps.App, '*app_instance', rumps.App)
        dumped = app.serializer.dumps(data)
        objc_string = string_to_objc(dumped)
        ns_dict = Foundation.NSMutableDictionary.alloc().init()
        ns_dict.setDictionary_({'value': objc_string})
        notification.setUserInfo_(ns_dict)

    if icon is not None:
        notification.set_identityImage_(rumps._nsimage_from_file(icon))
    if sound:
        notification.setSoundName_("NSUserNotificationDefaultSoundName")
    if action_button:
        notification.setActionButtonTitle_(action_button)
        notification.set_showsButtons_(True)
    if other_button:
        notification.setOtherButtonTitle_(other_button)
        notification.set_showsButtons_(True)
    if has_reply_button:
        notification.setHasReplyButton_(True)
    if ignoreDnD:
        notification.set_ignoresDoNotDisturb_(True)

    notification.setDeliveryDate_(Foundation.NSDate.dateWithTimeInterval_sinceDate_(0, Foundation.NSDate.date()))
    notification_center = _default_user_notification_center()
    notification_center.scheduleNotification_(notification)
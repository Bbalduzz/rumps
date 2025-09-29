#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple Checkbox example

Shows basic usage of the CheckboxMenuItem.
"""

import rumps


class SimpleCheckboxApp(rumps.App):
    def __init__(self):
        super(SimpleCheckboxApp, self).__init__("Checkbox Test", title="☑️")

        # Create checkboxes
        self.dark_mode = rumps.CheckboxMenuItem(
            "Dark Mode",
            checked=False,
            callback=self.on_dark_mode
        )

        self.notifications = rumps.CheckboxMenuItem(
            "Notifications",
            checked=True,
            callback=self.on_notifications
        )

        self.auto_save = rumps.CheckboxMenuItem(
            "Auto-save",
            checked=True,
            callback=self.on_auto_save
        )

        # Build menu
        self.menu = [
            self.dark_mode,
            self.notifications,
            self.auto_save,
            rumps.separator,
            rumps.MenuItem("Show Status", callback=self.show_status),
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]

    def on_dark_mode(self, sender):
        """Handle dark mode checkbox."""
        print(f"Dark mode: {'CHECKED' if sender.checked else 'UNCHECKED'}")
        self.title = "🌙" if sender.checked else "☀️"

    def on_notifications(self, sender):
        """Handle notifications checkbox."""
        print(f"Notifications: {'CHECKED' if sender.checked else 'UNCHECKED'}")
        if sender.checked:
            rumps.notification("Notifications", "Enabled", "You'll receive updates")

    def on_auto_save(self, sender):
        """Handle auto-save checkbox."""
        print(f"Auto-save: {'CHECKED' if sender.checked else 'UNCHECKED'}")

    def show_status(self, sender):
        """Show current status of all checkboxes."""
        print(f"Dark Mode: {'✓' if self.dark_mode.checked else '✗'}")
        print(f"Notifications: {'✓' if self.notifications.checked else '✗'}")
        print(f"Auto-save: {'✓' if self.auto_save.checked else '✗'}")


if __name__ == "__main__":
    print("Simple checkbox demo")
    print("Click the checkboxes in the menu to see them in action!")

    app = SimpleCheckboxApp()
    app.run()
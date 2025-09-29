#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Checkbox example for rumps

This example demonstrates the CheckboxMenuItem component that provides
native macOS checkboxes for boolean settings and options.
"""

import rumps


class CheckboxDemoApp(rumps.App):
    def __init__(self):
        super(CheckboxDemoApp, self).__init__(
            "Checkbox Demo",
            title="☑️"
        )

        # Storage for checkbox references
        self.checkboxes = {}

        self.build_menu()

    def build_menu(self):
        """Build menu with various checkbox examples."""
        menu_items = []

        # Section 1: Basic Checkboxes
        menu_items.append(rumps.MenuItem("=== Settings ==="))

        # Dark Mode checkbox
        dark_mode = rumps.CheckboxMenuItem(
            "Dark Mode",
            checked=False,
            callback=self.on_dark_mode_change
        )
        self.checkboxes['dark_mode'] = dark_mode
        menu_items.append(dark_mode)

        # Notifications checkbox
        notifications = rumps.CheckboxMenuItem(
            "Enable Notifications",
            checked=True,
            callback=self.on_notifications_change
        )
        self.checkboxes['notifications'] = notifications
        menu_items.append(notifications)

        # Auto-save checkbox
        auto_save = rumps.CheckboxMenuItem(
            "Auto-save Documents",
            checked=True,
            callback=self.on_auto_save_change
        )
        self.checkboxes['auto_save'] = auto_save
        menu_items.append(auto_save)

        menu_items.append(rumps.separator)

        # Section 2: Feature Checkboxes
        menu_items.append(rumps.MenuItem("=== Features ==="))

        # Experimental features
        experimental = rumps.CheckboxMenuItem(
            "Experimental Features",
            checked=False,
            callback=self.on_experimental_change
        )
        self.checkboxes['experimental'] = experimental
        menu_items.append(experimental)

        # Debug mode
        debug_mode = rumps.CheckboxMenuItem(
            "Debug Mode",
            checked=False,
            callback=self.on_debug_change
        )
        self.checkboxes['debug'] = debug_mode
        menu_items.append(debug_mode)

        # Analytics
        analytics = rumps.CheckboxMenuItem(
            "Send Analytics",
            checked=True,
            callback=self.on_analytics_change
        )
        self.checkboxes['analytics'] = analytics
        menu_items.append(analytics)

        menu_items.append(rumps.separator)

        # Section 3: View Options
        menu_items.append(rumps.MenuItem("=== View Options ==="))

        # Show hidden files
        show_hidden = rumps.CheckboxMenuItem(
            "Show Hidden Files",
            checked=False,
            callback=self.on_show_hidden_change
        )
        self.checkboxes['show_hidden'] = show_hidden
        menu_items.append(show_hidden)

        # Show line numbers
        line_numbers = rumps.CheckboxMenuItem(
            "Show Line Numbers",
            checked=True,
            callback=self.on_line_numbers_change
        )
        self.checkboxes['line_numbers'] = line_numbers
        menu_items.append(line_numbers)

        # Word wrap
        word_wrap = rumps.CheckboxMenuItem(
            "Word Wrap",
            checked=False,
            callback=self.on_word_wrap_change
        )
        self.checkboxes['word_wrap'] = word_wrap
        menu_items.append(word_wrap)

        menu_items.append(rumps.separator)

        # Section 4: Controls
        menu_items.append(rumps.MenuItem("=== Controls ==="))

        menu_items.append(rumps.MenuItem("Check All", callback=self.check_all))
        menu_items.append(rumps.MenuItem("Uncheck All", callback=self.uncheck_all))
        menu_items.append(rumps.MenuItem("Toggle All", callback=self.toggle_all))
        menu_items.append(rumps.MenuItem("Reset to Defaults", callback=self.reset_defaults))

        menu_items.append(rumps.separator)
        menu_items.append(rumps.MenuItem("Show Current State", callback=self.show_state))

        menu_items.append(rumps.separator)
        menu_items.append(rumps.MenuItem("Quit", callback=rumps.quit_application))

        self.menu = menu_items

    def on_dark_mode_change(self, sender):
        """Handle dark mode checkbox change."""
        print(f"Dark Mode: {'CHECKED' if sender.checked else 'UNCHECKED'}")

        # Update app title to reflect dark mode
        self.title = "🌙" if sender.checked else "☀️"

        rumps.notification(
            title="Dark Mode",
            subtitle="Setting Changed",
            message=f"Dark mode is now {'enabled' if sender.checked else 'disabled'}",
            data=None
        )

    def on_notifications_change(self, sender):
        """Handle notifications checkbox change."""
        print(f"Notifications: {'ENABLED' if sender.checked else 'DISABLED'}")

        if sender.checked:
            rumps.notification(
                title="Notifications Enabled",
                subtitle="You'll receive updates",
                message="Notification system is now active",
                data=None
            )
        else:
            print("Notifications disabled - no more alerts will be shown")

    def on_auto_save_change(self, sender):
        """Handle auto-save checkbox change."""
        print(f"Auto-save: {'ON' if sender.checked else 'OFF'}")

        if sender.checked:
            print("Auto-save enabled: Documents will be saved automatically")
        else:
            print("Auto-save disabled: Remember to save manually")

    def on_experimental_change(self, sender):
        """Handle experimental features checkbox change."""
        print(f"Experimental Features: {'ENABLED' if sender.checked else 'DISABLED'}")

        if sender.checked:
            print("Warning: Experimental features may be unstable!")
            # Enable debug mode automatically when experimental is enabled
            self.checkboxes['debug'].checked = True
        else:
            print("Experimental features disabled")

    def on_debug_change(self, sender):
        """Handle debug mode checkbox change."""
        print(f"Debug Mode: {'ON' if sender.checked else 'OFF'}")

        if sender.checked:
            print("Debug logging enabled")
            print("Verbose output activated")
        else:
            print("Debug logging disabled")

    def on_analytics_change(self, sender):
        """Handle analytics checkbox change."""
        print(f"Analytics: {'ENABLED' if sender.checked else 'DISABLED'}")

        if sender.checked:
            print("Anonymous usage data will be collected")
        else:
            print("Analytics disabled - no data will be sent")

    def on_show_hidden_change(self, sender):
        """Handle show hidden files checkbox change."""
        print(f"Show Hidden Files: {'ON' if sender.checked else 'OFF'}")

    def on_line_numbers_change(self, sender):
        """Handle line numbers checkbox change."""
        print(f"Line Numbers: {'SHOWN' if sender.checked else 'HIDDEN'}")

    def on_word_wrap_change(self, sender):
        """Handle word wrap checkbox change."""
        print(f"Word Wrap: {'ON' if sender.checked else 'OFF'}")

    def check_all(self, sender):
        """Check all checkboxes."""
        print("Checking all checkboxes...")

        for checkbox in self.checkboxes.values():
            checkbox.checked = True

        rumps.notification(
            title="All Settings",
            subtitle="Enabled",
            message="All checkboxes have been checked",
            data=None
        )

    def uncheck_all(self, sender):
        """Uncheck all checkboxes."""
        print("Unchecking all checkboxes...")

        for checkbox in self.checkboxes.values():
            checkbox.checked = False

        rumps.notification(
            title="All Settings",
            subtitle="Disabled",
            message="All checkboxes have been unchecked",
            data=None
        )

    def toggle_all(self, sender):
        """Toggle all checkboxes."""
        print("Toggling all checkboxes...")

        for checkbox in self.checkboxes.values():
            checkbox.toggle()

        rumps.notification(
            title="All Settings",
            subtitle="Toggled",
            message="All checkboxes have been toggled",
            data=None
        )

    def reset_defaults(self, sender):
        """Reset all checkboxes to their default states."""
        print("Resetting to default settings...")

        # Default states
        defaults = {
            'dark_mode': False,
            'notifications': True,
            'auto_save': True,
            'experimental': False,
            'debug': False,
            'analytics': True,
            'show_hidden': False,
            'line_numbers': True,
            'word_wrap': False
        }

        for name, default_checked in defaults.items():
            if name in self.checkboxes:
                self.checkboxes[name].checked = default_checked

        rumps.notification(
            title="Settings Reset",
            subtitle="Defaults Restored",
            message="All settings have been reset to their default values",
            data=None
        )

    def show_state(self, sender):
        """Show current state of all checkboxes."""
        print("\n" + "="*40)
        print("CURRENT CHECKBOX STATES:")
        print("="*40)

        for name, checkbox in self.checkboxes.items():
            status = "CHECKED" if checkbox.checked else "UNCHECKED"
            print(f"{checkbox.title}: {status}")

        print("="*40 + "\n")

        # Count checked checkboxes
        checked_count = sum(1 for checkbox in self.checkboxes.values() if checkbox.checked)
        total_count = len(self.checkboxes)

        rumps.notification(
            title="Current Settings",
            subtitle=f"{checked_count}/{total_count} options enabled",
            message="Check console for detailed state information",
            data=None
        )


if __name__ == "__main__":
    print("Checkbox Demo")
    print("=" * 15)
    print()
    print("This demo showcases the CheckboxMenuItem component:")
    print("• Native macOS checkboxes with checkmarks")
    print("• Boolean state management (checked/unchecked)")
    print("• Callback functions for state changes")
    print("• Programmatic state control")
    print("• Clean, familiar interface")
    print()
    print("Click the checkboxes in the menu to see them in action!")
    print()

    app = CheckboxDemoApp()
    app.run(debug=True)
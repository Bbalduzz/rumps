#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Checkbox Decorator example

Shows how to use the @rumps.checkbox decorator for creating checkboxes.
"""

import rumps


class DecoratorCheckboxApp(rumps.App):
    def __init__(self):
        super(DecoratorCheckboxApp, self).__init__("Checkbox Decorators", title="☑️")

    @rumps.checkbox("Settings", "Dark Mode", checked=False)
    def dark_mode_checkbox(self, sender):
        """Handle dark mode checkbox using decorator."""
        print(f"Dark mode: {'CHECKED' if sender.checked else 'UNCHECKED'}")
        self.title = "🌙" if sender.checked else "☀️"

    @rumps.checkbox("Settings", "Notifications", checked=True)
    def notifications_checkbox(self, sender):
        """Handle notifications checkbox using decorator."""
        print(f"Notifications: {'CHECKED' if sender.checked else 'UNCHECKED'}")
        if sender.checked:
            rumps.notification("Settings", "Notifications Enabled", "You'll receive updates")

    @rumps.checkbox("Features", "Debug Mode", checked=False)
    def debug_checkbox(self, sender):
        """Handle debug mode checkbox using decorator."""
        print(f"Debug mode: {'CHECKED' if sender.checked else 'UNCHECKED'}")
        if sender.checked:
            print("Debug logging enabled - verbose output activated")
        else:
            print("Debug logging disabled")

    @rumps.checkbox("Features", "Auto-save", checked=True)
    def auto_save_checkbox(self, sender):
        """Handle auto-save checkbox using decorator."""
        print(f"Auto-save: {'CHECKED' if sender.checked else 'UNCHECKED'}")

    @rumps.checkbox("View", "Show Hidden Files", checked=False)
    def show_hidden_checkbox(self, sender):
        """Handle show hidden files checkbox using decorator."""
        print(f"Show hidden files: {'CHECKED' if sender.checked else 'UNCHECKED'}")

    @rumps.checkbox("View", "Line Numbers", checked=True)
    def line_numbers_checkbox(self, sender):
        """Handle line numbers checkbox using decorator."""
        print(f"Line numbers: {'CHECKED' if sender.checked else 'UNCHECKED'}")

    @rumps.clicked("Show Status")
    def show_status(self, sender):
        """Show current status of all checkboxes."""
        print("\n" + "="*30)
        print("CURRENT SETTINGS:")
        print("="*30)

        # Access checkboxes through menu path
        try:
            settings_menu = self.menu["Settings"]
            features_menu = self.menu["Features"]
            view_menu = self.menu["View"]

            dark_mode = settings_menu["Dark Mode"]
            notifications = settings_menu["Notifications"]
            debug_mode = features_menu["Debug Mode"]
            auto_save = features_menu["Auto-save"]
            show_hidden = view_menu["Show Hidden Files"]
            line_numbers = view_menu["Line Numbers"]

            print(f"Dark Mode: {'✓' if dark_mode.checked else '✗'}")
            print(f"Notifications: {'✓' if notifications.checked else '✗'}")
            print(f"Debug Mode: {'✓' if debug_mode.checked else '✗'}")
            print(f"Auto-save: {'✓' if auto_save.checked else '✗'}")
            print(f"Show Hidden Files: {'✓' if show_hidden.checked else '✗'}")
            print(f"Line Numbers: {'✓' if line_numbers.checked else '✗'}")

        except (KeyError, AttributeError) as e:
            print(f"Error accessing menu items: {e}")

        print("="*30 + "\n")

    @rumps.clicked("Reset All")
    def reset_all(self, sender):
        """Reset all checkboxes to defaults."""
        try:
            # Access and reset checkboxes
            settings_menu = self.menu["Settings"]
            features_menu = self.menu["Features"]
            view_menu = self.menu["View"]

            settings_menu["Dark Mode"].checked = False
            settings_menu["Notifications"].checked = True
            features_menu["Debug Mode"].checked = False
            features_menu["Auto-save"].checked = True
            view_menu["Show Hidden Files"].checked = False
            view_menu["Line Numbers"].checked = True

            print("All settings reset to defaults")
            rumps.notification("Settings", "Reset Complete", "All checkboxes reset to default values")

        except (KeyError, AttributeError) as e:
            print(f"Error resetting checkboxes: {e}")

    @rumps.clicked("Quit")
    def quit_app(self, sender):
        rumps.quit_application()


if __name__ == "__main__":
    print("Checkbox Decorator Demo")
    print("=" * 25)
    print()
    print("This demo shows how to use the @rumps.checkbox decorator:")
    print("• Creates checkboxes using decorators")
    print("• Organizes checkboxes in menu hierarchies")
    print("• Clean, declarative syntax")
    print("• Native macOS checkbox appearance")
    print()
    print("Check the menu structure: Settings, Features, View")
    print()

    app = DecoratorCheckboxApp()
    app.run(debug=True)
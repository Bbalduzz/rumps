#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TextFieldMenuItem example demonstrating inline text input in menus.

This example shows how to use the new TextFieldMenuItem class to create
text input fields directly within menu items, without requiring modal dialogs.
"""

import rumps


class TextInputApp(rumps.App):
    def __init__(self):
        super(TextInputApp, self).__init__(
            "Text Input Demo",
            title="📝",  # Memo emoji as icon
            template=True
        )

        # Store the text values
        self.username = ""
        self.search_query = ""
        self.notes = ""

        self.build_menu()

    def build_menu(self):
        """Build the menu with various text input examples."""

        # Basic text input
        basic_menu = rumps.MenuItem("Basic Text Input")

        # Simple text field with clipboard support
        simple_textfield = rumps.TextFieldMenuItem(
            text="Type here and try Cmd+C/V/X",
            placeholder="Enter text (supports clipboard)",
            callback=self.on_simple_text_change,
            dimensions=(200, 22)
        )
        basic_menu.add(rumps.MenuItem("Text Field (with clipboard):"))
        basic_menu.add(simple_textfield)

        # Text field with placeholder
        placeholder_textfield = rumps.TextFieldMenuItem(
            text="",
            placeholder="Search...",
            callback=self.on_search_change,
            dimensions=(180, 20)
        )
        basic_menu.add(rumps.separator)
        basic_menu.add(rumps.MenuItem("Search Field:"))
        basic_menu.add(placeholder_textfield)

        # Secure text input (password field)
        secure_menu = rumps.MenuItem("Secure Input")

        password_field = rumps.TextFieldMenuItem(
            text="",
            placeholder="Password",
            callback=self.on_password_change,
            dimensions=(150, 22),
            secure=True
        )
        secure_menu.add(rumps.MenuItem("Password:"))
        secure_menu.add(password_field)

        # Form-like inputs
        form_menu = rumps.MenuItem("Form Example")

        # Username field
        username_field = rumps.TextFieldMenuItem(
            text="",
            placeholder="Username",
            callback=self.on_username_change,
            dimensions=(180, 20)
        )

        # Notes field (larger)
        notes_field = rumps.TextFieldMenuItem(
            text="",
            placeholder="Add notes...",
            callback=self.on_notes_change,
            dimensions=(250, 22)
        )

        form_menu.add(rumps.MenuItem("Username:"))
        form_menu.add(username_field)
        form_menu.add(rumps.separator)
        form_menu.add(rumps.MenuItem("Notes:"))
        form_menu.add(notes_field)
        form_menu.add(rumps.separator)
        form_menu.add(rumps.MenuItem("Submit Form", callback=self.submit_form))

        # Actions menu
        actions_menu = rumps.MenuItem("Actions")
        actions_menu.add(rumps.MenuItem("Show Current Values", callback=self.show_values))
        actions_menu.add(rumps.MenuItem("Clear All Fields", callback=self.clear_fields))

        # Build main menu
        self.menu = [
            basic_menu,
            rumps.separator,
            secure_menu,
            rumps.separator,
            form_menu,
            rumps.separator,
            actions_menu,
            rumps.separator,
            rumps.MenuItem("About", callback=self.show_about)
        ]

    # Callback methods for text fields
    def on_simple_text_change(self, sender):
        print(f"Simple text changed: '{sender.text}'")
        rumps.notification(
            title="Text Changed",
            subtitle="Simple Field",
            message=f"New text: {sender.text}",
            data=None
        )

    def on_search_change(self, sender):
        self.search_query = sender.text
        print(f"Search query: '{sender.text}'")
        if sender.text:
            rumps.notification(
                title="Search",
                subtitle="Query Updated",
                message=f"Searching for: {sender.text}",
                data=None
            )

    def on_password_change(self, sender):
        password_length = len(sender.text)
        print(f"Password changed (length: {password_length})")
        if password_length > 0:
            rumps.notification(
                title="Security",
                subtitle="Password Set",
                message=f"Password length: {password_length} characters",
                data=None
            )

    def on_username_change(self, sender):
        self.username = sender.text
        print(f"Username: '{sender.text}'")

    def on_notes_change(self, sender):
        self.notes = sender.text
        print(f"Notes: '{sender.text}'")

    def submit_form(self, sender):
        """Handle form submission."""
        if not self.username:
            rumps.alert("Form Error", "Please enter a username")
            return

        form_data = {
            "username": self.username,
            "notes": self.notes,
            "search_query": self.search_query
        }

        message = f"Username: {self.username}\n"
        if self.notes:
            message += f"Notes: {self.notes}\n"
        if self.search_query:
            message += f"Last Search: {self.search_query}"

        rumps.alert(
            title="Form Submitted",
            message=message,
            ok="OK"
        )

        print(f"Form submitted: {form_data}")

    def show_values(self, sender):
        """Show current values in all text fields."""
        values = f"Username: {self.username}\n"
        values += f"Notes: {self.notes}\n"
        values += f"Search Query: {self.search_query}"

        rumps.alert(
            title="Current Values",
            message=values,
            ok="OK"
        )

    def clear_fields(self, sender):
        """Clear all text fields."""
        self.username = ""
        self.notes = ""
        self.search_query = ""

        rumps.notification(
            title="Fields Cleared",
            subtitle="All text fields reset",
            message="All form fields have been cleared",
            data=None
        )

        print("All fields cleared")

    def show_about(self, sender):
        about_text = """TextFieldMenuItem Example

This example demonstrates the new TextFieldMenuItem class which allows
for inline text input directly within menu items.

Features demonstrated:
• Basic text input with callbacks
• Full clipboard support (⌘C/V/X, Ctrl+C/V/X)
• Placeholder text
• Secure password fields (paste only for security)
• Form-like interfaces
• Real-time text change notifications
• Keyboard shortcuts (Select All: ⌘A/Ctrl+A, Undo: ⌘Z/Ctrl+Z)

The TextFieldMenuItem provides a seamless way to collect user input
without requiring separate modal dialogs, with full system integration
including clipboard operations and standard text editing shortcuts."""

        rumps.alert(
            title="About Text Input Demo",
            message=about_text,
            ok="Got it!"
        )


# Decorator-based example
@rumps.textfield("Quick Input", text="", placeholder="Quick note...", dimensions=(200, 20))
def quick_input_callback(sender):
    """Example using the @textfield decorator."""
    print(f"Quick input: '{sender.text}'")
    if sender.text.strip():
        rumps.notification(
            title="Quick Note",
            subtitle="Saved",
            message=sender.text,
            data=None
        )


if __name__ == "__main__":
    print("Text Input Demo starting...")
    print("This example demonstrates inline text input in menus using TextFieldMenuItem.")
    print("Look for the 📝 icon in your menu bar.")
    print()
    print("Features to try:")
    print("• Type in the various text fields")
    print("• Try the secure password field")
    print("• Fill out the form and submit it")
    print("• Use the Quick Input decorator example")
    print()

    app = TextInputApp()

    # Add the decorator example to the menu
    app.menu.add(rumps.separator)
    app.menu.add(rumps.MenuItem("Decorator Example"))

    print("Running the app...")
    app.run(debug=True)
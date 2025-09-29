#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ComboBox Test for debugging ListMenuItem
"""

import rumps


class ComboBoxTestApp(rumps.App):
    def __init__(self):
        super(ComboBoxTestApp, self).__init__(
            "ComboBox Test",
            title="📋",
            template=True
        )

        self.build_menu()

    def build_menu(self):
        """Build a simple test menu with just a combobox."""

        # Test ComboBox (ListMenuItem)
        combo_box = rumps.ListMenuItem(
            items=["Apple", "Banana", "Cherry", "Date", "Elderberry"],
            callback=self.on_combo_selection
        )

        # Build menu
        self.menu = [
            rumps.MenuItem("Select a fruit:"),
            combo_box
        ]

    def on_combo_selection(self, sender):
        """Handle combo box selection."""
        selected = sender.get_selected_item()
        index = sender.get_selected_index()
        print(f"ComboBox selected: '{selected}' at index {index}")

        rumps.notification(
            title="ComboBox Selection",
            subtitle=f"Index: {index}",
            message=f"Selected: {selected}",
            data=None
        )


if __name__ == "__main__":
    print("ComboBox Test starting...")
    print("Testing ListMenuItem (ComboBox) functionality")
    print("Look for the 📋 icon in your menu bar")
    print("Click on the dropdown to test selection")
    print()

    app = ComboBoxTestApp()
    app.run(debug=True)
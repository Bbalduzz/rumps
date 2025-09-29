#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple test for debugging the new widgets
"""

import rumps
import os
import tempfile


def create_test_image():
    """Create a simple test image."""
    try:
        from PIL import Image
        temp_file = os.path.join(tempfile.gettempdir(), "test_image.png")
        img = Image.new('RGB', (80, 60), color=(255, 0, 0))  # Red square
        img.save(temp_file)
        return temp_file
    except ImportError:
        # Try to find a system icon
        system_icons = [
            "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/GenericDocumentIcon.icns"
        ]
        for icon_path in system_icons:
            if os.path.exists(icon_path):
                return icon_path
        return None


class SimpleTestApp(rumps.App):
    def __init__(self):
        super(SimpleTestApp, self).__init__(
            "Simple Test",
            title="🧪",
            template=True
        )

        self.build_menu()

    def build_menu(self):
        """Build a simple test menu."""

        # Test ComboBox (ListMenuItem)
        combo_box = rumps.ListMenuItem(
            items=["Option 1", "Option 2", "Option 3"],
            dimensions=(150, 30),
            callback=self.on_combo_selection
        )

        # Test Image
        image_path = create_test_image()
        if image_path:
            image_item = rumps.ImageMenuItem(
                image_path=image_path,
                dimensions=(60, 45),
                callback=self.on_image_click
            )
        else:
            image_item = None

        # Build menu
        self.menu = [
            rumps.MenuItem("ComboBox Test:"),
            combo_box,
            rumps.separator,
        ]

        if image_item:
            self.menu.extend([
                rumps.MenuItem("Image Test:"),
                image_item,
                rumps.separator,
            ])

        self.menu.append(rumps.MenuItem("Quit", callback=rumps.quit_application))

    def on_combo_selection(self, sender):
        """Handle combo box selection."""
        selected = sender.get_selected_item()
        print(f"ComboBox selected: {selected}")
        rumps.notification(
            title="ComboBox",
            subtitle="Selection",
            message=f"Selected: {selected}",
            data=None
        )

    def on_image_click(self, sender):
        """Handle image click."""
        print(f"Image clicked: {sender.image_path}")
        rumps.notification(
            title="Image",
            subtitle="Clicked",
            message=f"Image: {os.path.basename(sender.image_path)}",
            data=None
        )


if __name__ == "__main__":
    print("Simple Test starting...")
    print("Testing ComboBox and Image widgets")

    app = SimpleTestApp()
    app.run(debug=True)
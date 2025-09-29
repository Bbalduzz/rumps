#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple image example for rumps ImageMenuItem

This example shows ONLY an image in the menu when opened.
The image is displayed directly in the menu without any other items.
"""

import rumps
import os


class ImageOnlyApp(rumps.App):
    def __init__(self):
        super(ImageOnlyApp, self).__init__(
            "Image Example",
            title="🖼️",  # Picture frame emoji as the status bar icon
            template=True
        )

        # Create the image
        self.image_path = "/Users/edoardobalducci/Documents/work/rumps/examples/level_4.png"

        if self.image_path:
            print(f"Using image: {self.image_path}")
        else:
            print("No image available - will show text instead")

        self.build_menu()

    def build_menu(self):
        """Build menu with ONLY the image."""

        if self.image_path:
            # Create the image menu item
            image_item = rumps.ImageMenuItem(
                image_path=self.image_path,
                callback=self.on_image_click,
                dimensions=(200, 200),
                scale_mode='fill'
            )

            # Create a menu item with SF Symbol icon
            turtle_item = rumps.MenuItem("Turtle Item")
            turtle_icon = rumps.SFSymbol.named("turtle")
            if turtle_icon:
                turtle_item.set_icon(turtle_icon)

            # Menu contains the image and the SF Symbol menu item
            self.menu = [image_item, turtle_item]

        else:
            # Fallback if no image is available
            self.menu = [rumps.MenuItem("No image available")]

    def on_image_click(self, sender):
        """Handle image click."""
        print("Image was clicked!")

        # Show notification when image is clicked
        rumps.notification(
            title="Image Clicked!",
            subtitle="Image Example",
            message="You clicked on the image in the menu",
            data=None
        )


if __name__ == "__main__":
    print("Image Example starting...")
    print("This app shows ONLY an image in the menu.")
    print("Click on the 🖼️ icon in your menu bar to see the image.")
    print("Then click on the image itself to see the callback in action.")
    print()

    app = ImageOnlyApp()

    print("App created successfully!")
    print("Running the app...")

    app.run(debug=True)
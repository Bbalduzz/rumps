#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Card Example for rumps CardMenuItem

This example demonstrates the CardMenuItem widget which creates hoverable
list tiles with text and optional leading/trailing icons.
"""

import rumps
import os


class CardExampleApp(rumps.App):
    def __init__(self):
        super(CardExampleApp, self).__init__(
            "Card Example",
            title="📄",  # Document emoji as the status bar icon
            template=True
        )

        self.build_menu()

    def build_menu(self):
        """Build menu with various card examples."""

        # Get the icon path (assuming we have some icon files)
        icon_path = "/Users/edoardobalducci/Documents/work/rumps/examples/pony.jpg"

        # Shazam card - blue circle with icon
        shazam_card = rumps.CardMenuItem(
            title="Shazam",
            leading_icon=icon_path if os.path.exists(icon_path) else None,
            icon_color=(0.0, 0.5, 1.0, 1.0),  # Blue color like in the image
            callback=self.on_shazam_card_click
        )

        # Start Pomodoro card - red/orange circle with icon
        pomodoro_card = rumps.CardMenuItem(
            title="Start Pomodoro",
            # leading_icon=icon_path if os.path.exists(icon_path) else None,
            # icon_color=(1.0, 0.3, 0.2, 1.0),  # Red/orange color like in the image
            callback=self.on_pomodoro_card_click
        )

        # Simple card without icon
        simple_card = rumps.CardMenuItem(
            title="No Icon Card",
            callback=self.on_simple_card_click
        )

        # # Card with leading icon
        # leading_icon_card = rumps.CardMenuItem(
        #     title="Card with Leading Icon",
        #     subtitle="Has an icon on the left",
        #     leading_icon=icon_path if os.path.exists(icon_path) else None,
        #     callback=self.on_leading_icon_card_click
        # )

        # # Card with trailing icon
        # trailing_icon_card = rumps.CardMenuItem(
        #     title="Card with Trailing Icon",
        #     subtitle="Has an icon on the right",
        #     trailing_icon=icon_path if os.path.exists(icon_path) else None,
        #     callback=self.on_trailing_icon_card_click
        # )

        # # Card with both icons
        # both_icons_card = rumps.CardMenuItem(
        #     title="Card with Both Icons",
        #     subtitle="Icons on both sides",
        #     leading_icon=icon_path if os.path.exists(icon_path) else None,
        #     trailing_icon=icon_path if os.path.exists(icon_path) else None,
        #     callback=self.on_both_icons_card_click
        # )

        # # Card with custom dimensions and background
        # custom_card = rumps.CardMenuItem(
        #     title="Custom Styled Card",
        #     subtitle="Different size and background",
        #     dimensions=(300, 80),
        #     background_color=(0.95, 0.95, 1.0, 1.0),  # Light blue background
        #     hover_color=(0.9, 0.9, 1.0, 1.0),  # Slightly darker blue on hover
        #     callback=self.on_custom_card_click
        # )

        # Card with long text to test text wrapping
        long_text_card = rumps.CardMenuItem(
            title="Card with Very Long Title That Might Need Truncation",
            # subtitle="This subtitle is also quite long to test how the layout handles longer text content",
            callback=self.on_long_text_card_click
        )

        # Build menu
        self.menu = [
            rumps.MenuItem("Card Examples:"),
            rumps.separator,
            shazam_card,
            pomodoro_card,
            simple_card,
        ]

    def on_simple_card_click(self, sender):
        """Handle simple card click."""
        print("No Icon card clicked!")

        rumps.notification(
            title="Card Clicked",
            subtitle="Simple Card",
            message="You clicked the card without an icon",
            data=None
        )

    def on_shazam_card_click(self, sender):
        """Handle Shazam card click."""
        print("Shazam card clicked!")

        rumps.notification(
            title="Shazam",
            subtitle="Listening...",
            message="Identifying music playing nearby",
            data=None
        )

    def on_pomodoro_card_click(self, sender):
        """Handle Pomodoro card click."""
        print("Start Pomodoro card clicked!")

        rumps.notification(
            title="Pomodoro Started",
            subtitle="Focus Time",
            message="25-minute focus session has begun",
            data=None
        )

    def on_leading_icon_card_click(self, sender):
        """Handle leading icon card click."""
        print("Leading icon card clicked!")

        rumps.notification(
            title="Card Clicked",
            subtitle="Leading Icon Card",
            message="You clicked the card with a leading icon",
            data=None
        )

    def on_trailing_icon_card_click(self, sender):
        """Handle trailing icon card click."""
        print("Trailing icon card clicked!")

        rumps.notification(
            title="Card Clicked",
            subtitle="Trailing Icon Card",
            message="You clicked the card with a trailing icon",
            data=None
        )

    def on_both_icons_card_click(self, sender):
        """Handle both icons card click."""
        print("Both icons card clicked!")

        rumps.notification(
            title="Card Clicked",
            subtitle="Both Icons Card",
            message="You clicked the card with both icons",
            data=None
        )

    def on_custom_card_click(self, sender):
        """Handle custom card click."""
        print("Custom card clicked!")

        rumps.notification(
            title="Card Clicked",
            subtitle="Custom Styled Card",
            message="You clicked the custom styled card",
            data=None
        )

    def on_long_text_card_click(self, sender):
        """Handle long text card click."""
        print("Long text card clicked!")

        rumps.notification(
            title="Card Clicked",
            subtitle="Long Text Card",
            message="You clicked the card with long text",
            data=None
        )


if __name__ == "__main__":
    print("Card Example starting...")
    print("This app demonstrates various CardMenuItem widgets.")
    print("Look for the 📄 icon in your menu bar")
    print("Click on the cards to see them in action")
    print("Hover over cards to see hover effects")
    print()

    app = CardExampleApp()
    app.run(debug=True)
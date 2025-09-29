#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for the new SFSymbol constructor API
"""

import rumps


class TestSFSymbolApp(rumps.App):
    def __init__(self):
        super(TestSFSymbolApp, self).__init__(
            "SFSymbol Test",
            title="🐢"
        )

        # Test the new constructor syntax
        sfsymbol_item = rumps.SFSymbol(
            name="turtle",
            rendering="monochrome",
            color="#ffffff"
        )

        # Set app icon using new syntax
        self.icon = sfsymbol_item

        self.build_menu()

    def build_menu(self):
        """Build test menu with various SFSymbol configurations."""
        menu_items = []

        # Test different rendering modes
        test_configs = [
            ("gear", "automatic", None, "Automatic Gear"),
            ("heart.fill", "monochrome", "#ff0000", "Red Monochrome Heart"),
            ("house.fill", "hierarchical", "#00ff00", "Green Hierarchical House"),
            ("star.fill", "palette", "#ffff00", "Yellow Palette Star"),
            ("folder.fill", "multicolor", None, "Multicolor Folder"),
        ]

        for symbol_name, rendering, color, title in test_configs:
            item = rumps.MenuItem(title, callback=self.on_symbol_click)

            # Create SFSymbol with new constructor
            symbol = rumps.SFSymbol(
                name=symbol_name,
                rendering=rendering,
                color=color
            )

            # Set icon using SFSymbol instance
            item.set_icon(symbol)
            menu_items.append(item)

        menu_items.append(rumps.separator)

        # Test backward compatibility with SFSymbol.named()
        legacy_item = rumps.MenuItem("Legacy Named", callback=self.on_symbol_click)
        legacy_icon = rumps.SFSymbol.named("tortoise")
        if legacy_icon:
            legacy_item.set_icon(legacy_icon)
        menu_items.append(legacy_item)

        menu_items.append(rumps.separator)
        menu_items.append(rumps.MenuItem("Quit", callback=rumps.quit_application))

        self.menu = menu_items

    def on_symbol_click(self, sender):
        """Handle menu item clicks."""
        print(f"Clicked: {sender.title}")

        rumps.notification(
            title="SFSymbol Test",
            subtitle=f"Clicked: {sender.title}",
            message="Testing new SFSymbol constructor API",
            data=None
        )


if __name__ == "__main__":
    print("Testing new SFSymbol constructor API...")
    print()
    print("Usage patterns being tested:")
    print("1. sfsymbol_item = rumps.SFSymbol(name='turtle', rendering='monochrome', color='#ffffff')")
    print("2. app.icon = sfsymbol_item")
    print("3. menu_item.set_icon(sfsymbol_item)")
    print()

    app = TestSFSymbolApp()
    app.run(debug=True)
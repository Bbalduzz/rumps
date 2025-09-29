#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple test for the exact SFSymbol usage pattern requested
"""

import rumps

# Test the exact syntax requested by the user
sfsymbol_item = rumps.SFSymbol(
    name="turtle",
    rendering="monochrome",  # hierarchical
    color="#ffffff"
)

print("SFSymbol created successfully!")
print(f"Symbol: {sfsymbol_item}")

# Test that it can be used in an app
class SimpleApp(rumps.App):
    def __init__(self):
        super(SimpleApp, self).__init__("Simple Test")

        # Use the SFSymbol as app icon
        self.icon = sfsymbol_item

        # Create menu with SFSymbol
        test_item = rumps.MenuItem("Test Item")
        test_item.set_icon(sfsymbol_item)

        self.menu = [test_item, rumps.MenuItem("Quit", callback=rumps.quit_application)]

if __name__ == "__main__":
    print("Testing the exact syntax pattern:")
    print("sfsymbol_item = rumps.SFSymbol(name='turtle', rendering='monochrome', color='#ffffff')")

    app = SimpleApp()
    print("App created successfully with SFSymbol!")
    print("Run with: python simple_test.py (and look for turtle icon in menu bar)")
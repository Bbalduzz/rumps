#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comprehensive SF Symbol example for rumps

This example demonstrates the full SFSymbol API with all configuration options
following Apple's NSImage.SymbolConfiguration conventions.
"""

import rumps


class ComprehensiveSFSymbolApp(rumps.App):
    def __init__(self):
        super(ComprehensiveSFSymbolApp, self).__init__(
            "SF Symbol Comprehensive",
            title="⚙️"  # Fallback emoji
        )

        # Main app icon using your requested syntax
        app_icon = rumps.SFSymbol(
            name="turtle",
            rendering="monochrome",
            color="#ffffff"
        )
        self.icon = app_icon

        self.build_menu()

    def build_menu(self):
        """Build menu demonstrating all SFSymbol configuration options."""
        menu_items = []

        # Section 1: Basic rendering modes
        menu_items.append(rumps.MenuItem("=== Rendering Modes ==="))

        # Automatic (default)
        auto_item = rumps.MenuItem("Automatic Rendering", callback=self.on_click)
        auto_symbol = rumps.SFSymbol(name="gear")
        auto_item.set_icon(auto_symbol)
        menu_items.append(auto_item)

        # Monochrome
        mono_item = rumps.MenuItem("Monochrome Red", callback=self.on_click)
        mono_symbol = rumps.SFSymbol(
            name="heart.fill",
            rendering="monochrome",
            color="#FF0000"
        )
        mono_item.set_icon(mono_symbol)
        menu_items.append(mono_item)

        # Hierarchical
        hier_item = rumps.MenuItem("Hierarchical Blue", callback=self.on_click)
        hier_symbol = rumps.SFSymbol(
            name="house.fill",
            rendering="hierarchical",
            color="#007AFF"
        )
        hier_item.set_icon(hier_symbol)
        menu_items.append(hier_item)

        # Palette with multiple colors
        palette_item = rumps.MenuItem("Palette Multi-Color", callback=self.on_click)
        palette_symbol = rumps.SFSymbol(
            name="paintbrush.fill",
            rendering="palette",
            color=["#FF0000", "#00FF00", "#0000FF"]
        )
        palette_item.set_icon(palette_symbol)
        menu_items.append(palette_item)

        # Multicolor
        multi_item = rumps.MenuItem("Multicolor", callback=self.on_click)
        multi_symbol = rumps.SFSymbol(
            name="star.fill",
            rendering="multicolor"
        )
        multi_item.set_icon(multi_symbol)
        menu_items.append(multi_item)

        menu_items.append(rumps.separator)

        # Section 2: Font styling (text style and scale)
        menu_items.append(rumps.MenuItem("=== Font Styling ==="))

        # Text style examples
        text_styles = [
            ("headline", "Headline Style"),
            ("body", "Body Style"),
            ("caption1", "Caption Style")
        ]

        for style, title in text_styles:
            item = rumps.MenuItem(title, callback=self.on_click)
            symbol = rumps.SFSymbol(
                name="textformat",
                text_style=style,
                scale="large",
                rendering="hierarchical",
                color="#FF8800"
            )
            item.set_icon(symbol)
            menu_items.append(item)

        menu_items.append(rumps.separator)

        # Section 3: Point size and weight
        menu_items.append(rumps.MenuItem("=== Size & Weight ==="))

        # Weight examples
        weights = [
            ("light", "Light Weight"),
            ("regular", "Regular Weight"),
            ("bold", "Bold Weight"),
            ("heavy", "Heavy Weight")
        ]

        for weight, title in weights:
            item = rumps.MenuItem(title, callback=self.on_click)
            symbol = rumps.SFSymbol(
                name="textformat.size",
                point_size=20.0,
                weight=weight,
                rendering="monochrome",
                color="#8A2BE2"
            )
            item.set_icon(symbol)
            menu_items.append(item)

        menu_items.append(rumps.separator)

        # Section 4: Scale examples
        menu_items.append(rumps.MenuItem("=== Scale Variants ==="))

        scales = [
            ("small", "Small Scale"),
            ("medium", "Medium Scale"),
            ("large", "Large Scale")
        ]

        for scale, title in scales:
            item = rumps.MenuItem(title, callback=self.on_click)
            symbol = rumps.SFSymbol(
                name="circle.fill",
                scale=scale,
                rendering="hierarchical",
                color="#00CED1"
            )
            item.set_icon(symbol)
            menu_items.append(item)

        menu_items.append(rumps.separator)

        # Section 5: Color format examples
        menu_items.append(rumps.MenuItem("=== Color Formats ==="))

        # Hex color
        hex_item = rumps.MenuItem("Hex Color (#FF4500)", callback=self.on_click)
        hex_symbol = rumps.SFSymbol(
            name="number",
            rendering="monochrome",
            color="#FF4500"
        )
        hex_item.set_icon(hex_symbol)
        menu_items.append(hex_item)

        # RGB tuple (0-1 range)
        rgb_item = rumps.MenuItem("RGB Tuple (0-1)", callback=self.on_click)
        rgb_symbol = rumps.SFSymbol(
            name="eyedropper",
            rendering="hierarchical",
            color=(0.5, 0.8, 0.2)  # RGB in 0-1 range
        )
        rgb_item.set_icon(rgb_symbol)
        menu_items.append(rgb_item)

        # RGBA tuple (0-255 range)
        rgba_item = rumps.MenuItem("RGBA Tuple (0-255)", callback=self.on_click)
        rgba_symbol = rumps.SFSymbol(
            name="drop.fill",
            rendering="palette",
            color=(255, 128, 0, 180)  # RGBA in 0-255 range
        )
        rgba_item.set_icon(rgba_symbol)
        menu_items.append(rgba_item)

        menu_items.append(rumps.separator)

        # Section 6: Complex combinations
        menu_items.append(rumps.MenuItem("=== Complex Examples ==="))

        # All options combined
        complex_item = rumps.MenuItem("Everything Combined", callback=self.on_click)
        complex_symbol = rumps.SFSymbol(
            name="crown.fill",
            rendering="palette",
            color=["#FFD700", "#FFA500"],
            point_size=18.0,
            weight="semibold",
            accessibility_description="Golden crown with gradient colors"
        )
        complex_item.set_icon(complex_symbol)
        menu_items.append(complex_item)

        # Document symbol with text styling
        doc_item = rumps.MenuItem("Styled Document", callback=self.on_click)
        doc_symbol = rumps.SFSymbol(
            name="doc.fill",
            text_style="title2",
            scale="medium",
            rendering="hierarchical",
            color="#4169E1"
        )
        doc_item.set_icon(doc_symbol)
        menu_items.append(doc_item)

        menu_items.append(rumps.separator)
        menu_items.append(rumps.MenuItem("Quit", callback=rumps.quit_application))

        self.menu = menu_items

    def on_click(self, sender):
        """Handle menu item clicks."""
        print(f"Clicked: {sender.title}")

        rumps.notification(
            title="SF Symbol Demo",
            subtitle=f"Selected: {sender.title}",
            message="Comprehensive SFSymbol configuration showcase",
            data=None
        )


if __name__ == "__main__":
    print("Comprehensive SF Symbol Demo")
    print("=" * 40)
    print()
    print("This demo showcases all SFSymbol configuration options:")
    print("• Rendering modes: automatic, monochrome, hierarchical, palette, multicolor")
    print("• Font styling: text styles, scales, point sizes, weights")
    print("• Color formats: hex strings, RGB/RGBA tuples, multiple colors")
    print("• Complex combinations of all options")
    print()
    print("Based on Apple's NSImage.SymbolConfiguration API")
    print()

    app = ComprehensiveSFSymbolApp()
    app.run(debug=True)
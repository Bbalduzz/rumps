#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Image and List Demo for rumps

This example demonstrates the new ImageMenuItem and ListMenuItem widgets:
- ImageMenuItem: Display images directly in menus with click callbacks
- ListMenuItem: Scrollable lists within menu items
- Various image scaling modes and list configurations
- Dynamic content updates and interactions
"""

import rumps
import os
import tempfile
from datetime import datetime


def create_sample_image(filename, color=(255, 0, 0), size=(100, 100)):
    """Create a simple colored image for demonstration."""
    try:
        from PIL import Image
        img = Image.new('RGB', size, color)
        img.save(filename)
        return filename
    except ImportError:
        # Fallback: create a simple text file as placeholder
        with open(filename.replace('.png', '.txt'), 'w') as f:
            f.write(f"Sample image placeholder\nColor: {color}\nSize: {size}")
        return filename.replace('.png', '.txt')


class ImageListDemoApp(rumps.App):
    def __init__(self):
        super(ImageListDemoApp, self).__init__(
            "Image & List Demo",
            title="🖼️📋",  # Image and clipboard emojis
            template=True
        )

        # Create temporary sample images
        self.temp_dir = tempfile.mkdtemp()
        self.sample_images = self.create_sample_images()

        # Sample data for lists
        self.recent_files = [
            "document1.txt",
            "presentation.pptx",
            "spreadsheet.xlsx",
            "image.png",
            "video.mp4"
        ]

        self.color_list = [
            {"title": "🔴 Red", "value": "#FF0000"},
            {"title": "🟢 Green", "value": "#00FF00"},
            {"title": "🔵 Blue", "value": "#0000FF"},
            {"title": "🟡 Yellow", "value": "#FFFF00"},
            {"title": "🟣 Purple", "value": "#800080"},
            {"title": "🟠 Orange", "value": "#FFA500"},
            {"title": "⚫ Black", "value": "#000000"},
            {"title": "⚪ White", "value": "#FFFFFF"}
        ]

        self.build_menu()

    def create_sample_images(self):
        """Create sample images for demonstration."""
        images = {}

        # Create different colored sample images
        colors = [
            ("red", (255, 0, 0)),
            ("green", (0, 255, 0)),
            ("blue", (0, 0, 255)),
            ("yellow", (255, 255, 0))
        ]

        for name, color in colors:
            filename = os.path.join(self.temp_dir, f"sample_{name}.png")
            images[name] = create_sample_image(filename, color, (80, 60))

        return images

    def build_menu(self):
        """Build the menu with image and list demonstrations."""

        # Image demonstrations
        image_menu = rumps.MenuItem("Image Examples")

        # Basic image display
        if 'red' in self.sample_images:
            red_image = rumps.ImageMenuItem(
                image_path=self.sample_images['red'],
                dimensions=(80, 60),
                callback=self.on_image_click,
                scale_mode='fit'
            )
            image_menu.add(rumps.MenuItem("Red Image:"))
            image_menu.add(red_image)

        # Image with different scaling
        if 'blue' in self.sample_images:
            blue_image = rumps.ImageMenuItem(
                image_path=self.sample_images['blue'],
                dimensions=(120, 40),
                callback=self.on_image_click,
                scale_mode='fill'
            )
            image_menu.add(rumps.separator)
            image_menu.add(rumps.MenuItem("Blue Image (stretched):"))
            image_menu.add(blue_image)

        # Gallery-style images
        gallery_menu = rumps.MenuItem("Image Gallery")
        for name, path in self.sample_images.items():
            if os.path.exists(path):
                img = rumps.ImageMenuItem(
                    image_path=path,
                    dimensions=(60, 45),
                    callback=self.on_gallery_click
                )
                gallery_menu.add(img)

        image_menu.add(rumps.separator)
        image_menu.add(gallery_menu)

        # List demonstrations
        list_menu = rumps.MenuItem("List Examples")

        # Recent files list
        recent_files_list = rumps.ListMenuItem(
            items=self.recent_files,
            dimensions=(180, 30),
            callback=self.on_file_selected,
            allow_multiple_selection=False
        )
        list_menu.add(rumps.MenuItem("Recent Files:"))
        list_menu.add(recent_files_list)

        # Color picker list
        color_list = rumps.ListMenuItem(
            items=self.color_list,
            dimensions=(150, 30),
            callback=self.on_color_selected,
            allow_multiple_selection=False
        )
        list_menu.add(rumps.separator)
        list_menu.add(rumps.MenuItem("Color Picker:"))
        list_menu.add(color_list)

        # Dynamic list
        self.dynamic_list = rumps.ListMenuItem(
            items=["Item 1", "Item 2", "Item 3"],
            dimensions=(160, 30),
            callback=self.on_dynamic_selected
        )
        list_menu.add(rumps.separator)
        list_menu.add(rumps.MenuItem("Dynamic List:"))
        list_menu.add(self.dynamic_list)

        # List actions
        list_actions = rumps.MenuItem("List Actions")
        list_actions.add(rumps.MenuItem("Add Item", callback=self.add_dynamic_item))
        list_actions.add(rumps.MenuItem("Remove Last", callback=self.remove_dynamic_item))
        list_actions.add(rumps.MenuItem("Clear List", callback=self.clear_dynamic_list))

        # Combined examples
        combined_menu = rumps.MenuItem("Combined Examples")

        # File browser simulation
        file_browser = rumps.MenuItem("File Browser")

        # Add folder icon (if available)
        if 'yellow' in self.sample_images:
            folder_icon = rumps.ImageMenuItem(
                image_path=self.sample_images['yellow'],
                dimensions=(20, 20),
                callback=self.on_folder_click
            )
            file_browser.add(folder_icon)

        # Add file list
        file_list = rumps.ListMenuItem(
            items=["📁 Documents", "📁 Pictures", "📁 Downloads", "📄 readme.txt"],
            dimensions=(140, 30),
            callback=self.on_browser_select
        )
        file_browser.add(file_list)

        combined_menu.add(file_browser)

        # Actions menu
        actions_menu = rumps.MenuItem("Actions")
        actions_menu.add(rumps.MenuItem("Refresh Images", callback=self.refresh_images))
        actions_menu.add(rumps.MenuItem("Update Lists", callback=self.update_lists))
        actions_menu.add(rumps.MenuItem("Show Statistics", callback=self.show_stats))

        # Build main menu
        self.menu = [
            image_menu,
            rumps.separator,
            list_menu,
            list_actions,
            rumps.separator,
            combined_menu,
            rumps.separator,
            actions_menu,
            rumps.separator,
            rumps.MenuItem("About", callback=self.show_about)
        ]

    # Image callbacks
    def on_image_click(self, sender):
        """Handle image clicks."""
        image_path = sender.image_path
        print(f"Image clicked: {image_path}")

        if image_path:
            filename = os.path.basename(image_path)
            rumps.notification(
                title="Image Clicked",
                subtitle=filename,
                message=f"You clicked on image: {filename}",
                data=None
            )

    def on_gallery_click(self, sender):
        """Handle gallery image clicks."""
        self.on_image_click(sender)
        # Could implement image viewer, slideshow, etc.

    def on_folder_click(self, sender):
        """Handle folder icon clicks."""
        rumps.notification(
            title="Folder",
            subtitle="Navigate",
            message="Folder icon clicked - could open file browser",
            data=None
        )

    # List callbacks
    def on_file_selected(self, sender):
        """Handle file selection from recent files list."""
        selected_item = sender.get_selected_item()
        selected_index = sender.get_selected_index()

        if selected_item:
            print(f"File selected: {selected_item} (index: {selected_index})")
            rumps.notification(
                title="File Selected",
                subtitle=selected_item,
                message=f"You selected: {selected_item}",
                data=None
            )

    def on_color_selected(self, sender):
        """Handle color selection."""
        selected_item = sender.get_selected_item()

        if selected_item and isinstance(selected_item, dict):
            color_name = selected_item['title']
            color_value = selected_item['value']
            print(f"Color selected: {color_name} ({color_value})")

            rumps.notification(
                title="Color Selected",
                subtitle=color_name,
                message=f"Color value: {color_value}",
                data=None
            )

    def on_dynamic_selected(self, sender):
        """Handle dynamic list selection."""
        selected_item = sender.get_selected_item()
        if selected_item:
            rumps.notification(
                title="Dynamic List",
                subtitle="Item Selected",
                message=f"Selected: {selected_item}",
                data=None
            )

    def on_browser_select(self, sender):
        """Handle file browser selection."""
        selected_item = sender.get_selected_item()
        if selected_item:
            rumps.notification(
                title="File Browser",
                subtitle="Navigation",
                message=f"Opening: {selected_item}",
                data=None
            )

    # Action callbacks
    def add_dynamic_item(self, sender):
        """Add item to dynamic list."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        new_item = f"Item {timestamp}"
        self.dynamic_list.add_item(new_item)

        rumps.notification(
            title="List Updated",
            subtitle="Item Added",
            message=f"Added: {new_item}",
            data=None
        )

    def remove_dynamic_item(self, sender):
        """Remove last item from dynamic list."""
        items = self.dynamic_list.get_items()
        if items:
            last_item = items[-1]
            self.dynamic_list.remove_item(len(items) - 1)

            rumps.notification(
                title="List Updated",
                subtitle="Item Removed",
                message=f"Removed: {last_item}",
                data=None
            )

    def clear_dynamic_list(self, sender):
        """Clear dynamic list."""
        self.dynamic_list.clear_items()

        rumps.notification(
            title="List Updated",
            subtitle="List Cleared",
            message="All items removed from dynamic list",
            data=None
        )

    def refresh_images(self, sender):
        """Refresh sample images."""
        # Could regenerate images, load new ones, etc.
        rumps.notification(
            title="Images",
            subtitle="Refreshed",
            message="Sample images have been refreshed",
            data=None
        )

    def update_lists(self, sender):
        """Update list contents."""
        # Add timestamp to recent files
        timestamp = datetime.now().strftime("%H:%M")
        new_file = f"new_file_{timestamp}.txt"
        self.recent_files.insert(0, new_file)

        # Keep only last 10 files
        self.recent_files = self.recent_files[:10]

        rumps.notification(
            title="Lists Updated",
            subtitle="New Content",
            message=f"Added: {new_file}",
            data=None
        )

    def show_stats(self, sender):
        """Show statistics about images and lists."""
        num_images = len([path for path in self.sample_images.values() if os.path.exists(path)])
        num_list_items = len(self.recent_files) + len(self.color_list) + len(self.dynamic_list.get_items())

        stats = f"""Image & List Statistics

Images:
• Sample images: {num_images}
• Total image menu items: {num_images}

Lists:
• Recent files: {len(self.recent_files)} items
• Colors: {len(self.color_list)} items
• Dynamic list: {len(self.dynamic_list.get_items())} items
• Total list items: {num_list_items}

Memory:
• Temp directory: {self.temp_dir}"""

        rumps.alert(
            title="Statistics",
            message=stats,
            ok="OK"
        )

    def show_about(self, sender):
        about_text = """Image & List Demo

This demo showcases the new ImageMenuItem and ListMenuItem widgets:

🖼️ IMAGEMENUITEM FEATURES:
• Display images directly in menus
• Multiple scaling modes (fit, fill, stretch)
• Click callbacks for interactive images
• Support for common image formats
• Background color customization

📋 LISTMENUITEM FEATURES:
• Scrollable lists within menu items
• Single and multiple selection modes
• Dynamic item management (add/remove)
• Custom item data (strings or dictionaries)
• Selection callbacks with item details

🔧 INTEGRATION:
• Combine images and lists for rich UIs
• File browsers, galleries, pickers
• Dynamic content updates
• Memory-efficient design

Both widgets integrate seamlessly with the existing rumps
architecture and support all standard menu operations."""

        rumps.alert(
            title="About Image & List Demo",
            message=about_text,
            ok="Got it!"
        )

    def __del__(self):
        """Cleanup temporary files."""
        try:
            import shutil
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass


# Decorator examples
@rumps.image("Decorator Examples", "Sample Image",
             image_path=None, dimensions=(60, 40))
def decorator_image_callback(sender):
    """Example using the @image decorator."""
    print(f"Decorator image clicked!")
    rumps.notification(
        title="Decorator Image",
        subtitle="Clicked",
        message="Image created with @rumps.image decorator",
        data=None
    )


@rumps.list_menu("Decorator Examples", "Sample List",
                 items=["Option 1", "Option 2", "Option 3"],
                 dimensions=(140, 60))
def decorator_list_callback(sender):
    """Example using the @list_menu decorator."""
    selected = sender.get_selected_item()
    print(f"Decorator list selection: {selected}")
    rumps.notification(
        title="Decorator List",
        subtitle="Selection",
        message=f"Selected: {selected}",
        data=None
    )


if __name__ == "__main__":
    print("Image & List Demo starting...")
    print("This demo shows ImageMenuItem and ListMenuItem widgets.")
    print("Look for the 🖼️📋 icon in your menu bar.")
    print()
    print("Features to try:")
    print("• Click on images to see callbacks")
    print("• Select items from lists")
    print("• Add/remove items from dynamic list")
    print("• Explore the file browser simulation")
    print("• Check out the decorator examples")
    print()

    app = ImageListDemoApp()

    # Add decorator examples to the menu
    app.menu.add(rumps.separator)
    app.menu.add(rumps.MenuItem("Decorator Examples"))

    print("Running the app...")
    app.run(debug=True)
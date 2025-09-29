#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Complete rumps widgets showcase example.

This example demonstrates all available widgets and features in rumps:
- MenuItem (basic, with icons, callbacks, keyboard shortcuts)
- SliderMenuItem (sliders in menus)
- TextFieldMenuItem (inline text input fields)
- ImageMenuItem (image display in menus)
- ListMenuItem (scrollable lists in menus)
- SeparatorMenuItem (visual separators)
- Window (input dialogs)
- Alert (simple alerts)
- Timer (background timers)
- Console output (instead of system notifications)
- App (main statusbar application)
"""

import rumps
import os
import tempfile
from datetime import datetime

def safe_notification(title, subtitle="", message="", data=None):
    """Print notification content instead of showing actual notifications."""
    print(f"[{title}] {message}")

class AllWidgetsApp(rumps.App):
    def __init__(self):
        super(AllWidgetsApp, self).__init__(
            "All Widgets Demo",
            title="🎛️",  # Control knobs emoji as icon
            template=True
        )

        # Initialize timer counter
        self.timer_count = 0

        # Create timer for demonstration
        self.demo_timer = rumps.Timer(self.timer_callback, 5)

        # Build the menu
        self.build_menu()

    def build_menu(self):
        """Build the complete menu with all widget types."""

        # Basic MenuItems
        basic_menu = rumps.MenuItem("Basic MenuItems")
        basic_menu.add(rumps.MenuItem("Simple Item", callback=self.simple_callback))
        basic_menu.add(rumps.MenuItem("Item with Key", callback=self.key_callback, key="k"))

        # MenuItem with icon (if icon file exists)
        icon_item = rumps.MenuItem("Item with Icon", callback=self.icon_callback)
        # Try to set an icon if available
        try:
            # Use a small colored circle as demo icon
            icon_item.set_icon(None)  # No icon for demo
        except:
            pass
        basic_menu.add(icon_item)

        # MenuItem states
        state_item = rumps.MenuItem("Toggle State", callback=self.toggle_state)
        state_item.state = 0  # Start unchecked
        basic_menu.add(state_item)

        # Hidden/Show MenuItem
        hidden_item = rumps.MenuItem("Toggle Visibility", callback=self.toggle_visibility)
        basic_menu.add(hidden_item)
        self.hidden_demo_item = rumps.MenuItem("I can be hidden!", callback=self.simple_callback)
        basic_menu.add(self.hidden_demo_item)

        # Separator demonstration
        basic_menu.add(rumps.separator)
        basic_menu.add(rumps.MenuItem("After separator", callback=self.simple_callback))

        # SliderMenuItem demonstrations
        slider_menu = rumps.MenuItem("Sliders")

        # Basic slider
        volume_slider = rumps.SliderMenuItem(
            value=50,
            min_value=0,
            max_value=100,
            callback=self.volume_callback
        )
        slider_menu.add(volume_slider)

        # Custom dimension slider
        brightness_slider = rumps.SliderMenuItem(
            value=75,
            min_value=0,
            max_value=100,
            callback=self.brightness_callback,
            dimensions=(200, 20)
        )
        slider_menu.add(brightness_slider)

        # TextFieldMenuItem demonstrations
        textfield_menu = rumps.MenuItem("Text Fields")

        # Basic text field
        basic_textfield = rumps.TextFieldMenuItem(
            text="Type here...",
            placeholder="Enter text",
            callback=self.textfield_callback,
            dimensions=(180, 20)
        )
        textfield_menu.add(basic_textfield)

        # Secure text field (password)
        secure_textfield = rumps.TextFieldMenuItem(
            text="",
            placeholder="Password",
            callback=self.secure_textfield_callback,
            dimensions=(150, 20),
            secure=True
        )
        textfield_menu.add(secure_textfield)

        # ImageMenuItem demonstrations
        image_menu = rumps.MenuItem("Images")

        # Sample image (create a simple one if PIL available)
        sample_image_path = "/Users/edoardobalducci/Documents/work/rumps/examples/rumps_example.png"
        if sample_image_path:
            sample_image = rumps.ImageMenuItem(
                image_path=sample_image_path,
                callback=self.image_callback
            )
            image_menu.add(sample_image)

        # ListMenuItem demonstrations
        list_menu = rumps.MenuItem("Lists")

        # Simple list
        simple_list = rumps.ListMenuItem(
            items=["Option A", "Option B", "Option C", "Option D"],
            dimensions=(150, 80),
            callback=self.list_callback
        )
        list_menu.add(simple_list)

        # List with dictionaries
        color_list = rumps.ListMenuItem(
            items=[
                {"title": "🔴 Red", "value": "#FF0000"},
                {"title": "🟢 Green", "value": "#00FF00"},
                {"title": "🔵 Blue", "value": "#0000FF"}
            ],
            dimensions=(120, 60),
            callback=self.color_list_callback
        )
        list_menu.add(color_list)

        # Window demonstrations
        window_menu = rumps.MenuItem("Windows & Dialogs")
        window_menu.add(rumps.MenuItem("Text Input Window", callback=self.show_text_window))
        window_menu.add(rumps.MenuItem("Secure Input Window", callback=self.show_secure_window))
        window_menu.add(rumps.MenuItem("Custom Button Window", callback=self.show_custom_window))

        # Alert demonstrations
        alert_menu = rumps.MenuItem("Alerts")
        alert_menu.add(rumps.MenuItem("Simple Alert", callback=self.show_simple_alert))
        alert_menu.add(rumps.MenuItem("Alert with Buttons", callback=self.show_button_alert))
        alert_menu.add(rumps.MenuItem("Alert with Icon", callback=self.show_icon_alert))

        # Timer demonstrations
        timer_menu = rumps.MenuItem("Timers")
        timer_menu.add(rumps.MenuItem("Start Timer", callback=self.start_timer))
        timer_menu.add(rumps.MenuItem("Stop Timer", callback=self.stop_timer))
        timer_menu.add(rumps.MenuItem("Show Timer Status", callback=self.show_timer_status))

        # Note: Notification demos removed per user request

        # App control demonstrations
        app_menu = rumps.MenuItem("App Controls")
        app_menu.add(rumps.MenuItem("Change Title", callback=self.change_title))
        app_menu.add(rumps.MenuItem("Change Icon", callback=self.change_icon))
        app_menu.add(rumps.MenuItem("Show Menu Programmatically", callback=self.show_menu_demo))

        # Build main menu
        self.menu = [
            basic_menu,
            rumps.separator,
            slider_menu,
            textfield_menu,
            image_menu,
            list_menu,
            rumps.separator,
            window_menu,
            alert_menu,
            rumps.separator,
            timer_menu,
            rumps.separator,
            app_menu,
            rumps.separator,
            rumps.MenuItem("About This Demo", callback=self.show_about)
        ]

    # Callback methods for MenuItem demonstrations
    def simple_callback(self, sender):
        print(f"Simple callback triggered by: {sender.title}")
        safe_notification("Simple Callback", "", f"Clicked: {sender.title}")

    def key_callback(self, sender):
        print(f"Keyboard shortcut (⌘K) callback: {sender.title}")
        safe_notification("Keyboard Shortcut", "", "You pressed ⌘K!")

    def icon_callback(self, sender):
        print(f"Icon item callback: {sender.title}")
        safe_notification("Icon Item", "", "Icon menu item clicked")

    def toggle_state(self, sender):
        # Toggle between checked (1), unchecked (0), and mixed (-1)
        if sender.state == 0:
            sender.state = 1
            state_text = "checked"
        elif sender.state == 1:
            sender.state = -1
            state_text = "mixed"
        else:
            sender.state = 0
            state_text = "unchecked"

        print(f"State toggled to: {state_text}")
        safe_notification("State Toggle", "", f"Item is now {state_text}")

    def toggle_visibility(self, sender):
        if self.hidden_demo_item.hidden:
            self.hidden_demo_item.show()
            safe_notification("Visibility", "", "Item is now visible")
        else:
            self.hidden_demo_item.hide()
            safe_notification("Visibility", "", "Item is now hidden")

    # SliderMenuItem callbacks
    def volume_callback(self, sender):
        value = int(sender.value)
        print(f"Volume slider: {value}")
        safe_notification("Volume", "", f"Volume set to {value}%")

    def brightness_callback(self, sender):
        value = int(sender.value)
        print(f"Brightness slider: {value}")
        safe_notification("Brightness", "", f"Brightness set to {value}%")

    # TextFieldMenuItem callbacks
    def textfield_callback(self, sender):
        text = sender.text
        print(f"Text field: '{text}'")
        safe_notification("Text Field", "", f"Text: {text}")

    def secure_textfield_callback(self, sender):
        text_length = len(sender.text)
        print(f"Secure text field (length: {text_length})")
        safe_notification("Secure Field", "", f"Password length: {text_length} chars")

    # ImageMenuItem callbacks
    def image_callback(self, sender):
        image_path = sender.image_path
        print(f"Image clicked: {image_path}")
        safe_notification("Image Clicked", "", f"Image: {os.path.basename(image_path) if image_path else 'Unknown'}")

    # ListMenuItem callbacks
    def list_callback(self, sender):
        selected_item = sender.get_selected_item()
        selected_index = sender.get_selected_index()
        print(f"List selection: {selected_item} (index: {selected_index})")
        safe_notification("List Selection", "", f"Selected: {selected_item}")

    def color_list_callback(self, sender):
        selected_item = sender.get_selected_item()
        if selected_item and isinstance(selected_item, dict):
            color_name = selected_item['title']
            color_value = selected_item['value']
            print(f"Color selected: {color_name} ({color_value})")
            safe_notification("Color Selected", color_name, f"Value: {color_value}")

    # Window demonstrations
    def show_text_window(self, sender):
        window = rumps.Window(
            message="Enter some text below:",
            title="Text Input Demo",
            default_text="Hello, rumps!",
            ok="Submit",
            cancel="Cancel",
            dimensions=(300, 20)
        )
        response = window.run()

        if response.clicked:
            print(f"User entered: {response.text}")
            safe_notification("Text Input", "", f"You entered: {response.text}")
        else:
            print("User cancelled")
            safe_notification("Text Input", "", "Input cancelled")

    def show_secure_window(self, sender):
        window = rumps.Window(
            message="Enter a password:",
            title="Secure Input Demo",
            default_text="",
            ok="Login",
            cancel="Cancel",
            secure=True,
            dimensions=(300, 20)
        )
        response = window.run()

        if response.clicked:
            print(f"Password length: {len(response.text)}")
            safe_notification("Secure Input", "", f"Password entered ({len(response.text)} characters)")
        else:
            safe_notification("Secure Input", "", "Login cancelled")

    def show_custom_window(self, sender):
        window = rumps.Window(
            message="Choose an option:",
            title="Custom Buttons Demo",
            default_text="Type something here...",
            ok="Option A",
            cancel="Option B"
        )
        window.add_button("Option C")
        window.add_button("Option D")

        response = window.run()

        button_names = ["Option B", "Option A", "Option C", "Option D"]
        button_name = button_names[response.clicked] if response.clicked < len(button_names) else f"Button {response.clicked}"

        print(f"User clicked: {button_name}, text: {response.text}")
        safe_notification("Custom Window", "", f"Clicked: {button_name}")

    # Alert demonstrations
    def show_simple_alert(self, sender):
        result = rumps.alert(
            title="Simple Alert",
            message="This is a simple alert dialog with just an OK button."
        )
        print(f"Alert result: {result}")
        safe_notification("Alert Demo", "", "Simple alert was shown")

    def show_button_alert(self, sender):
        result = rumps.alert(
            title="Multi-Button Alert",
            message="This alert has multiple buttons. Which do you choose?",
            ok="Yes",
            cancel="No",
            other="Maybe"
        )

        button_map = {1: "Yes", 0: "No", -1: "Maybe"}
        choice = button_map.get(result, f"Button {result}")
        print(f"User chose: {choice}")
        safe_notification("Multi-Button Alert", "", f"You chose: {choice}")

    def show_icon_alert(self, sender):
        # Alert with custom icon (if available)
        rumps.alert(
            title="Alert with Icon",
            message="This alert demonstrates icon capability.",
            ok="Cool!",
            icon_path=None  # No custom icon for demo
        )
        safe_notification("Icon Alert", "", "Icon alert was shown")

    # Timer demonstrations
    def start_timer(self, sender):
        if not self.demo_timer.is_alive():
            self.demo_timer.start()
            print("Timer started")
            safe_notification("Timer", "", "Timer started (5 second interval)")
        else:
            safe_notification("Timer", "", "Timer is already running")

    def stop_timer(self, sender):
        if self.demo_timer.is_alive():
            self.demo_timer.stop()
            print("Timer stopped")
            safe_notification("Timer", "", "Timer stopped")
        else:
            safe_notification("Timer", "", "Timer is not running")

    def show_timer_status(self, sender):
        status = "running" if self.demo_timer.is_alive() else "stopped"
        safe_notification("Timer Status", "", f"Timer is {status}. Count: {self.timer_count}")

    def timer_callback(self, timer):
        self.timer_count += 1
        print(f"Timer fired! Count: {self.timer_count}")
        safe_notification("Timer Callback", "", f"Timer fired #{self.timer_count}")

    # Notification demonstrations removed per user request

    # App control demonstrations
    def change_title(self, sender):
        current_time = datetime.now().strftime("%H:%M")
        self.title = f"🕐 {current_time}"
        safe_notification("Title Change", "", f"Title changed to show time: {current_time}")

    def change_icon(self, sender):
        # Cycle through different emoji icons
        icons = ["🎛️", "⚙️", "🔧", "🎚️", "📊"]
        current = self.title or "🎛️"
        try:
            current_index = icons.index(current)
            next_index = (current_index + 1) % len(icons)
        except ValueError:
            next_index = 0

        self.title = icons[next_index]
        safe_notification("Icon Change", "", f"Icon changed to: {icons[next_index]}")

    def show_menu_demo(self, sender):
        print("Showing menu programmatically")
        self.showMenu()
        safe_notification("Menu Demo", "", "Menu was shown programmatically")

    def show_about(self, sender):
        about_text = """This example demonstrates all widgets available in rumps:

• MenuItem: Basic menu items with callbacks, icons, shortcuts
• SliderMenuItem: Interactive sliders in menus
• TextFieldMenuItem: Inline text input fields (normal and secure)
• ImageMenuItem: Display images in menus with click callbacks
• ListMenuItem: Scrollable lists with selection callbacks
• SeparatorMenuItem: Visual menu separators
• Window: Text input dialogs (normal and secure)
• Alert: Simple notification dialogs
• Timer: Background timers with callbacks
• Console Output: Feedback printed to terminal instead of notifications
• App: Main statusbar application class

All widgets support extensive customization and callback functions."""

        rumps.alert(
            title="All Widgets Demo",
            message=about_text,
            ok="Got it!"
        )

# Decorator-based examples (alternative to class-based approach)
@rumps.clicked("Decorator Example")
def decorator_callback(sender):
    """Example of using the @clicked decorator for menu items."""
    print(f"Decorator callback: {sender.title}")
    safe_notification("Decorator", "", "This callback was registered with @rumps.clicked")

@rumps.timer(10)
def decorator_timer(timer):
    """Example of using the @timer decorator."""
    print("Decorator timer fired!")
    safe_notification("Decorator Timer", "", "Timer created with @rumps.timer decorator")

@rumps.slider(value=25, min_value=0, max_value=50)
def decorator_slider(sender):
    """Example of using the @slider decorator."""
    print(f"Decorator slider: {sender.value}")
    safe_notification("Decorator Slider", "", f"Slider value: {int(sender.value)}")

@rumps.textfield("Decorator Text Field", text="", placeholder="Type here...", dimensions=(180, 20))
def decorator_textfield(sender):
    """Example of using the @textfield decorator."""
    print(f"Decorator text field: '{sender.text}'")
    safe_notification("Decorator Text Field", "", f"Text: {sender.text}")

@rumps.image("Decorator Image", image_path=None, dimensions=(80, 50))
def decorator_image(sender):
    """Example of using the @image decorator."""
    print(f"Decorator image clicked!")
    safe_notification("Decorator Image", "", "Image created with @rumps.image")

@rumps.list_menu("Decorator List", items=["Item 1", "Item 2", "Item 3"], dimensions=(140, 60))
def decorator_list(sender):
    """Example of using the @list_menu decorator."""
    selected = sender.get_selected_item()
    print(f"Decorator list selection: {selected}")
    safe_notification("Decorator List", "", f"Selected: {selected}")

if __name__ == "__main__":
    # Add decorator example to global menu
    app = AllWidgetsApp()

    # Add separator and decorator examples
    app.menu.add(rumps.separator)
    app.menu.add(rumps.MenuItem("Decorator Examples"))
    app.menu["Decorator Examples"].add(rumps.MenuItem("Decorator Example", callback=decorator_callback))

    print("All Widgets Demo starting...")
    print("This example demonstrates every widget type available in rumps.")
    print("Check the menu bar for the 🎛️ icon and explore all the features!")
    print("Note: If you see notification errors, this is normal in development mode.")
    print("The example will still demonstrate all widgets properly.")

    # Run the app
    app.run(debug=True)
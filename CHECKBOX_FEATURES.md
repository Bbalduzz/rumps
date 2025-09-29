# Checkboxes in rumps

The `CheckboxMenuItem` class provides native macOS checkboxes for boolean settings and options in your menu bar applications.

## Features

- **Native macOS Checkboxes**: Uses system-provided checkmarks for familiar UI
- **Boolean State Management**: Simple checked/unchecked states
- **Callback Functions**: Execute functions when checkbox state changes
- **Programmatic Control**: Set state programmatically
- **Decorator Support**: Use `@rumps.checkbox` decorator for clean syntax
- **Property Management**: Get/set title and checked state properties

## Basic Usage

### Direct Instantiation

```python
import rumps

class MyApp(rumps.App):
    def __init__(self):
        super(MyApp, self).__init__("Checkbox App")

        # Basic checkbox
        self.dark_mode = rumps.CheckboxMenuItem(
            "Dark Mode",
            checked=False,
            callback=self.on_dark_mode
        )

        # Pre-checked checkbox
        self.notifications = rumps.CheckboxMenuItem(
            "Enable Notifications",
            checked=True,
            callback=self.on_notifications
        )

        self.menu = [
            self.dark_mode,
            self.notifications,
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]

    def on_dark_mode(self, sender):
        print(f"Dark mode: {'CHECKED' if sender.checked else 'UNCHECKED'}")
        self.title = "🌙" if sender.checked else "☀️"

    def on_notifications(self, sender):
        print(f"Notifications: {'CHECKED' if sender.checked else 'UNCHECKED'}")
```

### Using Decorators

```python
import rumps

class MyApp(rumps.App):
    def __init__(self):
        super(MyApp, self).__init__("Checkbox App")

    @rumps.checkbox("Settings", "Dark Mode", checked=False)
    def dark_mode_checkbox(self, sender):
        print(f"Dark mode: {'CHECKED' if sender.checked else 'UNCHECKED'}")

    @rumps.checkbox("Settings", "Notifications", checked=True)
    def notifications_checkbox(self, sender):
        print(f"Notifications: {'CHECKED' if sender.checked else 'UNCHECKED'}")
```

## Constructor Parameters

```python
CheckboxMenuItem(
    title="Checkbox",    # Label text
    checked=False,       # Initial state (True/False)
    callback=None        # Function called when checked/unchecked
)
```

## Properties and Methods

### Properties

- `title` - Get/set the label text
- `checked` - Get/set the current state (True/False)
- `callback` - Get the current callback function

### Methods

- `toggle()` - Switch the current checked state
- `set_callback(callback)` - Set the callback function

### Examples

```python
# Get current state
is_checked = my_checkbox.checked

# Set state programmatically
my_checkbox.checked = True

# Toggle the state
my_checkbox.toggle()

# Change the title
my_checkbox.title = "New Label"

# Set a new callback
my_checkbox.set_callback(my_new_function)
```

## Advanced Examples

### Settings Panel

```python
class SettingsApp(rumps.App):
    def __init__(self):
        super(SettingsApp, self).__init__("Settings")

        self.checkboxes = {
            'dark_mode': rumps.CheckboxMenuItem("Dark Mode", callback=self.on_setting_change),
            'notifications': rumps.CheckboxMenuItem("Notifications", checked=True, callback=self.on_setting_change),
            'auto_save': rumps.CheckboxMenuItem("Auto-save", checked=True, callback=self.on_setting_change),
        }

        self.menu = list(self.checkboxes.values()) + [
            rumps.separator,
            rumps.MenuItem("Reset All", callback=self.reset_all),
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]

    def on_setting_change(self, sender):
        print(f"{sender.title}: {'CHECKED' if sender.checked else 'UNCHECKED'}")

    def reset_all(self, sender):
        for checkbox in self.checkboxes.values():
            checkbox.checked = False
```

### Grouped Settings with Decorators

```python
class GroupedSettingsApp(rumps.App):
    def __init__(self):
        super(GroupedSettingsApp, self).__init__("Settings")

    @rumps.checkbox("Appearance", "Dark Mode")
    def dark_mode(self, sender):
        self.title = "🌙" if sender.checked else "☀️"

    @rumps.checkbox("Appearance", "High Contrast")
    def high_contrast(self, sender):
        print(f"High contrast: {'CHECKED' if sender.checked else 'UNCHECKED'}")

    @rumps.checkbox("Privacy", "Analytics", checked=True)
    def analytics(self, sender):
        print(f"Analytics: {'CHECKED' if sender.checked else 'UNCHECKED'}")

    @rumps.checkbox("Privacy", "Crash Reports", checked=True)
    def crash_reports(self, sender):
        print(f"Crash reports: {'CHECKED' if sender.checked else 'UNCHECKED'}")

    @rumps.clicked("Show Status")
    def show_status(self, sender):
        # Access checkboxes through menu structure
        appearance = self.menu["Appearance"]
        privacy = self.menu["Privacy"]

        print(f"Dark Mode: {'✓' if appearance['Dark Mode'].checked else '✗'}")
        print(f"Analytics: {'✓' if privacy['Analytics'].checked else '✗'}")
```

### View Options

```python
class ViewOptionsApp(rumps.App):
    def __init__(self):
        super(ViewOptionsApp, self).__init__("View Options")

    @rumps.checkbox("View", "Show Hidden Files")
    def show_hidden(self, sender):
        print(f"Show hidden files: {'ON' if sender.checked else 'OFF'}")

    @rumps.checkbox("View", "Line Numbers", checked=True)
    def line_numbers(self, sender):
        print(f"Line numbers: {'SHOWN' if sender.checked else 'HIDDEN'}")

    @rumps.checkbox("View", "Word Wrap")
    def word_wrap(self, sender):
        print(f"Word wrap: {'ON' if sender.checked else 'OFF'}")

    @rumps.checkbox("View", "Syntax Highlighting", checked=True)
    def syntax_highlighting(self, sender):
        print(f"Syntax highlighting: {'ON' if sender.checked else 'OFF'}")
```

## Integration with Other Components

Checkboxes work seamlessly with other rumps components:

```python
class IntegratedApp(rumps.App):
    def __init__(self):
        super(IntegratedApp, self).__init__("Integrated App")

        # Mix checkboxes with other menu items
        self.menu = [
            rumps.MenuItem("Regular Item"),
            rumps.CheckboxMenuItem("Checkbox Setting", callback=self.on_checkbox),
            rumps.SliderMenuItem(callback=self.on_slider),
            rumps.ProgressBarMenuItem(value=0.5),
            rumps.separator,
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]
```

## State Persistence

For applications that need to remember checkbox states between sessions:

```python
import json

class PersistentCheckboxApp(rumps.App):
    def __init__(self):
        super(PersistentCheckboxApp, self).__init__("Persistent Settings")

        # Load saved states
        self.settings = self.load_settings()

        self.dark_mode = rumps.CheckboxMenuItem(
            "Dark Mode",
            checked=self.settings.get('dark_mode', False),
            callback=self.on_dark_mode
        )

        self.notifications = rumps.CheckboxMenuItem(
            "Notifications",
            checked=self.settings.get('notifications', True),
            callback=self.on_notifications
        )

        self.menu = [self.dark_mode, self.notifications]

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                return json.load(f)
        except:
            return {}

    def save_settings(self):
        settings = {
            'dark_mode': self.dark_mode.checked,
            'notifications': self.notifications.checked
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)

    def on_dark_mode(self, sender):
        print(f"Dark mode: {'ON' if sender.checked else 'OFF'}")
        self.save_settings()

    def on_notifications(self, sender):
        print(f"Notifications: {'ON' if sender.checked else 'OFF'}")
        self.save_settings()
```

## Best Practices

1. **Use Clear Labels**: Make checkbox purposes obvious
2. **Set Sensible Defaults**: Use `checked=True/False` appropriately
3. **Provide Feedback**: Use callbacks to show state changes
4. **Group Related Options**: Use decorator paths for organization
5. **Native Appearance**: Checkboxes automatically match system appearance
6. **State Persistence**: Consider saving checkbox states between sessions
7. **Batch Operations**: Provide "Select All" / "Clear All" options when appropriate

## Comparison with Toggle Switches

Checkboxes are preferred over custom toggle switches because they:

- Use native macOS appearance and behavior
- Are immediately familiar to users
- Automatically adapt to system themes (light/dark mode)
- Require less code and resources
- Follow macOS Human Interface Guidelines
- Work consistently across all macOS versions

## Examples

- `examples/checkbox_example.py` - Comprehensive checkbox demonstration
- `simple_checkbox_example.py` - Basic checkbox usage
- `decorator_checkbox_example.py` - Decorator-based checkboxes

## Native Appearance

CheckboxMenuItem uses NSMenuItem's native state system:
- Checked items show a checkmark (✓)
- Unchecked items show no indicator
- Automatically adapts to system appearance
- Follows macOS accessibility settings
- Consistent with other system applications
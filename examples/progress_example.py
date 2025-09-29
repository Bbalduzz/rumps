#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Progress Indicators example for rumps

This example demonstrates the new ProgressBarMenuItem and CircularProgressMenuItem
components that can be embedded directly in menus.
"""

import rumps
import threading
import time


class ProgressDemoApp(rumps.App):
    def __init__(self):
        super(ProgressDemoApp, self).__init__(
            "Progress Demo",
            title="📊"
        )

        # Storage for progress items to update them
        self.progress_items = {}

        self.build_menu()

    def build_menu(self):
        """Build menu with various progress indicator examples."""
        menu_items = []

        # Section 1: Progress Bar Examples
        title_item = rumps.MenuItem("Progress Bars")
        title_symbol = rumps.SFSymbol(
            name="progress.indicator",
            rendering="hierarchical",
            point_size=25.0,
            weight="semibold",
        )
        title_item.set_icon(title_symbol)
        menu_items.append(title_item)

        # Basic progress bar at 25%
        basic_progress = rumps.ProgressBarMenuItem(value=0.25)
        self.progress_items['basic'] = basic_progress
        menu_items.append(basic_progress)

        # Styled progress bar with color
        colored_progress = rumps.ProgressBarMenuItem(
            value=0.60,
            color="#007AFF",
            dimensions=(250, 20)
        )
        self.progress_items['colored'] = colored_progress
        menu_items.append(colored_progress)

        # Progress bar without text
        no_text_progress = rumps.ProgressBarMenuItem(
            value=0.80,
            show_text=False,
            color="#FF3B30",
            dimensions=(180, 16)
        )
        self.progress_items['no_text'] = no_text_progress
        menu_items.append(no_text_progress)

        # Indeterminate progress bar (spinning)
        indeterminate_progress = rumps.ProgressBarMenuItem(
            indeterminate=True,
            dimensions=(200, 20)
        )
        self.progress_items['indeterminate'] = indeterminate_progress
        menu_items.append(indeterminate_progress)

        menu_items.append(rumps.separator)

        # Section 2: Circular Progress Examples
        menu_items.append(rumps.MenuItem("Circular Progress"))

        # Indeterminate circular (spinning)
        spinning_circular = rumps.CircularProgressMenuItem(
            indeterminate=True,
            dimensions=(30, 30),
            color="#FF9500"
        )
        self.progress_items['spinning'] = spinning_circular
        menu_items.append(spinning_circular)

        # Determinate circular (spinning)
        determiante_circular = rumps.CircularProgressMenuItem(
            value=0.3,
            dimensions=(30, 30),
            line_width=3,
        )
        self.progress_items['determinate'] = determiante_circular
        menu_items.append(determiante_circular)

        menu_items.append(rumps.separator)

        # Section 3: Control buttons
        menu_items.append(rumps.MenuItem("Controls"))

        menu_items.append(rumps.MenuItem("Start Simulation", callback=self.start_simulation))
        menu_items.append(rumps.MenuItem("Reset All", callback=self.reset_all))
        menu_items.append(rumps.MenuItem("Toggle Indeterminate", callback=self.toggle_indeterminate))

        menu_items.append(rumps.separator)

        # Download simulation
        download_progress = rumps.ProgressBarMenuItem(
            value=0.0,
            dimensions=(220, 18),
            color="#5856D6"
        )
        self.progress_items['download'] = download_progress

        # Task completion
        task_circular = rumps.CircularProgressMenuItem(
            value=0.0,
            dimensions=(35, 35),
            color="#32D74B"
        )
        self.progress_items['task'] = task_circular

        self.menu = menu_items

    def start_simulation(self, sender):
        """Start a background simulation that updates progress indicators."""
        print("Starting progress simulation...")

        def simulate_progress():
            for i in range(101):
                progress_value = i / 100.0

                # Update various progress indicators
                if 'basic' in self.progress_items:
                    self.progress_items['basic'].value = progress_value

                if 'colored' in self.progress_items:
                    # Make colored bar move in reverse
                    self.progress_items['colored'].value = 1.0 - progress_value

                if 'circular' in self.progress_items:
                    self.progress_items['circular'].value = progress_value

                if 'download' in self.progress_items:
                    # Simulate stepped download progress
                    step_value = min(1.0, progress_value * 1.2)
                    self.progress_items['download'].value = step_value

                if 'determinate' in self.progress_items:
                    # Simulate task completion with delays
                    task_value = min(1.0, (progress_value ** 0.2))
                    self.progress_items['determinate'].value = task_value

                time.sleep(0.05)  # 50ms delay

        # Run simulation in background thread
        thread = threading.Thread(target=simulate_progress, daemon=True)
        thread.start()

        rumps.notification(
            title="Progress Simulation",
            subtitle="Started",
            message="Watch the progress indicators update in real-time",
            data=None
        )

    def reset_all(self, sender):
        """Reset all progress indicators to 0."""
        print("Resetting all progress indicators...")

        for name, progress_item in self.progress_items.items():
            if not progress_item.indeterminate:
                progress_item.value = 0.0

        rumps.notification(
            title="Progress Reset",
            subtitle="Complete",
            message="All progress indicators reset to 0%",
            data=None
        )

    def toggle_indeterminate(self, sender):
        """Toggle indeterminate mode on some progress indicators."""
        print("Toggling indeterminate mode...")

        # Toggle basic progress bar
        if 'basic' in self.progress_items:
            basic = self.progress_items['basic']
            basic.indeterminate = not basic.indeterminate

        # Toggle circular progress
        if 'circular' in self.progress_items:
            circular = self.progress_items['circular']
            circular.indeterminate = not circular.indeterminate

        status = "enabled" if self.progress_items.get('basic', type('', (), {'indeterminate': False})).indeterminate else "disabled"

        rumps.notification(
            title="Indeterminate Mode",
            subtitle=f"Mode {status}",
            message="Basic progress bar and circular indicator toggled",
            data=None
        )


if __name__ == "__main__":
    print("Progress Indicators Demo")
    print("=" * 30)
    print()
    print("This demo showcases the new progress indicator menu items:")
    print("• ProgressBarMenuItem - Horizontal progress bars with percentage")
    print("• CircularProgressMenuItem - Compact circular progress indicators")
    print()
    print("Features demonstrated:")
    print("• Determinate progress (0-100%)")
    print("• Indeterminate progress (spinning animation)")
    print("• Custom colors and dimensions")
    print("• Real-time updates")
    print("• Various styling options")
    print()
    print("Use the control buttons in the menu to interact with the progress indicators!")
    print()

    app = ProgressDemoApp()
    app.run(debug=True)
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script to verify the circular progress indicator visual artifacts are fixed
"""

import rumps


class CircularTestApp(rumps.App):
    def __init__(self):
        super(CircularTestApp, self).__init__("Circular Test", title="🔄")

        # Create various circular progress indicators to test
        self.progress_items = {}

        # Different progress values
        progress_25 = rumps.CircularProgressMenuItem(value=0.25, color="#FF3B30")
        progress_50 = rumps.CircularProgressMenuItem(value=0.5, color="#007AFF")
        progress_75 = rumps.CircularProgressMenuItem(value=0.75, color="#34C759")
        progress_100 = rumps.CircularProgressMenuItem(value=1.0, color="#FF9500")

        # Indeterminate (spinning)
        spinning = rumps.CircularProgressMenuItem(indeterminate=True, color="#5856D6")

        # Store references
        self.progress_items['25'] = progress_25
        self.progress_items['50'] = progress_50
        self.progress_items['75'] = progress_75
        self.progress_items['100'] = progress_100
        self.progress_items['spinning'] = spinning

        self.menu = [
            "25% Progress:",
            progress_25,
            "50% Progress:",
            progress_50,
            "75% Progress:",
            progress_75,
            "100% Progress:",
            progress_100,
            rumps.separator,
            "Spinning:",
            spinning,
            rumps.separator,
            rumps.MenuItem("Animate", callback=self.animate),
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]

    def animate(self, sender):
        """Animate the progress indicators to test smooth updates."""
        import threading
        import time

        def animate_progress():
            for i in range(101):
                progress = i / 100.0

                # Update progress indicators
                self.progress_items['25'].value = min(1.0, progress * 4)  # Reaches 100% at 25%
                self.progress_items['50'].value = min(1.0, progress * 2)  # Reaches 100% at 50%
                self.progress_items['75'].value = min(1.0, progress * 1.33)  # Reaches 100% at 75%
                self.progress_items['100'].value = progress

                time.sleep(0.05)

        thread = threading.Thread(target=animate_progress, daemon=True)
        thread.start()

        print("Started animation - check for smooth circular progress without artifacts!")


if __name__ == "__main__":
    print("Testing fixed circular progress indicators...")
    print("Look for:")
    print("• Smooth circular arcs without visual artifacts")
    print("• Clean determinate progress (custom drawn)")
    print("• Smooth spinning indeterminate progress (NSProgressIndicator)")
    print("• No strange shapes or rendering issues")
    print()

    app = CircularTestApp()
    app.run()
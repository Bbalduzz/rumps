#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple Progress Indicators example

Shows basic usage of the new progress indicator menu items.
"""

import rumps


class SimpleProgressApp(rumps.App):
    def __init__(self):
        super(SimpleProgressApp, self).__init__("Progress Test", title="📈")

        # Create progress indicators
        self.download_progress = rumps.ProgressBarMenuItem(
            value=0.0,
            color="#007AFF",
            dimensions=(200, 18)
        )

        self.task_progress = rumps.CircularProgressMenuItem(
            value=0.0,
            dimensions=(40, 40),
            color="#34C759"
        )

        # Build menu
        self.menu = [
            "Download Progress:",
            self.download_progress,
            rumps.separator,
            "Task Progress:",
            self.task_progress,
            rumps.separator,
            rumps.MenuItem("Start", callback=self.start_progress),
            rumps.MenuItem("Reset", callback=self.reset_progress),
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]

    def start_progress(self, sender):
        """Simulate some progress."""
        import threading
        import time

        def update_progress():
            for i in range(101):
                progress = i / 100.0
                self.download_progress.value = progress
                self.task_progress.value = progress
                time.sleep(0.03)

        thread = threading.Thread(target=update_progress, daemon=True)
        thread.start()

    def reset_progress(self, sender):
        """Reset progress to 0."""
        self.download_progress.value = 0.0
        self.task_progress.value = 0.0


if __name__ == "__main__":
    app = SimpleProgressApp()
    app.run()
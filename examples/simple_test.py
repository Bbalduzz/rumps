#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Cocoa import (
    NSApp, NSApplication, NSObject, NSWindow, NSView, NSColor, NSFont,
    NSWindowStyleMaskTitled, NSWindowStyleMaskClosable, NSWindowStyleMaskMiniaturizable,
    NSWindowStyleMaskResizable, NSBackingStoreBuffered,
    NSMakeRect, NSMakePoint, NSTimer
)
import objc
import math


class CircularProgressView(NSView):
    """
    A lightweight circular progress bar for AppKit in pure Python (PyObjC).
    - Set progress in [0.0, 1.0] with setProgress_().
    - Customize stroke thickness via setLineWidth_().
    """
    def initWithFrame_(self, frame):
        self = objc.super(CircularProgressView, self).initWithFrame_(frame)
        if self is None:
            return None
        self._progress = 0.0         # 0.0 .. 1.0
        self._line_width = 12.0
        # Opt into layer backing for smoother rendering
        self.setWantsLayer_(True)
        return self

    # Public API
    def setProgress_(self, value):
        # Clamp and redraw
        self._progress = max(0.0, min(1.0, float(value)))
        self.setNeedsDisplay_(True)

    def progress(self):
        return self._progress

    def setLineWidth_(self, w):
        self._line_width = max(1.0, float(w))
        self.setNeedsDisplay_(True)

    def drawRect_(self, dirtyRect):
        bounds = self.bounds()
        w, h = bounds.size.width, bounds.size.height
        cx, cy = w * 0.5, h * 0.5
        radius = max(0.0, min(w, h) * 0.5 - self._line_width * 1.2)

        # Colors
        track_color = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.88, 0.90, 0.94, 1.0)
        prog_color  = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.17, 0.47, 0.90, 1.0)  # bluish

        # ---- Track circle ----
        track = objc.lookUpClass("NSBezierPath").bezierPath()
        track.setLineWidth_(self._line_width)
        track.appendBezierPathWithOvalInRect_(NSMakeRect(cx - radius, cy - radius, radius * 2, radius * 2))
        track_color.set()
        track.stroke()

        # ---- Progress arc (clockwise from 12 o'clock) ----
        if self._progress > 0.0:
            start_deg = 90.0               # 12 o'clock
            end_deg = start_deg - (self._progress * 360.0)  # clockwise
            arc = objc.lookUpClass("NSBezierPath").bezierPath()
            arc.setLineWidth_(self._line_width)
            # rounded line caps look nicer
            try:
                from AppKit import NSRoundLineCapStyle
                arc.setLineCapStyle_(NSRoundLineCapStyle)
            except Exception:
                pass
            arc.appendBezierPathWithArcWithCenter_radius_startAngle_endAngle_clockwise_(
                NSMakePoint(cx, cy), radius, start_deg, end_deg, True
            )
            prog_color.set()
            arc.stroke()

        # ---- (Optional) percentage label in the center ----
        pct = f"{int(round(self._progress * 100.0))}%"
        attrs = {
            # These constant keys exist in AppKit; fall back silently if not found
            "NSFont": NSFont.boldSystemFontOfSize_(min(w, h) * 0.18),
            "NSColor": NSColor.colorWithCalibratedWhite_alpha_(0.2, 1.0),
        }
        try:
            # Prefer explicit attribute keys when available
            from AppKit import NSFontAttributeName, NSForegroundColorAttributeName
            attrs = {NSFontAttributeName: attrs["NSFont"], NSForegroundColorAttributeName: attrs["NSColor"]}
        except Exception:
            pass

        # Center the text
        size = pct.sizeWithAttributes_(attrs)
        text_rect = NSMakeRect(cx - size.width * 0.5, cy - size.height * 0.5, size.width, size.height)
        pct.drawInRect_withAttributes_(text_rect, attrs)


class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, _):
        # --- Window ---
        style = (NSWindowStyleMaskTitled
                 | NSWindowStyleMaskClosable
                 | NSWindowStyleMaskMiniaturizable
                 | NSWindowStyleMaskResizable)
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(100, 100, 380, 320), style, NSBackingStoreBuffered, False
        )
        self.window.setTitle_("Circular Progress (AppKit + PyObjC)")

        # --- Progress view ---
        self.progressView = CircularProgressView.alloc().initWithFrame_(NSMakeRect(40, 40, 300, 300))
        self.window.contentView().addSubview_(self.progressView)

        # Demo: animate from 0 → 100% repeatedly
        self._direction = +1
        self._tick = 0.0
        self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.02, self, objc.selector(self.update_, signature=b"v@:@"), None, True
        )

        self.window.makeKeyAndOrderFront_(None)

    def update_(self, _timer):
        # Ease in/out a little for nicer movement
        self._tick += 0.005 * self._direction
        if self._tick >= 1.0:
            self._tick = 1.0
            self._direction = -1
        elif self._tick <= 0.0:
            self._tick = 0.0
            self._direction = +1

        # Optional easing curve (smoothstep)
        t = self._tick
        eased = t * t * (3.0 - 2.0 * t)
        self.progressView.setProgress_(eased)


if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.run()

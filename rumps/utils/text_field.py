from AppKit import NSApp, NSApplication, NSTextField, NSSecureTextField, NSKeyDown, NSCommandKeyMask, NSShiftKeyMask, NSControlKeyMask, NSDeviceIndependentModifierFlagsMask


class Editing(NSTextField):
    """NSTextField with cut, copy, paste, undo and selectAll

    Supports both Command (⌘) and Control (^) key combinations for cross-platform compatibility:
    - ⌘C / ^C: Copy
    - ⌘V / ^V: Paste
    - ⌘X / ^X: Cut
    - ⌘Z / ^Z: Undo
    - ⌘A / ^A: Select All
    """
    def performKeyEquivalent_(self, event):
        return _perform_key_equivalent(self, event)


class SecureEditing(NSSecureTextField):
    """NSSecureTextField with cut, copy, paste, undo and selectAll

    Supports both Command (⌘) and Control (^) key combinations for cross-platform compatibility.
    Note: Copy is disabled for security reasons in secure text fields.
    """
    def performKeyEquivalent_(self, event):
        return _perform_key_equivalent(self, event)


def _perform_key_equivalent(self, event):
    if event.type() == NSKeyDown:
        modifiers = event.modifierFlags() & NSDeviceIndependentModifierFlagsMask
        
        if modifiers == NSCommandKeyMask:
            char = event.charactersIgnoringModifiers()
            if char == "v":
                if NSApp.sendAction_to_from_(b"paste:", None, self):
                    return True
            elif char == "c":
                if NSApp.sendAction_to_from_(b"copy:", None, self):
                    return True
            elif char == "x":
                if NSApp.sendAction_to_from_(b"cut:", None, self):
                    return True
            elif char == "a":
                if NSApp.sendAction_to_from_(b"selectAll:", None, self):
                    return True
            elif char == "z":
                if NSApp.sendAction_to_from_(b"undo:", None, self):
                    return True
        elif modifiers == (NSCommandKeyMask | NSShiftKeyMask):
            char = event.charactersIgnoringModifiers()
            if char == "Z":
                if NSApp.sendAction_to_from_(b"redo:", None, self):
                    return True

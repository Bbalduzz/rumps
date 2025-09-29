#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""Exception classes for rumps."""


class RumpsError(Exception):
    """A generic rumps error occurred."""
    pass


class InternalRumpsError(RumpsError):
    """Internal mechanism powering functionality of rumps failed."""
    pass
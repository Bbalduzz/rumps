#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""
Compatibility layer for Python 2 and Python 3.

This module provides compatibility shims for code that needs to run on both
Python 2 and Python 3.
"""

import sys

PY2 = sys.version_info[0] == 2

if not PY2:
    # Python 3
    binary_type = bytes
    text_type = str
    string_types = (str,)

    iteritems = lambda d: iter(d.items())

    import collections.abc as collections_abc

else:
    # Python 2
    binary_type = ()
    text_type = unicode
    string_types = (str, unicode)

    iteritems = lambda d: d.iteritems()

    import collections as collections_abc
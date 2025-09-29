#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""Utility modules for rumps."""

from .listdict import ListDict
from .internal import (
    require_string,
    require_string_or_none,
    call_as_function_or_method,
    guard_unexpected_errors,
    string_to_objc
)
from .compat import (
    PY2,
    binary_type,
    text_type,
    string_types,
    iteritems,
    collections_abc
)

__all__ = [
    'ListDict',
    'require_string',
    'require_string_or_none',
    'call_as_function_or_method',
    'guard_unexpected_errors',
    'string_to_objc',
    'PY2',
    'binary_type',
    'text_type',
    'string_types',
    'iteritems',
    'collections_abc'
]
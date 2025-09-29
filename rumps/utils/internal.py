#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""Internal utility functions."""

from __future__ import print_function

import inspect
import traceback
import sys

import Foundation

from .compat import string_types, binary_type, PY2
from ..core.exceptions import InternalRumpsError


def require_string(*objs):
    """Ensure all objects are strings."""
    for obj in objs:
        if not isinstance(obj, string_types):
            raise TypeError(
                'a string is required but given {0}, a {1}'.format(obj, type(obj).__name__)
            )


def require_string_or_none(*objs):
    """Ensure all objects are strings or None."""
    for obj in objs:
        if not(obj is None or isinstance(obj, string_types)):
            raise TypeError(
                'a string or None is required but given {0}, a {1}'.format(obj, type(obj).__name__)
            )


def call_as_function_or_method(func, *args, **kwargs):
    """
    Call func as function or method.

    The idea here is that when using decorators in a class, the functions passed are not bound so we have to
    determine later if the functions we have (those saved as callbacks) for particular events need to be passed
    'self'.

    This works for an App subclass method or a standalone decorated function. Will attempt to find function as
    a bound method of the App instance. If it is found, use it, otherwise simply call function.
    """
    from ..core import app as app_module
    try:
        app = getattr(app_module.App, '*app_instance')
    except (AttributeError, ImportError):
        pass
    else:
        for name, method in inspect.getmembers(app, predicate=inspect.ismethod):
            if method.__func__ is func:
                return method(*args, **kwargs)
    return func(*args, **kwargs)


def guard_unexpected_errors(func):
    """
    Decorator to be used in PyObjC callbacks where an error bubbling up
    would cause a crash. Instead of crashing, print the error to stderr and
    prevent passing to PyObjC layer.

    For Python 3, print the exception using chaining. Accomplished by setting
    the cause of InternalRumpsError to the exception.

    For Python 2, emulate exception chaining by printing the original exception
    followed by InternalRumpsError.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except Exception as e:
            internal_error = InternalRumpsError(
                'an unexpected error occurred within an internal callback'
            )
            if PY2:
                traceback.print_exc()
                print('\nThe above exception was the direct cause of the following exception:\n', file=sys.stderr)
                traceback.print_exception(InternalRumpsError, internal_error, None)
            else:
                internal_error.__cause__ = e
                traceback.print_exception(InternalRumpsError, internal_error, None)

    return wrapper


def string_to_objc(x):
    """Convert Python string to Objective-C string."""
    if isinstance(x, binary_type):
        return Foundation.NSData.alloc().initWithData_(x)
    elif isinstance(x, string_types):
        return Foundation.NSString.alloc().initWithString_(x)
    else:
        raise TypeError(
            "expected a string or a bytes-like object but provided %s, "
            "having type '%s'" % (
                x,
                type(x).__name__
            )
        )
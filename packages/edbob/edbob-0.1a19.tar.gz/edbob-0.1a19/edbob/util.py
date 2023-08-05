#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  edbob -- Pythonic Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of edbob.
#
#  edbob is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  edbob is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with edbob.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
``edbob.util`` -- Utilities
"""

from pkg_resources import iter_entry_points

import edbob


# Import OrderedDict for the sake of other modules.
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


def entry_point_map(key):
    """
    Convenience function to retrieve a dictionary of entry points, keyed by
    name.

    ``key`` must be the "section name" for the entry points you're after, e.g.
    ``'edbob.commands'``.
    """

    epmap = {}
    for ep in iter_entry_points(key):
        epmap[ep.name] = ep.load()
    return epmap


def prettify(text):
    """
    Returns a "prettified" version of ``text``, which is more or less assumed
    to be a Pythonic representation of an (singular or plural) entity name.  It
    splits the text into capitalized words, e.g. "purchase_orders" becomes
    "Purchase Orders".

    .. note::
       No attempt is made to handle pluralization; the spelling of ``text`` is
       always preserved.
    """

    words = text.replace('_', ' ').split()
    return ' '.join([x.capitalize() for x in words])


class requires_impl(edbob.Object):
    """
    Decorator for properties or methods defined on parent classes only for
    documentation's sake, but which in fact rely on the derived class entirely
    for implementation.

    This merely adds a helpful message to the ``NotImplementedError`` exception
    which will be raised.
    """

    is_property = False

    def __call__(self, func):
        if self.is_property:
            message = "Please define the %s.%s attribute"
        else:
            message = "Please implement the %s.%s() method"

        def wrapped(self, *args, **kwargs):
            msg = message % (self.__class__.__name__, func.__name__)
            msg += " (within the %s module)" % self.__class__.__module__
            raise NotImplementedError(msg)

        # wrapped.__doc__ = func.__doc__ + "\n\n    This must be implemented by the derived class."
        wrapped.__doc__ = """%s

        This must be implemented by the derived class.""" % func.__doc__
        return wrapped

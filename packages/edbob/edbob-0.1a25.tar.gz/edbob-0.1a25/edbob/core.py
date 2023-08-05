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
``edbob.core`` -- Core Stuff
"""


import logging
import uuid


__all__ = ['Object', 'basic_logging', 'get_uuid', 'graft']


class Object(object):
    """
    Generic base class which provides a common ancestor, and some other
    conveniences.
    """

    def __init__(self, **kwargs):
        """
        Constructor.  All keyword arguments are assumed to be attribute names
        and are assigned directly to the new ``Object`` instance.
        """

        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __getitem__(self, key):
        """
        Allows dict-like access to the object's attributes.
        """

        if hasattr(self, key):
            return getattr(self, key)

    def __str__(self):
        """
        Leverage :meth:`__unicode__()` method if it exists; otherwise fall back
        to ``repr(self)``.
        """

        if hasattr(self, '__unicode__'):
            return str(unicode(self))
        return repr(self)


def basic_logging():
    """
    Does some basic configuration on the root logger.

    .. note::
       This only enables console output at this point; it is assumed that if
       you intend to "truly" configure logging that you will be using a proper
       config file and calling :func:`edbob.init()`.
    """

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
            '%(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s'))
    root = logging.getLogger()
    root.addHandler(handler)


def get_uuid():
    """
    Generates a universally-unique identifier and returns its 32-character hex
    value.
    """

    return uuid.uuid1().hex


def graft(target, source, names=None):
    """
    Adds names to the ``target`` namespace, copying each from ``source``.

    If ``names`` is provided, it can be a string if adding only one thing;
    otherwise it should be a list of strings.  If it is not provided, then
    everything from ``source`` will be grafted.

    .. note::
       If "everything" is to be grafted (i.e. ``names is None``), then
       ``source.__all__`` will be consulted if available.  If it is not, then
       ``dir(source)`` will be used instead.
    """

    if names is None:
        if hasattr(source, '__all__'):
            names = source.__all__
        else:
            names = dir(source)
    elif isinstance(names, basestring):
        names = [names]

    for name in names:
        if hasattr(source, name):
            setattr(target, name, getattr(source, name))
        else:
            setattr(target, name, source.get(name))
        if not hasattr(target, '__all__'):
            target.__all__ = []
        target.__all__.append(name)

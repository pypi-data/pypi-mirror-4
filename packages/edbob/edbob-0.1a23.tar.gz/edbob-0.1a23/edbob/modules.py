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
``edbob.modules`` -- Module Tools
"""

import sys

from edbob import exceptions


__all__ = ['load_spec']


def import_module_path(module_path):
    """
    Imports and returns an arbitrary Python module, given its "dotted" path
    (i.e. not its file path).
    """

    if module_path in sys.modules:
        return sys.modules[module_path]
    module = __import__(module_path)
    return last_module(module, module_path)


def last_module(module, module_path):
    """
    Returns the "last" module represented by ``module_path``, by walking
    ``module`` until the desired module is found.

    For example, passing a reference to the ``rattail`` module and a module
    path of ``"rattail.sw.ishida.slpv"``, this function will ultimately return
    a reference to the actual ``rattail.sw.ishida.slpv`` module.

    This function is primarily used by :func:`import_module_path()`, since
    Python's ``__import__()`` function will typically return the top-most
    ("first") module in the dotted path.
    """

    parts = module_path.split('.')
    parts.pop(0)
    child = getattr(module, parts[0])
    if len(parts) == 1:
        return child
    return last_module(child, '.'.join(parts))


def load_spec(spec):
    """
    .. highlight:: none

    Returns an object as found in a module namespace.  ``spec`` should be of
    the same form which setuptools uses for its entry points, e.g.::

       rattail.ce:collect_batch

    The above would return a reference to the ``collect_batch`` function found
    in the ``rattail.ce`` module namespace.  The module is loaded (imported) if
    necessary.
    """

    module_path, obj = spec.split(':')
    module = import_module_path(module_path)
    try:
        obj = getattr(module, obj)
    except AttributeError:
        raise exceptions.ModuleMissingAttribute(spec)
    return obj

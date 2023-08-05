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
``edbob.sqlalchemy`` -- SQLAlchemy Stuff
"""

from __future__ import absolute_import

from sqlalchemy import Table, Column, String
from sqlalchemy import engine_from_config as _engine_from_config

from edbob.core import get_uuid
from edbob.modules import load_spec
from edbob.time import utc_time


__all__ = ['getset_factory', 'table_with_uuid', 'current_time']


def current_time(context):
    """
    This function may be provided to the ``default`` parameter of a
    :class:`sqlalchemy.Column` class definition.  Doing so will ensure the
    column's default value will be the current time in UTC.
    """

    return utc_time(naive=True)


def engine_from_config(config, prefix='sqlalchemy.', **kwargs):
    """
    Slightly enhanced version of the :func:`sqlalchemy.engine_from_config()`
    function.  This version is aware of the ``poolclass`` configuration
    parameter, and will coerce it via :func:`edbob.load_spec()`.

    Note that if a pool class is specified, the class should be represented
    using the "spec" format and *not* pure dotted path notation, e.g.:

    Correct::

       [edbob.db]
       default.poolclass = sqlqlchemy.pool:NullPool

    Incorrect::

       [edbob.db]
       default.poolclass = sqlalchemy.pool.NullPool
    """

    if config.has_key(prefix + 'poolclass'):
        config[prefix + 'poolclass'] = load_spec(config[prefix + 'poolclass'])
    return _engine_from_config(config, prefix=prefix, **kwargs)


def getset_factory(collection_class, proxy):
    """
    Get/set factory for SQLAlchemy association proxy attributes.
    """

    def getter(obj):
        if obj is None:
            return None
        return getattr(obj, proxy.value_attr)

    def setter(obj, val):
        setattr(obj, proxy.value_attr, val)

    return getter, setter


def table_with_uuid(name, metadata, *args, **kwargs):
    """
    .. highlight:: python

    Convenience function to abstract the addition of the ``uuid`` column to a
    new table.  Can be used to replace this::

       Table(
           'things', metadata,
           Column('uuid', String(32), primary_key=True, default=get_uuid),
           Column('name', String(50)),
           )

    ...with this::

        table_with_uuid(
            'things', metadata,
            Column('name', String(50)),
            )
    """

    return Table(name, metadata,
                 Column('uuid', String(32), primary_key=True, default=get_uuid),
                 *args, **kwargs)

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

from edbob.core import get_uuid
from edbob.time import utc_time


__all__ = ['getset_factory', 'table_with_uuid', 'current_time']


def getset_factory(collection_class, proxy):
    """
    Helper function, useful for SQLAlchemy's "association proxy" configuration.
    """

    def getter(obj):
        if obj is None: return None
        return getattr(obj, proxy.value_attr)
    setter = lambda obj, val: setattr(obj, proxy.value_attr, val)
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


def current_time(context):
    """
    This function may be provided to the ``default`` parameter of a
    :class:`sqlalchemy.Column` class definition.  Doing so will ensure the
    column's default value will be the current time in UTC.
    """

    return utc_time(naive=True)

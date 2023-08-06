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
``edbob.db.model`` -- Core Schema Definition
"""

from sqlalchemy import Column, String, Text

import edbob
from edbob.db import Base


__all__ = ['ActiveExtension', 'Setting']


def uuid_column(*args):
    """
    Convenience function which returns a ``uuid`` column for use as a table's
    primary key.
    """

    return Column(String(32), primary_key=True, default=edbob.get_uuid, *args)


class ActiveExtension(Base):
    """
    Represents an extension which has been activated within a database.
    """

    __tablename__ = 'active_extensions'

    name = Column(String(50), primary_key=True)

    def __repr__(self):
        return "<ActiveExtension: %s>" % self.name

    def __str__(self):
        return str(self.name or '')


class Setting(Base):
    """
    Represents a setting stored within the database.
    """

    __tablename__ = 'settings'

    name = Column(String(255), primary_key=True)
    value = Column(Text)

    def __repr__(self):
        return "<Setting: %s>" % self.name

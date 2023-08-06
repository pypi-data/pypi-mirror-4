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
``edbob.db.mappers`` -- Object Relational Mappings
"""

from sqlalchemy.orm import mapper, relationship

from edbob.db import classes as c


def make_mappers(metadata):
    """
    This function glues together the schema definition found in the ``models``
    module with the data class definitions found in the ``classes`` module.
    ``metadata`` should be a ``sqlalchemy.MetaData`` instance.

    It is meant to be called only once, by :func:`edbob.init()`.
    """

    t = metadata.tables


    # ActiveExtension
    mapper(
        c.ActiveExtension, t['active_extensions'],
        )


    # Permission
    mapper(
        c.Permission, t['permissions'],
        )


    # Person
    mapper(
        c.Person, t['people'],
        properties=dict(

            user=relationship(
                c.User,
                back_populates='person',
                uselist=False,
                ),
            ),
        )


    # Role
    mapper(
        c.Role, t['roles'],
        properties=dict(

            _permissions=relationship(
                c.Permission,
                backref='role',
                ),

            _users=relationship(
                c.UserRole,
                backref='role',
                ),
            ),
        )


    # Setting
    mapper(
        c.Setting, t['settings'],
        )


    # User
    mapper(
        c.User, t['users'],
        properties=dict(

            person=relationship(
                c.Person,
                back_populates='user',
                ),

            _roles=relationship(
                c.UserRole,
                backref='user',
                cascade='save-update,merge,delete',
                ),
            ),
        )


    # UserRole
    mapper(
        c.UserRole, t['users_roles'],
        )

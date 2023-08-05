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
``edbob.db.extensions.auth.model`` -- Schema Definition
"""

from sqlalchemy import *
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

import edbob
from edbob.db.model import Base, uuid_column
from edbob.db.extensions.contact import Person
from edbob.sqlalchemy import getset_factory


__all__ = ['Role', 'User', 'UserRole', 'Permission']


class Permission(Base):
    """
    Represents the fact that a particular :class:`Role` is allowed to do a
    particular type of thing.
    """

    __tablename__ = 'permissions'

    role_uuid = Column(String(32), ForeignKey('roles.uuid'), primary_key=True)
    permission = Column(String(50), primary_key=True)

    def __repr__(self):
        return "<Permission: %s, %s>" % (self.role, self.permission)

    def __str__(self):
        return str(self.permission or '')


class UserRole(Base):
    """
    Represents the association between a :class:`User` and a :class:`Role`.
    """

    __tablename__ = 'users_roles'

    uuid = uuid_column()
    user_uuid = Column(String(32), ForeignKey('users.uuid'))
    role_uuid = Column(String(32), ForeignKey('roles.uuid'))

    def __repr__(self):
        return "<UserRole: %s : %s>" % (self.user, self.role)


class Role(Base):
    """
    Represents a role within the system; used to manage permissions.
    """

    __tablename__ = 'roles'

    uuid = uuid_column()
    name = Column(String(25), nullable=False, unique=True)

    _permissions = relationship(
        Permission, backref='role',
        cascade='save-update, merge, delete, delete-orphan')
    permissions = association_proxy('_permissions', 'permission',
                                    creator=lambda x: Permission(permission=x),
                                    getset_factory=getset_factory)

    _users = relationship(UserRole, backref='role')
    users = association_proxy('_users', 'user',
                              creator=lambda x: UserRole(user=x),
                              getset_factory=getset_factory)

    def __repr__(self):
        return "<Role: %s>" % self.name

    def __str__(self):
        return str(self.name or '')


class User(Base):
    """
    Represents a user of the system.  This may or may not correspond to a real
    person, i.e. some users may exist solely for automated tasks.
    """

    __tablename__ = 'users'

    uuid = uuid_column()
    username = Column(String(25), nullable=False, unique=True)
    password = Column(String(60))
    salt = Column(String(29))
    person_uuid = Column(String(32), ForeignKey('people.uuid'))

    _roles = relationship(UserRole, backref='user')
    roles = association_proxy(
        '_roles', 'role',
        creator=lambda x: UserRole(role=x),
        getset_factory=getset_factory)

    def __repr__(self):
        return "<User: %s>" % self.username

    def __str__(self):
        return str(self.username or '')

    @property
    def display_name(self):
        """
        Returns the user's ``person.display_name``, if present, otherwise the
        ``username``.
        """
        if self.person and self.person.display_name:
            return self.person.display_name
        return self.username


User.person = relationship(
    Person,
    back_populates='user',
    uselist=False)

Person.user = relationship(
    User,
    back_populates='person',
    uselist=False)

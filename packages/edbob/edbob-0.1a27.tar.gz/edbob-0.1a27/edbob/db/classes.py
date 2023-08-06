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
``edbob.db.classes`` -- Data Class Definitions
"""

from sqlalchemy.ext.associationproxy import association_proxy

import edbob
from edbob.sqlalchemy import getset_factory


__all__ = ['Permission', 'Person', 'Role', 'Setting', 'User', 'UserRole']


class PersonDerivative(edbob.Object):
    """
    Base class for classes which must derive certain functionality from the
    :class:`Person` class, e.g. :class:`User`.
    """

    display_name = association_proxy('person', 'display_name',
                                     creator=lambda x: Person(display_name=x),
                                     getset_factory=getset_factory)

    first_name = association_proxy('person', 'first_name',
                                   creator=lambda x: Person(first_name=x),
                                   getset_factory=getset_factory)

    last_name = association_proxy('person', 'last_name',
                                  creator=lambda x: Person(last_name=x),
                                  getset_factory=getset_factory)


class ActiveExtension(edbob.Object):
    """
    Represents an extension which has been activated within a database.
    """

    def __repr__(self):
        return "<ActiveExtension: %s>" % self.name


class Permission(edbob.Object):
    """
    Represents the fact that a particular :class:`Role` is allowed to do a
    certain thing.
    """

    def __repr__(self):
        return "<Permission: %s: %s>" % (self.role, self.permission)


class Person(edbob.Object):
    """
    Represents a real, living and breathing person.  (Or, at least was
    previously living and breathing, in the case of the deceased.)
    """

    def __repr__(self):
        return "<Person: %s>" % self.display_name

    def __str__(self):
        return str(self.display_name or '')

    @property
    def customer(self):
        """
        Returns the first :class:`Customer` instance in
        :attr:`Person.customers`, or ``None`` if that list is empty.

        .. note::
           As of this writing, :attr:`Person.customers` is an
           arbitrarily-ordered list, so the only real certainty you have when
           using :attr:`Person.customer` is when the :class:`Person` instance
           is associated with exactly one (or zero) :class:`Customer`
           instances.
        """

        if self.customers:
            return self.customers[0]
        return None


class Role(edbob.Object):
    """
    Represents a role within the organization; used to manage permissions.
    """

    permissions = association_proxy('_permissions', 'permission',
                                    creator=lambda x: Permission(permission=x),
                                    getset_factory=getset_factory)

    users = association_proxy('_users', 'user',
                              creator=lambda x: UserRole(user=x),
                              getset_factory=getset_factory)

    def __repr__(self):
        return "<Role: %s>" % self.name

    def __str__(self):
        return str(self.name or '')


class Setting(edbob.Object):
    """
    Represents a setting stored within the database.
    """

    def __repr__(self):
        return "<Setting: %s>" % self.name


class User(PersonDerivative):
    """
    Represents a user of the system.  This may or may not correspond to a real
    person, e.g. for data import jobs and the like.
    """

    employee = association_proxy('person', 'employee',
                                 creator=lambda x: Person(employee=x),
                                 getset_factory=getset_factory)

    roles = association_proxy('_roles', 'role',
                              creator=lambda x: UserRole(role=x),
                              getset_factory=getset_factory)

    def __repr__(self):
        return "<User: %s>" % self.username

    def __str__(self):
        return str(self.username or '')


class UserRole(edbob.Object):
    """
    Represents the association between a :class:`User` and a :class:`Role`.
    """

    def __repr__(self):
        return "<UserRole: %s : %s>" % (self.user, self.role)

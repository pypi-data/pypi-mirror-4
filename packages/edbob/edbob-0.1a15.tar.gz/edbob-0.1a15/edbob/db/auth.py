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
``edbob.db.auth`` -- Authentication & Authorization
"""

import bcrypt

from sqlalchemy.orm import object_session

import edbob
from edbob.db import needs_session


class BcryptAuthenticator(edbob.Object):
    """
    Authentication with py-bcrypt (Blowfish).
    """

    def populate_user(self, user, password):
        user.salt = bcrypt.gensalt()
        user.password = bcrypt.hashpw(password, user.salt)

    def authenticate_user(self, user, password):
        return bcrypt.hashpw(password, user.salt) == user.password


@needs_session
def authenticate_user(session, username, password):
    """
    Attempts to authenticate with ``username`` and ``password``.  If successful,
    returns the :class:`edbob.User` instance; otherwise returns ``None``.
    """

    q = session.query(edbob.User)
    q = q.filter(edbob.User.username == username)
    user = q.first()
    if user:
        auth = BcryptAuthenticator()
        if auth.authenticate_user(user, password):
            return user


def administrator_role(session):
    """
    Returns the "Administrator" :class:`edbob.Role` instance, attached to the
    given ``session``.
    """

    uuid = 'd937fa8a965611dfa0dd001143047286'
    admin = session.query(edbob.Role).get(uuid)
    if admin:
        return admin
    admin = edbob.Role(uuid=uuid, name='Administrator')
    session.add(admin)
    return admin


def guest_role(session):
    """
    Returns the "Guest" :class:`edbob.Role` instance, attached to the given
    ``session``.
    """

    uuid = 'f8a27c98965a11dfaff7001143047286'
    guest = session.query(edbob.Role).get(uuid)
    if guest:
        return guest
    guest = edbob.Role(uuid=uuid, name='Guest')
    session.add(guest)
    return guest


def grant_permission(role, permission, session=None):
    """
    Grants ``permission`` to ``role``.
    """

    if not session:
        session = object_session(role)
        assert session
    if permission not in role.permissions:
        role.permissions.append(permission)


def has_permission(obj, perm, session=None):
    """
    Checks the given ``obj`` (which may be either a :class:`edbob.User`` or
    :class:`edbob.Role` instance), and returns a boolean indicating whether or
    not the object is allowed the given permission.  ``perm`` should be a
    fully-qualified permission name, e.g. ``'users.create'``.
    """

    if isinstance(obj, edbob.User):
        roles = list(obj.roles)
    elif isinstance(obj, edbob.Role):
        roles = [obj]
    elif obj is None:
        roles = []
    else:
        raise TypeError("You must pass either a User or Role for 'obj'; got: %s" % repr(obj))
    if not session:
        session = object_session(obj)
        assert session
    admin = administrator_role(session)
    roles.append(guest_role(session))
    for role in roles:
        if role is admin:
            return True
        for permission in role.permissions:
            if permission == perm:
                return True
    return False


def init_database(engine, session):
    """
    Initialize the auth system within an ``edbob`` database.

    Currently this only creates an :class:`edbob.User` instance with username
    ``'admin'`` (and password the same), and assigns the user to the built-in
    administrative role (see :func:`administrator_role()`).
    """

    admin = edbob.User(username='admin')
    set_user_password(admin, 'admin')
    admin.roles.append(administrator_role(session))
    session.add(admin)
    session.flush()
    print "Created 'admin' user with password 'admin'"


def set_user_password(user, password):
    """
    Sets the password for the given :class:`edbob.User` instance.
    """

    auth = BcryptAuthenticator()
    auth.populate_user(user, password)

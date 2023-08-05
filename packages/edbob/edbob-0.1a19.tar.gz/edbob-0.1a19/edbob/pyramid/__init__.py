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
``edbob.pyramid`` -- Pyramid Framework
"""

from sqlalchemy.orm import sessionmaker, scoped_session
from zope.sqlalchemy import ZopeTransactionExtension

import edbob


__all__ = ['Session']

Session = scoped_session(sessionmaker())


def includeme(config):
    """
    Adds ``edbob``-specific features to the application.  Currently this does
    two things:

    It adds a ``ZopeTransactionExtension`` instance as an extension to the
    SQLAlchemy scoped ``Session`` class.  This is necessary for most view code
    that ships with ``edbob``, so you will most likely need to specify
    ``config.include('edbob.pyramid')`` somewhere in your app config (i.e. your
    ``main()`` function).

    The other thing added is the ``edbob`` static view for CSS files etc.
    """

    # Configure Beaker session.
    config.include('pyramid_beaker')

    # Bring in transaction manager.
    config.include('pyramid_tm')

    # Configure SQLAlchemy session.
    Session.configure(bind=edbob.engine)
    Session.configure(extension=ZopeTransactionExtension())

    # Configure user authentication / authorization.
    from pyramid.authentication import SessionAuthenticationPolicy
    config.set_authentication_policy(SessionAuthenticationPolicy())
    from edbob.pyramid.auth import EdbobAuthorizationPolicy
    config.set_authorization_policy(EdbobAuthorizationPolicy())

    # Add forbidden view.
    config.add_forbidden_view('edbob.pyramid.views.forbidden')

    # Add static views.
    config.include('edbob.pyramid.static')

    # Add subscriber hooks.
    config.include('edbob.pyramid.subscribers')

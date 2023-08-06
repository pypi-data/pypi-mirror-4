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
``edbob.db.util`` -- Database Utilities
"""

import sqlalchemy.exc

import edbob.db
from edbob.db.model import ActiveExtension


def core_schema_installed(engine=None):
    """
    Returns boolean indicating whether the core schema has been installed to
    the database represented by ``engine``.

    If no engine is provided, :attr:`edbob.db.engine` is assumed.
    """
    
    if engine is None:
        engine = edbob.db.engine

    # Check database existence and/or connectivity.
    try:
        conn = engine.connect()
    except sqlalchemy.exc.OperationalError:
        return False
    else:
        conn.close()

    # Issue "bogus" query to verify core table existence.
    session = edbob.db.Session(bind=engine)
    try:
        session.query(ActiveExtension).count()
    except sqlalchemy.exc.ProgrammingError:
        return False
    finally:
        session.close()

    return True


def install_core_schema(engine=None):
    """
    Installs the core schema to the database represented by ``engine``.

    If no engine is provided, :attr:`edbob.db.engine` is assumed.
    """

    if not engine:
        engine = edbob.db.engine

    # Attempt connection in order to force an error, if applicable.
    conn = engine.connect()
    conn.close()

    # Create tables for core schema.
    meta = edbob.db.get_core_metadata()
    meta.create_all(engine)

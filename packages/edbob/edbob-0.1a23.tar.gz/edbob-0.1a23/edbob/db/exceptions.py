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
``edbob.db.exceptions`` -- Database Exceptions
"""


class CoreSchemaAlreadyInstalled(Exception):
    """
    Raised when a request is made to install the core schema to a database, but
    it is already installed there.
    """

    def __init__(self, installed_version):
        self.installed_version = installed_version

    def __str__(self):
        return "Core schema already installed (version %s)" % self.installed_version


class CoreSchemaNotInstalled(Exception):
    """
    Raised when a request is made which requires the core schema to be present
    in a database, yet such is not the case.
    """

    def __init__(self, engine):
        self.engine = engine

    def __str__(self):
        return "Core schema not installed: %s" % str(self.engine)


class ExtensionNotFound(Exception):
    """
    Raised when an extension is requested which cannot be located.
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Extension not found: %s" % self.name

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
``edbob.exceptions`` -- Exceptions
"""


class ConfigError(Exception):
    """
    Raised when configuration is missing or otherwise invalid.
    """

    def __init__(self, section, option, msg=None):
        self.section = section
        self.option = option
        self.msg = msg or "Missing or invalid config"

    def __str__(self):
        return "%s; please set '%s' in the [%s] section of your config file" % (
            self.msg, self.option, self.section)


class InitError(Exception):
    """
    Raised when initialization fails for a given module.
    """

    def __init__(self, module):
        self.module = module

    def __str__(self):
        return "Module '%s' has no init() function" % self.module.__name__


class LoadSpecError(Exception):
    """
    Raised when something obvious goes wrong with :func:`edbob.load_spec()`.
    """

    def __init__(self, spec):
        self.spec = spec

    def __str__(self):
        msg = 'Failed to load spec: %s' % self.spec
        specifics = self.specifics()
        if specifics:
            msg += " (%s)" % specifics
        return msg

    def specifics(self):
        return None


class ModuleMissingAttribute(LoadSpecError):
    """
    Raised during :func:`edbob.load_spec()` when the module imported okay but
    the attribute could not be found.
    """

    def specifics(self):
        mod, attr = self.spec.split(':')
        return "module '%s' was loaded but '%s' attribute not found" % (mod, attr)


class RecipientsNotFound(Exception):
    """
    Raised when no recipients could be found in config.
    """
    
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return "No recipients configured (set 'recipients.%s' in [edbob.mail])" % self.key


class SenderNotFound(Exception):
    """
    Raised when no sender could be found in config.
    """

    def __init__(self, key):
        self.key = key

    def __str__(self):
        return "No sender configured (set 'sender.%s' in [edbob.mail])" % self.key

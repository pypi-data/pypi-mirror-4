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
``edbob.pyramid.handlers.util`` -- Handler Utilities
"""

from pyramid.httpexceptions import HTTPFound

from edbob.db.perms import has_permission


class needs_perm(object):
    """
    Decorator to be used for handler methods which should restrict access based
    on the current user's permissions.
    """

    def __init__(self, permission, **kwargs):
        self.permission = permission
        self.kwargs = kwargs

    def __call__(self, fn):
        permission = self.permission
        kw = self.kwargs
        def wrapped(self):
            if not self.request.current_user:
                self.request.session['referrer'] = self.request.url_generator.current()
                self.request.session.flash("You must be logged in to do that.", 'error')
                return HTTPFound(location=self.request.route_url('login'))
            if not has_permission(self.request.current_user, permission):
                self.request.session.flash("You do not have permission to do that.", 'error')
                home = kw.get('redirect', self.request.route_url('home'))
                return HTTPFound(location=home)
            return fn(self)
        return wrapped


def needs_user(fn):
    """
    Decorator for handler methods which require simply that a user be currently
    logged in.
    """

    def wrapped(self):
        if not self.request.current_user:
            self.request.session['referrer'] = self.request.url_generator.current()
            self.request.session.flash("You must be logged in to do that.", 'error')
            return HTTPFound(location=self.request.route_url('login'))
        return fn(self)
    return wrapped

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
``edbob.pyramid.subscribers`` -- Subscribers
"""

from pyramid import threadlocal
from pyramid.security import authenticated_userid

import edbob
from edbob.db.auth import has_permission
from edbob.pyramid import helpers
from edbob.pyramid import Session


def before_render(event):
    """
    Adds goodies to the global template renderer context.
    """

    request = event.get('request') or threadlocal.get_current_request()

    renderer_globals = event
    renderer_globals['h'] = helpers
    renderer_globals['url'] = request.route_url
    renderer_globals['edbob'] = edbob
    renderer_globals['Session'] = Session


def context_found(event):
    """
    This hook attaches various attributes and methods to the ``request``
    object.  Specifically:

    The :class:`edbob.User` instance currently logged-in (if indeed there is
    one) is attached as ``request.user``.

    A ``request.has_perm()`` method is attached, which is a shortcut for
    :func:`edbob.db.auth.has_permission()`.

    A ``request.get_referrer()`` method is attached, which contains some
    convenient logic for determining the referring URL.

    The ``request.get_setting()`` and ``request.save_setting()`` methods are
    attached, which are shortcuts for :func:`edbob.get_setting()` and
    :func:`edbob.save_setting()`, respectively.
    """

    request = event.request

    request.user = None
    uuid = authenticated_userid(request)
    if uuid:
        request.user = Session.query(edbob.User).get(uuid)

    def has_perm(perm):
        if not request.user:
            return False
        return has_permission(request.user, perm)
    request.has_perm = has_perm

    def get_referrer(default=None):
        if request.params.get('referrer'):
            return request.params['referrer']
        if request.session.get('referrer'):
            return request.session.pop('referrer')
        referrer = request.referrer
        if not referrer or referrer == request.current_route_url():
            if default:
                referrer = default
            else:
                referrer = request.route_url('home')
        return referrer
    request.get_referrer = get_referrer

    def get_setting(name):
        return edbob.get_setting(name, Session())
    request.get_setting = get_setting

    def save_setting(name, value):
        edbob.save_setting(name, value, Session())
    request.save_setting = save_setting


def includeme(config):
    config.add_subscriber('edbob.pyramid.subscribers:before_render',
                          'pyramid.events.BeforeRender')
    config.add_subscriber('edbob.pyramid.subscribers.context_found',
                          'pyramid.events.ContextFound')

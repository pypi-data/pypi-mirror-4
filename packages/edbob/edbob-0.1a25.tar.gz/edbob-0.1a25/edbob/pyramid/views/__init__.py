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
``edbob.pyramid.views`` -- Views
"""

from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

from webhelpers.html import literal
from webhelpers.html.tags import link_to

from edbob.pyramid.views.core import *
from edbob.pyramid.views.grids import *
from edbob.pyramid.views.crud import *
from edbob.pyramid.views.autocomplete import *
# from edbob.pyramid.views.form import *


def forbidden(request):
    """
    The forbidden view.  This is triggered whenever access rights are denied
    for an otherwise-appropriate view.
    """

    msg = literal("You do not have permission to do that.")
    if not authenticated_userid(request):
        msg += literal("&nbsp; (Perhaps you should %s?)" %
                       link_to("log in", request.route_url('login')))
    request.session.flash(msg, allow_duplicate=False)

    url = request.referer
    if not url or url == request.current_route_url():
        url = request.route_url('home')
    return HTTPFound(location=url)


def includeme(config):
    config.include('edbob.pyramid.views.auth')
    config.include('edbob.pyramid.views.people')
    config.include('edbob.pyramid.views.progress')
    config.include('edbob.pyramid.views.users')

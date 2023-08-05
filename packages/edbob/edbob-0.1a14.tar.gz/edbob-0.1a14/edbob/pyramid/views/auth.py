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
``edbob.pyramid.views.auth`` -- Auth Views
"""

import formencode
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

import edbob
from edbob.db.auth import authenticate_user
from edbob.pyramid import Session


class UserLogin(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    username = formencode.validators.NotEmpty()
    password = formencode.validators.NotEmpty()


def login(request):
    """
    The login view, responsible for displaying and handling the login form.
    """

    referrer = request.get_referrer()

    # Redirect if already logged in.
    if request.user:
        return HTTPFound(location=referrer)

    form = Form(request, schema=UserLogin)
    if form.validate():
        user = authenticate_user(form.data['username'],
                                 form.data['password'],
                                 session=Session())
        if user:
            request.session.flash("%s logged in at %s" % (
                    user.display_name,
                    edbob.local_time().strftime('%I:%M %p')))
            headers = remember(request, user.uuid)
            return HTTPFound(location=referrer, headers=headers)
        request.session.flash("Invalid username or password")

    url = edbob.config.get('edbob.pyramid', 'login.logo_url',
                           default=request.static_url('edbob.pyramid:static/img/logo.jpg'))
    kwargs = eval(edbob.config.get('edbob.pyramid', 'login.logo_kwargs',
                                   default="dict(width=500)"))

    return {'form': FormRenderer(form), 'referrer': referrer,
            'logo_url': url, 'logo_kwargs': kwargs}


def logout(request):
    """
    View responsible for logging out the current user.

    This deletes/invalidates the current session and then redirects to the
    login page.
    """

    request.session.delete()
    request.session.invalidate()
    headers = forget(request)
    referrer = request.get_referrer()
    return HTTPFound(location=referrer, headers=headers)


def includeme(config):

    config.add_route('login', '/login')
    config.add_view(login, route_name='login', renderer='/login.mako')

    config.add_route('logout', '/logout')
    config.add_view(logout, route_name='logout')

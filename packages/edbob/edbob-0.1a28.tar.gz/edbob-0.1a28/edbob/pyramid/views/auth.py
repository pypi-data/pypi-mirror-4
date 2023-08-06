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

from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget

import formencode
from pyramid_simpleform import Form
import pyramid_simpleform.renderers

from webhelpers.html import tags
from webhelpers.html.builder import HTML

import edbob
from edbob.db.auth import authenticate_user, set_user_password
from edbob.pyramid import Session
from edbob.util import prettify


class FormRenderer(pyramid_simpleform.renderers.FormRenderer):
    """
    Customized form renderer.  Provides some extra methods for convenience.
    """

    # Note that as of this writing, this renderer is used only by the
    # ``change_password`` view.  This should probably change, and this class
    # definition should be moved elsewhere.

    def field_div(self, name, field, label=None):
        errors = self.errors_for(name)
        if errors:
            errors = [HTML.tag('div', class_='field-error', c=x) for x in errors]
            errors = tags.literal('').join(errors)

        label = HTML.tag('label', for_=name, c=label or prettify(name))
        inner = HTML.tag('div', class_='field', c=field)

        outer_class = 'field-wrapper'
        if errors:
            outer_class += ' error'
        outer = HTML.tag('div', class_=outer_class, c=(errors or '') + label + inner)
        return outer

    def referrer_field(self):
        return self.hidden('referrer', value=self.form.request.get_referrer())
        

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


class CurrentPasswordCorrect(formencode.validators.FancyValidator):

    def _to_python(self, value, state):
        user = state
        if not authenticate_user(user.username, value, session=Session()):
            raise formencode.Invalid("The password is incorrect.", value, state)
        return value


class ChangePassword(formencode.Schema):

    allow_extra_fields = True
    filter_extra_fields = True

    current_password = formencode.All(
        formencode.validators.NotEmpty(),
        CurrentPasswordCorrect())

    new_password = formencode.validators.NotEmpty()
    confirm_password = formencode.validators.NotEmpty()

    chained_validators = [formencode.validators.FieldsMatch(
            'new_password', 'confirm_password')]


def change_password(request):
    """
    Allows a user to change his or her password.
    """

    if not request.user:
        return HTTPFound(location=request.route_url('home'))

    form = Form(request, schema=ChangePassword, state=request.user)
    if form.validate():
        set_user_password(request.user, form.data['new_password'])
        return HTTPFound(location=request.get_referrer())

    return {'form': FormRenderer(form)}


def includeme(config):

    config.add_route('login', '/login')
    config.add_view(login, route_name='login', renderer='/login.mako')

    config.add_route('logout', '/logout')
    config.add_view(logout, route_name='logout')

    config.add_route('change_password', '/change-password')
    config.add_view(change_password, route_name='change_password', renderer='/change_password.mako')

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
``edbob.pyramid.forms.core`` -- Core Forms
"""

from sqlalchemy.util import OrderedDict

from webhelpers.html import literal, tags

import edbob
from edbob.util import requires_impl


__all__ = ['Form']


class Form(edbob.Object):
    """
    Generic form class.

    This class exists primarily so that rendering calls may mimic those used by
    FormAlchemy.
    """

    readonly = False
    successive = False

    action_url = None
    home_route = None
    home_url = None
    # template = None

    render_fields = OrderedDict()
    errors = {}

    # def __init__(self, request=None, action_url=None, home_url=None, template=None, **kwargs):
    def __init__(self, request=None, action_url=None, home_url=None, **kwargs):
        super(Form, self).__init__(**kwargs)
        self.request = request
        if action_url:
            self.action_url = action_url
        if request and not self.action_url:
            self.action_url = request.current_route_url()
        if home_url:
            self.home_url = home_url
        if request and not self.home_url:
            home = self.home_route if self.home_route else 'home'
            self.home_url = request.route_url(home)
        # if template:
        #     self.template = template
        # if not self.template:
        #     self.template = '%s.mako' % self.action_url

    @property
    def action_url(self):
        return self.request.current_route_url()

    def standard_buttons(self, submit="Save"):
        return literal(tags.submit('submit', submit) + ' ' + self.cancel_button())

    def cancel_button(self):
        return literal('<button type="button" class="cancel">Cancel</button>')

    def render(self, **kwargs):
        """
        Renders the form as HTML.  All keyword arguments are passed on to the
        template context.
        """

        return ''

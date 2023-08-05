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
``edbob.pyramid.views.form`` -- Generic Form View
"""

import transaction
from pyramid.httpexceptions import HTTPFound

from edbob.pyramid import Session
from edbob.pyramid.forms import SimpleForm
from edbob.util import requires_impl


__all__ = ['FormView']


class FormView(object):
    """
    This view provides basic form processing goodies.
    """

    route = None
    url = None
    template = None
    permission = None

    def __init__(self, request):
        self.request = request

    def __call__(self):
        """
        Callable for the view.  This method creates the underlying form and
        processes data if any was submitted.
        """

        f = self.form(self.request)
        if not f.readonly and self.request.POST:
            f.rebind(data=self.request.params)
            if f.validate():

                with transaction.manager:
                    f.save(Session)
                    Session.flush()
                    self.request.session.flash('The book "%s" has been loaned.' % f.book.value)

                if self.request.params.get('keep-going') == '1':
                    return HTTPFound(location=self.request.current_route_url())

                return HTTPFound(location=f.home_url)

        return {'form': f}

    def make_form(self, request, **kwargs):
        """
        Returns a :class:`edbob.pyramid.forms.Form` instance.
        """
        template = kwargs.pop('template', self.template or '%s.mako' % self.url)
        return SimpleForm(request, template=template, **kwargs)

    def form(self, request):
        """
        Should create and return a :class:`edbob.pyramid.forms.Form` instance
        for the view.
        """
        return self.make_form(request)

    @classmethod
    def add_route(cls, config, **kwargs):
        route = kwargs.get('route', cls.route)
        url = kwargs.get('url', cls.url)
        permission = kwargs.get('permission', cls.permission or route)
        template = kwargs.get('template', cls.template or '%s.mako' % url)
        config.add_route(route, url)
        config.add_view(cls, route_name=route, renderer=template,
                        permission=permission, http_cache=0)

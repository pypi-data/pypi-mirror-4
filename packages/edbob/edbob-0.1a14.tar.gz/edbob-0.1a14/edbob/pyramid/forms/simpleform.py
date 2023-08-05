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
``edbob.pyramid.forms.simpleform`` -- pyramid_simpleform Forms
"""

import pyramid_simpleform
from pyramid.renderers import render
from pyramid_simpleform.renderers import FormRenderer

from edbob.pyramid import helpers
from edbob.pyramid.forms import Form


__all__ = ['SimpleForm']


class SimpleForm(Form):

    template = None

    def __init__(self, request, **kwargs):
        super(SimpleForm, self).__init__(request, **kwargs)
        self.form = pyramid_simpleform.Form(request)

    def render(self, **kwargs):
        kw = {
            'form': self,
            }
        kw.update(kwargs)
        return render('/forms/form.mako', kw)

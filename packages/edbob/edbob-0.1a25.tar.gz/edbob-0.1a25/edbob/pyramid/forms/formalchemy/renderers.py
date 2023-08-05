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
``edbob.pyramid.forms.formalchemy.renderers`` -- Field Renderers
"""

import formalchemy

from pyramid.renderers import render


__all__ = ['AutocompleteFieldRenderer', 'EnumFieldRenderer',
           'YesNoFieldRenderer']


def AutocompleteFieldRenderer(service_url, field_value=None, field_display=None, width='300px'):
    """
    Autocomplete renderer.
    """

    class AutocompleteFieldRenderer(formalchemy.fields.FieldRenderer):

        @property
        def focus_name(self):
            return self.name + '-textbox'

        @property
        def needs_focus(self):
            return not bool(self.value or field_value)

        def render(self, **kwargs):
            kwargs.setdefault('field_name', self.name)
            kwargs.setdefault('field_value', self.value or field_value)
            kwargs.setdefault('field_display', self.raw_value or field_display)
            kwargs.setdefault('service_url', service_url)
            kwargs.setdefault('width', width)
            return render('/forms/field_autocomplete.mako', kwargs)

    return AutocompleteFieldRenderer


def EnumFieldRenderer(enum):
    """
    Adds support for enumeration fields.
    """

    class Renderer(formalchemy.fields.SelectFieldRenderer):
        
        def render_readonly(self, **kwargs):
            value = self.raw_value
            if value is None:
                return ''
            if value in enum:
                return enum[value]
            return str(value)

        def render(self, **kwargs):
            opts = [(enum[x], x) for x in sorted(enum)]
            return formalchemy.fields.SelectFieldRenderer.render(self, opts, **kwargs)

    return Renderer


class YesNoFieldRenderer(formalchemy.fields.CheckBoxFieldRenderer):

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if value is None:
            return ''
        return 'Yes' if value else 'No'

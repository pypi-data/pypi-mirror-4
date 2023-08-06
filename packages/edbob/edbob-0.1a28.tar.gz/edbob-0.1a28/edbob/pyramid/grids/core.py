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
``edbob.pyramid.grids.core`` -- Core Grid Classes
"""

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from webhelpers.html import HTML
from webhelpers.html.builder import format_attrs

from pyramid.renderers import render

import edbob


__all__ = ['Grid']


class Grid(edbob.Object):

    full = False
    hoverable = True
    clickable = False
    checkboxes = False
    editable = False
    deletable = False

    partial_only = False

    click_route_name = None
    click_route_kwargs = None

    edit_route_name = None
    edit_route_kwargs = None

    delete_route_name = None
    delete_route_kwargs = None

    def __init__(self, request, **kwargs):
        kwargs.setdefault('fields', OrderedDict())
        kwargs.setdefault('column_titles', {})
        kwargs.setdefault('extra_columns', [])
        super(Grid, self).__init__(**kwargs)
        self.request = request

    def add_column(self, name, label, callback):
        self.extra_columns.append(
            edbob.Object(name=name, label=label, callback=callback))

    def column_header(self, field):
        return HTML.tag('th', field=field.name,
                        title=self.column_titles.get(field.name),
                        c=field.label)

    def div_attrs(self):
        classes = ['grid']
        if self.full:
            classes.append('full')
        if self.clickable:
            classes.append('clickable')
        if self.hoverable:
            classes.append('hoverable')
        return format_attrs(
            class_=' '.join(classes),
            url=self.request.current_route_url())

    def get_delete_url(self, row):
        kwargs = {}
        if self.delete_route_kwargs:
            if callable(self.delete_route_kwargs):
                kwargs = self.delete_route_kwargs(row)
            else:
                kwargs = self.delete_route_kwargs
        return self.request.route_url(self.delete_route_name, **kwargs)

    def get_edit_url(self, row):
        kwargs = {}
        if self.edit_route_kwargs:
            if callable(self.edit_route_kwargs):
                kwargs = self.edit_route_kwargs(row)
            else:
                kwargs = self.edit_route_kwargs
        return self.request.route_url(self.edit_route_name, **kwargs)

    def get_row_attrs(self, row, i):
        attrs = self.row_attrs(row, i)
        if self.clickable:
            kwargs = {}
            if self.click_route_kwargs:
                if callable(self.click_route_kwargs):
                    kwargs = self.click_route_kwargs(row)
                else:
                    kwargs = self.click_route_kwargs
            attrs['url'] = self.request.route_url(self.click_route_name, **kwargs)
        return format_attrs(**attrs)

    def iter_fields(self):
        return self.fields.itervalues()

    def iter_rows(self):
        raise NotImplementedError

    def render(self, template='/grids/grid.mako', **kwargs):
        kwargs.setdefault('grid', self)
        return render(template, kwargs)

    def render_field(self, field):
        raise NotImplementedError

    def row_attrs(self, row, i):
        attrs = {'class_': 'odd' if i % 2 else 'even'}
        return attrs

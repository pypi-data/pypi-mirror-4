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
``edbob.pyramid.grids.alchemy`` -- FormAlchemy Grid Classes
"""

from webhelpers.html import tags
from webhelpers.html import HTML

import formalchemy

import edbob
from edbob.pyramid import Session
from edbob.pyramid.grids.core import Grid
from edbob.util import prettify


__all__ = ['AlchemyGrid']


class AlchemyGrid(Grid):

    sort_map = {}

    pager = None
    pager_format = '$link_first $link_previous ~1~ $link_next $link_last'

    def __init__(self, request, cls, instances, **kwargs):
        super(AlchemyGrid, self).__init__(request, **kwargs)
        self._formalchemy_grid = formalchemy.Grid(
            cls, instances, session=Session(), request=request)
        self._formalchemy_grid.prettify = prettify
        self.noclick_fields = []

    def __getattr__(self, attr):
        return getattr(self._formalchemy_grid, attr)

    def cell_class(self, field):
        classes = [field.name]
        if field.name in self.noclick_fields:
            classes.append('noclick')
        return ' '.join(classes)

    def checkbox(self, row):
        return tags.checkbox('check-'+row.uuid)

    def click_route_kwargs(self, row):
        return {'uuid': row.uuid}

    def column_header(self, field):
        class_ = None
        label = field.label()
        if field.key in self.sort_map:
            class_ = 'sortable'
            if field.key == self.config['sort']:
                class_ += ' sorted ' + self.config['dir']
            label = tags.link_to(label, '#')
        return HTML.tag('th', class_=class_, field=field.key,
                        title=self.column_titles.get(field.key), c=label)

    def edit_route_kwargs(self, row):
        return {'uuid': row.uuid}

    def delete_route_kwargs(self, row):
        return {'uuid': row.uuid}

    def iter_fields(self):
        return self._formalchemy_grid.render_fields.itervalues()

    def iter_rows(self):
        for row in self._formalchemy_grid.rows:
            self._formalchemy_grid._set_active(row)
            yield row

    def page_count_options(self):
        options = edbob.config.get('edbob.pyramid', 'grid.page_count_options')
        if options:
            options = options.split(',')
            options = [int(x.strip()) for x in options]
        else:
            options = [5, 10, 20, 50, 100]
        return options

    def page_links(self):
        return self.pager.pager(self.pager_format,
                                symbol_next='next',
                                symbol_previous='prev',
                                onclick="grid_navigate_page(this, '$partial_url'); return false;")

    def render_field(self, field):
        if self._formalchemy_grid.readonly:
            return field.render_readonly()
        return field.render()

    def row_attrs(self, row, i):
        attrs = super(AlchemyGrid, self).row_attrs(row, i)
        if hasattr(row, 'uuid'):
            attrs['uuid'] = row.uuid
        return attrs

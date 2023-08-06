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
``edbob.pyramid.views.grids`` -- Grid Views
"""

from webhelpers import paginate

from edbob.pyramid import grids
from edbob.pyramid import Session
from edbob.pyramid.views.grids.core import GridView
from edbob.util import requires_impl


__all__ = ['AlchemyGridView', 'SortableAlchemyGridView',
           'PagedAlchemyGridView', 'SearchableAlchemyGridView']


class AlchemyGridView(GridView):

    def make_query(self):
        q = Session.query(self.mapped_class)
        return q

    def query(self):
        return self.make_query()

    def make_grid(self, **kwargs):
        self.update_grid_kwargs(kwargs)
        return grids.AlchemyGrid(
            self.request, self.mapped_class, self._data, **kwargs)

    def grid(self):
        return self.make_grid()

    def __call__(self):
        self._data = self.query()
        grid = self.grid()
        return grids.util.render_grid(grid)


class SortableAlchemyGridView(AlchemyGridView):

    sort = None

    @property
    @requires_impl(is_property=True)
    def config_prefix(self):
        pass

    def join_map(self):
        return {}

    def make_sort_map(self, *args, **kwargs):
        return grids.util.get_sort_map(
            self.mapped_class, names=args or None, **kwargs)

    def sorter(self, field):
        return grids.util.sorter(field)

    def sort_map(self):
        return self.make_sort_map()

    def make_sort_config(self, **kwargs):
        return grids.util.get_sort_config(
            self.config_prefix, self.request, **kwargs)

    def sort_config(self):
        return self.make_sort_config(sort=self.sort)

    def make_query(self):
        query = Session.query(self.mapped_class)
        query = grids.util.sort_query(
            query, self._sort_config, self.sort_map(), self.join_map())
        return query

    def query(self):
        return self.make_query()

    def make_grid(self, **kwargs):
        self.update_grid_kwargs(kwargs)
        return grids.AlchemyGrid(
            self.request, self.mapped_class, self._data,
            sort_map=self.sort_map(), config=self._sort_config, **kwargs)

    def grid(self):
        return self.make_grid()

    def __call__(self):
        self._sort_config = self.sort_config()
        self._data = self.query()
        grid = self.grid()
        return grids.util.render_grid(grid)


class PagedAlchemyGridView(SortableAlchemyGridView):

    full = True

    def make_pager(self):
        config = self._sort_config
        query = self.query()
        return paginate.Page(
            query, item_count=query.count(),
            items_per_page=int(config['per_page']),
            page=int(config['page']),
            url=paginate.PageURL_WebOb(self.request))

    def __call__(self):
        self._sort_config = self.sort_config()
        self._data = self.make_pager()
        grid = self.grid()
        grid.pager = self._data
        return grids.util.render_grid(grid)


class SearchableAlchemyGridView(PagedAlchemyGridView):

    def filter_exact(self, field):
        return grids.search.filter_exact(field)

    def filter_ilike(self, field):
        return grids.search.filter_ilike(field)

    def make_filter_map(self, **kwargs):
        return grids.search.get_filter_map(self.mapped_class, **kwargs)

    def filter_map(self):
        return self.make_filter_map()

    def make_filter_config(self, **kwargs):
        return grids.search.get_filter_config(
            self.config_prefix, self.request, self.filter_map(), **kwargs)

    def filter_config(self):
        return self.make_filter_config()

    def make_search_form(self):
        return grids.search.get_search_form(
            self.request, self.filter_map(), self._filter_config)

    def search_form(self):
        return self.make_search_form()

    def make_query(self, session=Session):
        join_map = self.join_map()
        query = session.query(self.mapped_class)
        query = grids.search.filter_query(
            query, self._filter_config, self.filter_map(), join_map)
        if hasattr(self, '_sort_config'):
            self._sort_config['joins'] = self._filter_config['joins']
            query = grids.util.sort_query(
                query, self._sort_config, self.sort_map(), join_map)
        return query

    def __call__(self):
        self._filter_config = self.filter_config()
        search = self.search_form()
        self._sort_config = self.sort_config()
        self._data = self.make_pager()
        grid = self.grid()
        grid.pager = self._data
        kwargs = self.render_kwargs()
        return grids.util.render_grid(grid, search, **kwargs)

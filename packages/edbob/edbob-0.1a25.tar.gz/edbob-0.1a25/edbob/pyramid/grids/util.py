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
``edbob.pyramid.grids.util`` -- Grid Utilities
"""

from sqlalchemy.orm.attributes import InstrumentedAttribute

from webhelpers.html import literal

from pyramid.response import Response

from edbob.pyramid.grids.search import SearchFormRenderer


def get_sort_config(name, request, **kwargs):
    """
    Returns a configuration dictionary for grid sorting.
    """

    # Initial config uses some default values.
    config = {
        'dir': 'asc',
        'per_page': 20,
        'page': 1,
        }

    # Override with defaults provided by caller.
    config.update(kwargs)

    # Override with values from GET/POST request and/or session.
    for key in config:
        full_key = name+'_'+key
        if request.params.get(key):
            value = request.params[key]
            config[key] = value
            request.session[full_key] = value
        elif request.session.get(full_key):
            value = request.session[full_key]
            config[key] = value

    return config


def get_sort_map(cls, names=None, **kwargs):
    """
    Convenience function which returns a sort map for ``cls``.

    If ``names`` is not specified, the map will include all "standard" fields
    present on the mapped class.  Otherwise, the map will be limited to only
    the fields which are named.

    All remaining ``kwargs`` are assumed to be sort map entries, and will be
    added to the map directly.
    """

    smap = {}
    if names is None:
        names = []
        for attr in cls.__dict__:
            obj = getattr(cls, attr)
            if isinstance(obj, InstrumentedAttribute):
                if obj.key != 'uuid':
                    names.append(obj.key)
    for name in names:
        smap[name] = sorter(getattr(cls, name))
    smap.update(kwargs)
    return smap


def render_grid(grid, search_form=None, **kwargs):
    """
    Convenience function to render ``grid`` (which should be a
    :class:`edbob.pyramid.grids.Grid` instance).

    This "usually" will return a dictionary to be used as context for rendering
    the final view template.

    However, if a partial grid is requested (or mandated), then the grid body
    will be rendered and a :class:`pyramid.response.Response` object will be
    returned instead.
    """

    if grid.partial_only or grid.request.params.get('partial'):
        return Response(body=grid.render(), content_type='text/html')
    kwargs['grid'] = literal(grid.render())
    if search_form:
        kwargs['search'] = SearchFormRenderer(search_form)
    return kwargs


def sort_query(query, config, sort_map, join_map={}):
    """
    Sorts ``query`` according to ``config`` and ``sort_map``.  ``join_map`` is
    used, if necessary, to join additional tables to the base query.  The
    sorted query is returned.
    """

    field = config.get('sort')
    if not field:
        return query
    joins = config.setdefault('joins', [])
    if field in join_map and field not in joins:
        query = join_map[field](query)
        joins.append(field)
    sort = sort_map[field]
    return sort(query, config['dir'])


def sorter(field):
    """
    Returns a function suitable for a sort map callable, with typical logic
    built in for sorting applied to ``field``.
    """

    return lambda q, d: q.order_by(getattr(field, d)())

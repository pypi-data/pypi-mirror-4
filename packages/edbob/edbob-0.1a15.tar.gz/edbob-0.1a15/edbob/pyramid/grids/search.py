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
``edbob.pyramid.grids.search`` -- Grid Search Filters
"""

from sqlalchemy import or_

from webhelpers.html import tags
from webhelpers.html import literal

from pyramid.renderers import render
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

import edbob
from edbob.util import prettify


class SearchFilter(edbob.Object):
    """
    Base class and default implementation for search filters.
    """

    def __init__(self, name, label=None, **kwargs):
        edbob.Object.__init__(self, **kwargs)
        self.name = name
        self.label = label or prettify(name)

    def types_select(self):
        types = [
            ('is', "is"),
            ('nt', "is not"),
            ('lk', "contains"),
            ('nl', "doesn't contain"),
            ]
        options = []
        filter_map = self.search.filter_map[self.name]
        for value, label in types:
            if value in filter_map:
                options.append((value, label))
        return tags.select('filter_type_'+self.name,
                           self.search.config.get('filter_type_'+self.name),
                           options, class_='filter-type')

    def value_control(self):
        return tags.text(self.name, self.search.config.get(self.name))


class BooleanSearchFilter(SearchFilter):
    """
    Boolean search filter.
    """

    def value_control(self):
        return tags.select(self.name, self.search.config.get(self.name),
                           ["True", "False"])


class SearchForm(Form):
    """
    Generic form class which aggregates :class:`SearchFilter` instances.
    """

    def __init__(self, request, filter_map, config, *args, **kwargs):
        super(SearchForm, self).__init__(request, *args, **kwargs)
        self.filter_map = filter_map
        self.config = config
        self.filters = {}

    def add_filter(self, filter_):
        filter_.search = self
        self.filters[filter_.name] = filter_


class SearchFormRenderer(FormRenderer):
    """
    Renderer for :class:`SearchForm` instances.
    """

    def __init__(self, form, *args, **kwargs):
        super(SearchFormRenderer, self).__init__(form, *args, **kwargs)
        self.request = form.request
        self.filters = form.filters
        self.config = form.config

    def add_filter(self, visible):
        options = ['add a filter']
        for f in self.sorted_filters():
            options.append((f.name, f.label))
        return self.select('add-filter', options,
                           style='display: none;' if len(visible) == len(self.filters) else None)

    def checkbox(self, name, checked=None, **kwargs):
        if name.startswith('include_filter_'):
            if checked is None:
                checked = self.config[name]
            return tags.checkbox(name, checked=checked, **kwargs)
        if checked is None:
            checked = False
        return super(SearchFormRenderer, self).checkbox(name, checked=checked, **kwargs)

    def render(self, **kwargs):
        kwargs['search'] = self
        return literal(render('/grids/search.mako', kwargs))

    def sorted_filters(self):
        return sorted(self.filters.values(), key=lambda x: x.label)

    def text(self, name, **kwargs):
        return tags.text(name, value=self.config.get(name), **kwargs)


def filter_exact(field):
    """
    Convenience function which returns a filter map entry, with typical logic
    built in for "exact match" queries applied to ``field``.
    """

    return {
        'is':
            lambda q, v: q.filter(field == v) if v else q,
        'nt':
            lambda q, v: q.filter(field != v) if v else q,
        }


def filter_ilike(field):
    """
    Convenience function which returns a filter map entry, with typical logic
    built in for "ILIKE" queries applied to ``field``.
    """

    def ilike(query, value):
        if value:
            query = query.filter(field.ilike('%%%s%%' % value))
        return query

    def not_ilike(query, value):
        if value:
            query = query.filter(or_(
                    field == None,
                    ~field.ilike('%%%s%%' % value),
                    ))
        return query
    
    return {'lk': ilike, 'nl': not_ilike}


def get_filter_config(prefix, request, filter_map, **kwargs):
    """
    Returns a configuration dictionary for a search form.
    """

    config = {}

    def update_config(dict_, prefix='', exclude_by_default=False):
        """
        Updates the ``config`` dictionary based on the contents of ``dict_``.
        """

        for field in filter_map:
            if prefix+'include_filter_'+field in dict_:
                include = dict_[prefix+'include_filter_'+field]
                include = bool(include) and include != '0'
                config['include_filter_'+field] = include
            elif exclude_by_default:
                config['include_filter_'+field] = False
            if prefix+'filter_type_'+field in dict_:
                config['filter_type_'+field] = dict_[prefix+'filter_type_'+field]
            if prefix+field in dict_:
                config[field] = dict_[prefix+field]

    # Update config to exclude all filters by default.
    for field in filter_map:
        config['include_filter_'+field] = False

    # Update config to honor default settings.
    config.update(kwargs)

    # Update config with data cached in session.
    update_config(request.session, prefix=prefix+'.')

    # Update config with data from GET/POST request.
    if request.params.get('filters') == 'true':
        update_config(request.params, exclude_by_default=True)

    # Cache filter data in session.
    for key in config:
        if (not key.startswith('filter_factory_')
            and not key.startswith('filter_label_')):
            request.session[prefix+'.'+key] = config[key]

    return config


def get_filter_map(cls, exact=[], ilike=[], **kwargs):
    """
    Convenience function which returns a "filter map" for ``cls``.

    ``exact``, if provided, should be a list of field names for which "exact"
    filtering is to be allowed.

    ``ilike``, if provided, should be a list of field names for which "ILIKE"
    filtering is to be allowed.

    Any remaining ``kwargs`` are assumed to be filter map entries themselves,
    and are added directly to the map.
    """

    fmap = {}
    for name in exact:
        fmap[name] = filter_exact(getattr(cls, name))
    for name in ilike:
        fmap[name] = filter_ilike(getattr(cls, name))
    fmap.update(kwargs)
    return fmap


def get_search_form(request, filter_map, config):
    """
    Returns a :class:`SearchForm` instance with a :class:`SearchFilter` for
    each filter in ``filter_map``, using configuration from ``config``.
    """

    search = SearchForm(request, filter_map, config)
    for field in filter_map:
        factory = config.get('filter_factory_%s' % field, SearchFilter)
        label = config.get('filter_label_%s' % field)
        search.add_filter(factory(field, label=label))
    return search


def filter_query(query, config, filter_map, join_map):
    """
    Filters ``query`` according to ``config`` and ``filter_map``.  ``join_map``
    is used, if necessary, to join additional tables to the base query.  The
    filtered query is returned.
    """

    joins = config.setdefault('joins', [])
    for key in config:
        if key.startswith('include_filter_') and config[key]:
            field = key[15:]
            if field in join_map and field not in joins:
                query = join_map[field](query)
                joins.append(field)
            value = config.get(field)
            if value:
                fmap = filter_map[field]
                filt = fmap[config['filter_type_'+field]]
                query = filt(query, value)
    return query

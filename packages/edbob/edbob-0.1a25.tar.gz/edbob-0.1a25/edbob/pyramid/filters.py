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
``edbob.pyramid.filters`` -- Search Filters
"""

import re

from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer
from webhelpers.html import tags

import edbob
from edbob.util import prettify


__all__ = ['SearchFilter', 'SearchForm']


class SearchFilter(edbob.Object):

    def __init__(self, name, label=None, **kwargs):
        edbob.Object.__init__(self, **kwargs)
        self.name = name
        self.label = label or prettify(name)

    def types_select(self):
        types = [
            ('is', 'is'),
            ('nt', 'is not'),
            ('lk', 'contains'),
            ('nl', 'doesn\'t contain'),
            ]
        options = []
        filter_map = self.search.config['filter_map'][self.name]
        for value, label in types:
            if value in filter_map:
                options.append((value, label))
        return tags.select('filter_type_'+self.name,
                           self.search.config.get('filter_type_'+self.name),
                           options, class_='filter-type')

    def value_control(self):
        return tags.text(self.name, self.search.config.get(self.name))


class SearchForm(Form):

    def __init__(self, request, filters, config, *args, **kwargs):
        Form.__init__(self, request, *args, **kwargs)
        self.filters = filters
        for f in filters:
            filters[f].search = self
        self.config = config


class SearchFormRenderer(FormRenderer):

    def __init__(self, form, *args, **kwargs):
        FormRenderer.__init__(self, form, *args, **kwargs)
        self.filters = form.filters
        self.config = form.config

    def checkbox(self, name, checked=None, *args, **kwargs):
        if name.startswith('include_filter_'):
            if checked is None:
                checked = self.config[name]
            return tags.checkbox(name, checked=checked, *args, **kwargs)
        if checked is None:
            checked = False
        return FormRenderer.checkbox(self, name, checked=checked, *args, **kwargs)

    def text(self, name, *args, **kwargs):
        return tags.text(name, value=self.config.get(name), *args, **kwargs)

    def sorted_filters(self):
        return sorted(self.filters, key=lambda x: self.filters[x].label)

    def add_filter(self, visible):
        options = ['add a filter']
        for f in sorted(self.filters):
            f = self.filters[f]
            options.append((f.name, f.label))
        return self.select('add-filter', options,
                           style='display: none;' if len(visible) == len(self.filters) else None)

    def render(self, **kwargs):
        from formalchemy import config
        return config.engine('filterset', search=self, **kwargs)


def filter_exact(field):
    """
    Returns a filter map entry, with typical logic built in for "exact match"
    queries applied to ``field``.
    """
    return {
        'is':
            lambda q, v: q.filter(field == v) if v else q,
        'nt':
            lambda q, v: q.filter(field != v) if v else q,
        }


def filter_ilike(field):
    """
    Returns a filter map entry, with typical logic built in for ILIKE queries
    applied to ``field``.
    """
    return {
        'lk':
            lambda q, v: q.filter(field.ilike('%%%s%%' % v)) if v else q,
        'nl':
            lambda q, v: q.filter(~field.ilike('%%%s%%' % v)) if v else q,
        }


def filter_query(query, config, join_map={}):
    filter_map = config['filter_map']
    if config.get('search'):
        search = config['search'].config
        joins = config.setdefault('joins', [])
        include_filter = re.compile(r'^include_filter_(.*)$')
        for key in search:
            m = include_filter.match(key)
            if m and search[key]:
                field = m.group(1)
                if field in join_map and field not in joins:
                    query = join_map[field](query)
                    joins.append(field)
                value = search.get(field)
                if value:
                    f = filter_map[field][search['filter_type_'+field]]
                    query = f(query, value)
    return query


def get_filter_map(cls, exact=[], ilike=[], **kwargs):
    """
    Convenience function which returns a filter map for ``cls``.  All fields
    represented by ``names`` will be included in the map.

    Each field's entry will use the :func:`filter_ilike()` function unless the
    field's name is also found within ``exact``, in which case the
    :func:`filter_exact()` function will be used instead.
    """

    fmap = {}
    for name in exact:
        fmap[name] = filter_exact(getattr(cls, name))
    for name in ilike:
        fmap[name] = filter_ilike(getattr(cls, name))
    fmap.update(kwargs)
    return fmap


def get_search_config(name, request, filter_map, **kwargs):
    """
    Returns a dictionary of configuration options for a search form.
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

    # Update config with defaults from ``kwargs``.
    config.update(kwargs)

    # Update config with data cached in Beaker session.
    update_config(request.session, prefix=name+'.')

    # Update config with data from GET/POST request.
    if request.params.get('filters'):
        update_config(request.params, exclude_by_default=True)

    # Cache filter data in Beaker session.
    for key in config:
        if not key.startswith('filter_factory_'):
            request.session[name+'.'+key] = config[key]

    config['request'] = request
    config['filter_map'] = filter_map
    return config


def get_search_form(config, **labels):
    filters = {}
    for field in config['filter_map']:
        factory = config.get('filter_factory_%s' % field, SearchFilter)
        filters[field] = factory(field, label=labels.get(field))
    return SearchForm(config['request'], filters, config)

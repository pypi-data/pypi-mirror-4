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
``edbob.pyramid.views.autocomplete`` -- Autocomplete View
"""

from edbob.pyramid import Session
from edbob.pyramid.views.core import View
from edbob.util import requires_impl


__all__ = ['AutocompleteView']


class AutocompleteView(View):

    @property
    @requires_impl(is_property=True)
    def mapped_class(self):
        raise NotImplementedError

    @property
    @requires_impl(is_property=True)
    def fieldname(self):
        raise NotImplementedError

    def filter_query(self, q):
        return q

    def make_query(self, query):
        q = Session.query(self.mapped_class)
        q = self.filter_query(q)
        q = q.filter(getattr(self.mapped_class, self.fieldname).ilike('%%%s%%' % query))
        q = q.order_by(getattr(self.mapped_class, self.fieldname))
        return q

    def query(self, query):
        return self.make_query(query)

    def display(self, instance):
        return getattr(instance, self.fieldname)

    def __call__(self):
        query = self.request.params['query']
        objs = self.query(query).all()
        data = dict(
            query=query,
            suggestions=[self.display(x) for x in objs],
            data=[x.uuid for x in objs],
            )
        return data

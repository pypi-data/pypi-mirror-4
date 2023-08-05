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
``edbob.pyramid.forms.formalchemy.fieldset`` -- FormAlchemy FieldSet
"""

import formalchemy

from edbob.pyramid import Session
from edbob.util import prettify


__all__ = ['FieldSet', 'make_fieldset']


class FieldSet(formalchemy.FieldSet):
    """
    Adds a little magic to the :class:`formalchemy.FieldSet` class.
    """

    prettify = staticmethod(prettify)

    def __init__(self, model, class_name=None, crud_title=None, url=None,
                 route_name=None, action_url='', home_url=None, **kwargs):
        super(FieldSet, self).__init__(model, **kwargs)
        self.class_name = class_name or self._original_cls.__name__.lower()
        self.crud_title = crud_title or prettify(self.class_name)
        self.edit = isinstance(model, self._original_cls)
        self.route_name = route_name or (self.class_name + 's')
        self.action_url = action_url
        self.home_url = home_url
        self.allow_continue = kwargs.pop('allow_continue', False)

    def get_display_text(self):
        return unicode(self.model)

    def render(self, **kwargs):
        kwargs.setdefault('class_', self.class_name)
        return super(FieldSet, self).render(**kwargs)


def make_fieldset(model, **kwargs):
    """
    Returns a :class:`FieldSet` equipped with the current scoped
    :class:`edbob.db.Session` instance (unless ``session`` is provided as a
    keyword argument).
    """

    kwargs.setdefault('session', Session())
    return FieldSet(model, **kwargs)

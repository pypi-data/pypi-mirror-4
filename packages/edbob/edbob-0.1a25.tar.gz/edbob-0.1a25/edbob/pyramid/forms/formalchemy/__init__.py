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
``edbob.pyramid.forms.formalchemy`` -- FormAlchemy Interface
"""

from __future__ import absolute_import

import datetime

from pyramid.renderers import render
from webhelpers.html.tags import literal

import formalchemy
from formalchemy.validators import accepts_none

import edbob
from edbob.lib import pretty
from edbob.pyramid import Session
from edbob.time import localize
from edbob.util import requires_impl

from edbob.pyramid.forms.formalchemy.fieldset import *
from edbob.pyramid.forms.formalchemy.fields import *
from edbob.pyramid.forms.formalchemy.renderers import *


__all__ = ['ChildGridField', 'PropertyField', 'EnumFieldRenderer',
           'PrettyDateTimeFieldRenderer', 'AutocompleteFieldRenderer',
           'FieldSet', 'make_fieldset', 'required', 'pretty_datetime',
           'AssociationProxyField', 'YesNoFieldRenderer']


class TemplateEngine(formalchemy.templates.TemplateEngine):
    """
    Mako template engine for FormAlchemy.
    """

    def render(self, template, prefix='/forms/', suffix='.mako', **kwargs):
        template = ''.join((prefix, template, suffix))
        return render(template, kwargs)


# Make our TemplateEngine the default.
engine = TemplateEngine()
formalchemy.config.engine = engine


class AlchemyForm(edbob.Object):
    """
    Form to contain a :class:`formalchemy.FieldSet` instance.
    """

    create_label = "Create"
    update_label = "Update"

    allow_successive_creates = False

    def __init__(self, request, fieldset, **kwargs):
        edbob.Object.__init__(self, **kwargs)
        self.request = request
        self.fieldset = fieldset

    def _get_readonly(self):
        return self.fieldset.readonly

    def _set_readonly(self, val):
        self.fieldset.readonly = val

    readonly = property(_get_readonly, _set_readonly)

    @property
    def successive_create_label(self):
        return "%s and continue" % self.create_label

    def render(self, **kwargs):
        kwargs['form'] = self
        if self.readonly:
            template = '/forms/form_readonly.mako'
        else:
            template = '/forms/form.mako'
        return render(template, kwargs)

    def save(self):
        self.fieldset.sync()
        Session.flush()

    def validate(self):
        self.fieldset.rebind(data=self.request.params)
        return self.fieldset.validate()


class ChildGridField(formalchemy.Field):
    """
    Convenience class for including a child grid within a fieldset as a
    read-only field.
    """

    def __init__(self, name, value, *args, **kwargs):
        super(ChildGridField, self).__init__(name, *args, **kwargs)
        self.set(value=value)
        self.set(readonly=True)


class PropertyField(formalchemy.Field):
    """
    Convenience class for fields which simply involve a read-only property
    value.
    """

    def __init__(self, name, attr=None, *args, **kwargs):
        super(PropertyField, self).__init__(name, *args, **kwargs)
        if not attr:
            attr = name
        self.set(value=lambda x: getattr(x, attr))
        self.set(readonly=True)


@accepts_none
def required(value, field=None):
    if value is None or value == '':
        msg = "Please provide a value"
        if field:
            msg = "You must provide a value for %s" % field.label()
        raise formalchemy.ValidationError(msg)


def pretty_datetime(value, from_='local', to='local'):
    """
    Formats a ``datetime.datetime`` instance and returns a "pretty"
    human-readable string from it, e.g. "42 minutes ago".  ``value`` is
    rendered directly as a string if no date/time can be parsed from it.
    """

    if not isinstance(value, datetime.datetime):
        return str(value) if value else ''
    if not value.tzinfo:
        value = localize(value, from_=from_, to=to)
    return literal('<span title="%s">%s</span>' % (
            value.strftime('%Y-%m-%d %H:%M:%S %Z%z'),
            pretty.date(value)))    


def PrettyDateTimeFieldRenderer(from_='local', to='local'):

    class PrettyDateTimeFieldRenderer(formalchemy.fields.DateTimeFieldRenderer):

        def render_readonly(self, **kwargs):
            return pretty_datetime(self.raw_value, from_=from_, to=to)

    return PrettyDateTimeFieldRenderer


class DateTimeFieldRenderer(formalchemy.fields.DateTimeFieldRenderer):
    """
    Leverages edbob time system to coerce timestamp to local time zone before
    displaying it.
    """

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if isinstance(value, datetime.datetime):
            value = edbob.local_time(value)
            return value.strftime(self.format)
        return ''

FieldSet.default_renderers[formalchemy.types.DateTime] = DateTimeFieldRenderer

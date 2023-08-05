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
``edbob.pyramid.views.users`` -- User Views
"""

from webhelpers.html import literal, tags

import formalchemy
from formalchemy.fields import SelectFieldRenderer

import edbob
from edbob.db.auth import set_user_password
from edbob.pyramid import Session
from edbob.pyramid.views import SearchableAlchemyGridView, CrudView


class UsersGrid(SearchableAlchemyGridView):

    mapped_class = edbob.User
    config_prefix = 'users'
    sort = 'username'

    def join_map(self):
        return {
            'person':
                lambda q: q.outerjoin(edbob.Person),
            }

    def filter_map(self):
        return self.make_filter_map(
            ilike=['username'],
            person=self.filter_ilike(edbob.Person.display_name))

    def filter_config(self):
        return self.make_filter_config(
            include_filter_username=True,
            filter_type_username='lk',
            include_filter_person=True,
            filter_type_person='lk')

    def sort_map(self):
        return self.make_sort_map(
            'username',
            person=self.sorter(edbob.Person.display_name))

    def grid(self):
        g = self.make_grid()
        g.configure(
            include=[
                g.username,
                g.person,
                ],
            readonly=True)
        if self.request.has_perm('users.read'):
            g.clickable = True
            g.click_route_name = 'user.read'
        if self.request.has_perm('users.update'):
            g.editable = True
            g.edit_route_name = 'user.update'
        if self.request.has_perm('users.delete'):
            g.deletable = True
            g.delete_route_name = 'user.delete'
        return g


class _RolesFieldRenderer(SelectFieldRenderer):

    def render_readonly(self, **kwargs):
        roles = Session.query(edbob.Role)
        res = literal('<ul>')
        for uuid in self.value:
            role = roles.get(uuid)
            res += literal('<li>%s</li>' % (
                    tags.link_to(role.name,
                                 self.request.route_url('role.edit', uuid=role.uuid))))
        res += literal('</ul>')
        return res


def RolesFieldRenderer(request):
    return type('RolesFieldRenderer', (_RolesFieldRenderer,), {'request': request})


class RolesField(formalchemy.Field):

    def __init__(self, name, **kwargs):
        kwargs.setdefault('value', self.get_value)
        kwargs.setdefault('options', self.get_options())
        kwargs.setdefault('multiple', True)
        super(RolesField, self).__init__(name, **kwargs)

    def get_value(self, user):
        return [x.uuid for x in user.roles]

    def get_options(self):
        q = Session.query(edbob.Role.name, edbob.Role.uuid)
        q = q.order_by(edbob.Role.name)
        return q.all()

    def sync(self):
        if not self.is_readonly():
            user = self.model
            roles = Session.query(edbob.Role)
            data = self.renderer.deserialize()
            user.roles = [roles.get(x) for x in data]
                

class _ProtectedPersonRenderer(formalchemy.FieldRenderer):

    def render_readonly(self, **kwargs):
        res = str(self.person)
        res += tags.hidden('User--person_uuid',
                           value=self.field.parent.person_uuid.value)
        return res


def ProtectedPersonRenderer(uuid):
    person = Session.query(edbob.Person).get(uuid)
    assert person
    return type('ProtectedPersonRenderer', (_ProtectedPersonRenderer,),
                {'person': person})


class _LinkedPersonRenderer(formalchemy.FieldRenderer):

    def render_readonly(self, **kwargs):
        return tags.link_to(str(self.raw_value),
                            self.request.route_url('person.edit', uuid=self.value))


def LinkedPersonRenderer(request):
    return type('LinkedPersonRenderer', (_LinkedPersonRenderer,),
                {'request': request})


class PasswordFieldRenderer(formalchemy.PasswordFieldRenderer):

    def render(self, **kwargs):
        return tags.password(self.name, value='', maxlength=self.length, **kwargs)


def passwords_match(value, field):
    if field.parent.confirm_password.value != value:
        raise formalchemy.ValidationError("Passwords do not match")
    return value


class PasswordField(formalchemy.Field):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('value', lambda x: x.password)
        kwargs.setdefault('renderer', PasswordFieldRenderer)
        kwargs.setdefault('validate', passwords_match)
        super(PasswordField, self).__init__(*args, **kwargs)

    def sync(self):
        if not self.is_readonly():
            password = self.renderer.deserialize()
            if password:
                set_user_password(self.model, password)


class UserCrud(CrudView):

    mapped_class = edbob.User
    home_route = 'users'

    def fieldset(self, user):
        fs = self.make_fieldset(user)

        fs.append(PasswordField('password'))
        fs.append(formalchemy.Field('confirm_password',
                                    renderer=PasswordFieldRenderer))
        fs.append(RolesField('roles',
                             renderer=RolesFieldRenderer(self.request)))

        fs.configure(
            include=[
                fs.username,
                fs.person,
                fs.password.label("Set Password"),
                fs.confirm_password,
                fs.roles,
                ])

        # if fs.edit and user.person:
        if isinstance(user, edbob.User) and user.person:
            fs.person.set(readonly=True,
                          renderer=LinkedPersonRenderer(self.request))

        return fs

    def validation_failed(self, fs):
        if not fs.edit and fs.person_uuid.value:
            fs.person.set(readonly=True,
                          renderer=ProtectedPersonRenderer(fs.person_uuid.value))


def includeme(config):

    config.add_route('users', '/users')
    config.add_view(UsersGrid, route_name='users',
                    renderer='/users/index.mako',
                    permission='users.list')

    config.add_route('user.create', '/users/new')
    config.add_view(UserCrud, attr='create', route_name='user.create',
                    renderer='/users/crud.mako',
                    permission='users.create')

    config.add_route('user.read', '/users/{uuid}')
    config.add_view(UserCrud, attr='read', route_name='user.read',
                    renderer='/users/crud.mako',
                    permission='users.read')

    config.add_route('user.update', '/users/{uuid}/edit')
    config.add_view(UserCrud, attr='update', route_name='user.update',
                    renderer='/users/crud.mako',
                    permission='users.update')

    config.add_route('user.delete', '/users/{uuid}/delete')
    config.add_view(UserCrud, attr='delete', route_name='user.delete',
                    permission='users.delete')

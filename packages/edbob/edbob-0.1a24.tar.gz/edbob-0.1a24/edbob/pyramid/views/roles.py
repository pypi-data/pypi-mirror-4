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
``edbob.pyramid.views.roles`` -- Role Views
"""

from pyramid.httpexceptions import HTTPFound

import formalchemy
from webhelpers.html import tags
from webhelpers.html.builder import HTML

import edbob
from edbob.db import auth
from edbob.pyramid import Session
from edbob.pyramid.views import SearchableAlchemyGridView, CrudView


default_permissions = [

    ("People", [
            ('people.list',         "List People"),
            ('people.read',         "View Person"),
            ('people.create',       "Create Person"),
            ('people.update',       "Edit Person"),
            ('people.delete',       "Delete Person"),
            ]),

    ("Roles", [
            ('roles.list',          "List Roles"),
            ('roles.read',          "View Role"),
            ('roles.create',        "Create Role"),
            ('roles.update',        "Edit Role"),
            ('roles.delete',        "Delete Role"),
            ]),

    ("Users", [
            ('users.list',          "List Users"),
            ('users.read',          "View User"),
            ('users.create',        "Create User"),
            ('users.update',        "Edit User"),
            ('users.delete',        "Delete User"),
            ]),
    ]


class RolesGrid(SearchableAlchemyGridView):

    mapped_class = edbob.Role
    config_prefix = 'roles'
    sort = 'name'

    def filter_map(self):
        return self.make_filter_map(ilike=['name'])

    def filter_config(self):
        return self.make_filter_config(
            include_filter_name=True,
            filter_type_name='lk')

    def sort_map(self):
        return self.make_sort_map('name')

    def grid(self):
        g = self.make_grid()
        g.configure(
            include=[
                g.name,
                ],
            readonly=True)
        if self.request.has_perm('roles.read'):
            g.clickable = True
            g.click_route_name = 'role.read'
        if self.request.has_perm('roles.update'):
            g.editable = True
            g.edit_route_name = 'role.update'
        if self.request.has_perm('roles.delete'):
            g.deletable = True
            g.delete_route_name = 'role.delete'
        return g


class PermissionsField(formalchemy.Field):

    def sync(self):
        if not self.is_readonly():
            role = self.model
            role.permissions = self.renderer.deserialize()


def PermissionsFieldRenderer(permissions, *args, **kwargs):

    perms = permissions
    
    class PermissionsFieldRenderer(formalchemy.FieldRenderer):

        permissions = perms

        def deserialize(self):
            perms = []
            i = len(self.name) + 1
            for key in self.params:
                if key.startswith(self.name):
                    perms.append(key[i:])
            return perms

        def _render(self, readonly=False, **kwargs):
            role = self.field.model
            admin = auth.administrator_role(Session())
            if role is admin:
                html = HTML.tag('p', c="This is the administrative role; "
                                "it has full access to the entire system.")
                if not readonly:
                    html += tags.hidden(self.name, value='') # ugly hack..or good idea?
            else:
                html = ''
                for group, perms in self.permissions:
                    inner = HTML.tag('p', c=group)
                    for perm, title in perms:
                        checked = auth.has_permission(
                            role, perm, include_guest=False, session=Session())
                        if readonly:
                            span = HTML.tag('span', c="[X]" if checked else "[ ]")
                            inner += HTML.tag('p', class_='perm', c=span + ' ' + title)
                        else:
                            inner += tags.checkbox(self.name + '-' + perm,
                                                   checked=checked, label=title)
                    html += HTML.tag('div', class_='group', c=inner)
            return html

        def render(self, **kwargs):
            return self._render(**kwargs)

        def render_readonly(self, **kwargs):
            return self._render(readonly=True, **kwargs)

    return PermissionsFieldRenderer


class RoleCrud(CrudView):

    mapped_class = edbob.Role
    home_route = 'roles'
    permissions = default_permissions

    def fieldset(self, role):
        fs = self.make_fieldset(role)
        fs.append(PermissionsField(
                'permissions',
                renderer=PermissionsFieldRenderer(self.permissions)))
        fs.configure(
            include=[
                fs.name,
                fs.permissions,
                ])
        return fs

    def pre_delete(self, model):
        admin = auth.administrator_role(Session())
        guest = auth.guest_role(Session())
        if model in (admin, guest):
            self.request.session.flash("You may not delete the %s role." % str(model), 'error')
            return HTTPFound(location=self.request.get_referrer())


def includeme(config):
    
    config.add_route('roles', '/roles')
    config.add_view(RolesGrid, route_name='roles',
                    renderer='/roles/index.mako',
                    permission='roles.list')

    settings = config.get_settings()
    perms = settings.get('edbob.permissions')
    if perms:
        RoleCrud.permissions = perms

    config.add_route('role.create', '/roles/new')
    config.add_view(RoleCrud, attr='create', route_name='role.create',
                    renderer='/roles/crud.mako',
                    permission='roles.create')

    config.add_route('role.read', '/roles/{uuid}')
    config.add_view(RoleCrud, attr='read', route_name='role.read',
                    renderer='/roles/crud.mako',
                    permission='roles.read')

    config.add_route('role.update', '/roles/{uuid}/edit')
    config.add_view(RoleCrud, attr='update', route_name='role.update',
                    renderer='/roles/crud.mako',
                    permission='roles.update')

    config.add_route('role.delete', '/roles/{uuid}/delete')
    config.add_view(RoleCrud, attr='delete', route_name='role.delete',
                    permission='roles.delete')

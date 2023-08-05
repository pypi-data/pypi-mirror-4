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

import transaction
from pyramid.httpexceptions import HTTPFound

from formalchemy import Field, FieldRenderer
from webhelpers.html import literal
from webhelpers.html.tags import checkbox, hidden

import edbob
from edbob.db.auth import administrator_role, has_permission
from edbob.pyramid import filters
from edbob.pyramid import forms
from edbob.pyramid import grids
from edbob.pyramid import Session


def filter_map():
    return filters.get_filter_map(
        edbob.Role,
        ilike=['name'])

def search_config(request, fmap):
    return filters.get_search_config(
        'roles.list', request, fmap,
        include_filter_name=True,
        filter_type_name='lk')

def search_form(config):
    return filters.get_search_form(config)

def grid_config(request, search, fmap):
    return grids.get_grid_config(
        'roles.list', request, search,
        filter_map=fmap, sort='name')

def sort_map():
    return grids.get_sort_map(edbob.Role, ['name'])

def query(config):
    smap = sort_map()
    q = Session.query(edbob.Role)
    q = filters.filter_query(q, config)
    q = grids.sort_query(q, config, smap)
    return q


def roles(request):

    fmap = filter_map()
    config = search_config(request, fmap)
    search = search_form(config)
    config = grid_config(request, search, fmap)
    roles = grids.get_pager(query, config)

    g = forms.AlchemyGrid(
        edbob.Role, roles, config,
        gridurl=request.route_url('roles.list'),
        objurl='role.edit')

    g.configure(
        include=[
            g.name,
            ],
        readonly=True)

    grid = g.render(class_='clickable roles')
    return grids.render_grid(request, grid, search)


class PermissionsField(Field):

    def sync(self):
        if not self.is_readonly():
            role = self.model
            role.permissions = self.renderer.deserialize()


class PermissionsFieldRenderer(FieldRenderer):

    available_permissions = [

        ("Batches", [
                ('batches.list',        "List Batches"),
                ('batches.edit',        "Edit Batch"),
                ('batches.create',      "Create Batch"),
                ]),

        ("Roles", [
                ('roles.list',          "List Roles"),
                ('roles.edit',          "Edit Role"),
                ('roles.create',        "Create Role"),
                ]),
        ]

    def deserialize(self):
        perms = []
        i = len(self.name) + 1
        for key in self.params:
            if key.startswith(self.name):
                perms.append(key[i:])
        return perms

    def _render(self, readonly=False, **kwargs):
        # result = literal('')
        # for group_name, group_label, perm_list in self.field.model_value:
        #     rendered_group_name = literal('<p class="permission-group">' + group_label + '</p>\n')
        #     if readonly:
        #         result += literal('<tr><td colspan="2">') + rendered_group_name + literal('</td></tr>')
        #     else:
        #         result += rendered_group_name
        #         result += literal('<div>')
        #     for perm_name, perm_label, checked in perm_list:
        #         if readonly:
        #             result += literal('<tr>'
        #                               + '<td class="permission">' + ('[X]' if checked else '[&nbsp; ]') + '</td>'
        #                               + '<td class="permission-label">' + perm_label + '</td>'
        #                               + '</tr>\n')
        #         else:
        #             name = '.'.join((self.name, group_name, perm_name))
        #             result += check_box(name, label=perm_label, checked=checked)
        #     if not readonly:
        #         result += literal('</div>')
        # if readonly:
        #     return literal('<table class="permissions">') + result + literal('</table>')
        # return literal('<div class="permissions">') + result + literal('</div>')

        role = self.field.model
        if role is administrator_role(Session()):
            res = literal('<p>This is the administrative role; '
                          'it has full access to the entire system.</p>')
            if not readonly:
                res += hidden(self.name, value='') # ugly hack..or good idea?
        else:
            res = ''
            for group, perms in self.available_permissions:
                res += literal('<p class="group">%s</p>' % group)
                for perm, title in perms:
                    if readonly:
                        res += literal('<p>%s</p>' % title)
                    else:
                        checked = has_permission(role, perm)
                        res += checkbox(self.name + '-' + perm,
                                        checked=checked, label=title)
        return res

    def render(self, **kwargs):
        return self._render(**kwargs)

    def render_readonly(self, **kwargs):
        return self._render(readonly=True, **kwargs)


def role_fieldset(role, request):
    fs = forms.make_fieldset(role, url=request.route_url,
                             url_action=request.current_route_url(),
                             route_name='roles.list')
    
    fs.append(PermissionsField('permissions',
                               renderer=PermissionsFieldRenderer))

    fs.configure(
        include=[
            fs.name,
            fs.permissions,
            ])

    if not fs.edit:
        del fs.permissions

    return fs


def new_role(request):

    fs = role_fieldset(edbob.Role, request)
    if request.POST:
        fs.rebind(data=request.params)
        if fs.validate():

            with transaction.manager:
                fs.sync()
                fs.model = Session.merge(fs.model)
                request.session.flash("%s \"%s\" has been %s." % (
                        fs.crud_title, fs.get_display_text(),
                        'updated' if fs.edit else 'created'))
                home = request.route_url('roles.list')

            return HTTPFound(location=home)

    return {'fieldset': fs, 'crud': True}


def edit_role(request):
    uuid = request.matchdict['uuid']
    role = Session.query(edbob.Role).get(uuid) if uuid else None
    assert role

    fs = role_fieldset(role, request)
    if request.POST:
        fs.rebind(data=request.params)
        if fs.validate():

            with transaction.manager:
                Session.add(fs.model)
                fs.sync()
                request.session.flash("%s \"%s\" has been %s." % (
                        fs.crud_title, fs.get_display_text(),
                        'updated' if fs.edit else 'created'))
                home = request.route_url('roles.list')

            return HTTPFound(location=home)

    return {'fieldset': fs, 'crud': True}


def includeme(config):

    config.add_route('roles.list', '/roles')
    config.add_view(roles, route_name='roles.list', renderer='/roles/index.mako',
                    permission='roles.list', http_cache=0)

    config.add_route('role.new', '/roles/new')
    config.add_view(new_role, route_name='role.new', renderer='/roles/role.mako',
                    permission='roles.create', http_cache=0)

    config.add_route('role.edit', '/roles/{uuid}/edit')
    config.add_view(edit_role, route_name='role.edit', renderer='/roles/role.mako',
                    permission='roles.edit', http_cache=0)

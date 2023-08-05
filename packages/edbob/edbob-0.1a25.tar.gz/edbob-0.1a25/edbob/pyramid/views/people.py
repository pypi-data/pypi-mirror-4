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
``edbob.pyramid.views.people`` -- Person Views
"""

from sqlalchemy import and_

# import transaction
# from pyramid.httpexceptions import HTTPFound

# from formalchemy import Field

import edbob
# from edbob.pyramid import filters
# from edbob.pyramid import forms
# from edbob.pyramid import grids
# from edbob.pyramid import Session
from edbob.pyramid.views import SearchableAlchemyGridView, CrudView


class PeopleGrid(SearchableAlchemyGridView):

    mapped_class = edbob.Person
    config_prefix = 'people'
    sort = 'first_name'

    def join_map(self):
        return {
            'email':
                lambda q: q.outerjoin(edbob.PersonEmailAddress, and_(
                    edbob.PersonEmailAddress.parent_uuid == edbob.Person.uuid,
                    edbob.PersonEmailAddress.preference == 1)),
            'phone':
                lambda q: q.outerjoin(edbob.PersonPhoneNumber, and_(
                    edbob.PersonPhoneNumber.parent_uuid == edbob.Person.uuid,
                    edbob.PersonPhoneNumber.preference == 1)),
            }

    def filter_map(self):
        return self.make_filter_map(
            ilike=['first_name', 'last_name'],
            email=self.filter_ilike(edbob.PersonEmailAddress.address),
            phone=self.filter_ilike(edbob.PersonPhoneNumber.number))

    def filter_config(self):
        return self.make_filter_config(
            include_filter_first_name=True,
            filter_type_first_name='lk',
            include_filter_last_name=True,
            filter_type_last_name='lk',
            filter_label_phone="Phone Number",
            filter_label_email="Email Address")

    def sort_map(self):
        return self.make_sort_map(
            'first_name', 'last_name',
            email=self.sorter(edbob.PersonEmailAddress.address),
            phone=self.sorter(edbob.PersonPhoneNumber.number))

    def grid(self):
        g = self.make_grid()
        g.configure(
            include=[
                g.first_name,
                g.last_name,
                g.phone.label("Phone Number"),
                g.email.label("Email Address"),
                ],
            readonly=True)
        g.clickable = True
        g.click_route_name = 'person.read'
        return g


class PersonCrud(CrudView):

    mapped_class = edbob.Person
    home_route = 'people'

    def fieldset(self, model):
        fs = self.make_fieldset(model)
        fs.configure(
            include=[
                fs.first_name,
                fs.last_name,
                fs.phone.label("Phone Number"),
                fs.email.label("Email Address"),
                ])
        return fs


# def filter_map():
#     return filters.get_filter_map(
#         edbob.Person,
#         ilike=['first_name', 'last_name', 'display_name'])

# def search_config(request, fmap):
#     return filters.get_search_config(
#         'people.list', request, fmap,
#         include_filter_display_name=True,
#         filter_type_display_name='lk')

# def search_form(config):
#     return filters.get_search_form(config)

# def grid_config(request, search, fmap):
#     return grids.get_grid_config(
#         'people.list', request, search,
#         filter_map=fmap, sort='display_name')

# def sort_map():
#     return grids.get_sort_map(
#         edbob.Person,
#         ['first_name', 'last_name', 'display_name'])

# def query(config):
#     smap = sort_map()
#     q = Session.query(edbob.Person)
#     q = filters.filter_query(q, config)
#     q = grids.sort_query(q, config, smap)
#     return q


# def people(context, request):

#     fmap = filter_map()
#     config = search_config(request, fmap)
#     search = search_form(config)
#     config = grid_config(request, search, fmap)
#     people = grids.get_pager(query, config)

#     g = forms.AlchemyGrid(
#         edbob.Person, people, config,
#         gridurl=request.route_url('people.list'),
#         objurl='person.edit')

#     g.configure(
#         include=[
#             g.first_name,
#             g.last_name,
#             g.display_name,
#             ],
#         readonly=True)

#     grid = g.render(class_='clickable people')
#     return grids.render_grid(request, grid, search)


# def person_fieldset(person, request):
#     fs = forms.make_fieldset(person, url=request.route_url,
#                              url_action=request.current_route_url(),
#                              route_name='people.list')
#     fs.configure(
#         include=[
#             fs.first_name,
#             fs.last_name,
#             fs.display_name,
#             ])
#     return fs


# def new_person(context, request):

#     fs = person_fieldset(edbob.Person, request)
#     if not fs.readonly and request.POST:
#         fs.rebind(data=request.params)
#         if fs.validate():

#             with transaction.manager:
#                 fs.sync()
#                 Session.add(fs.model)
#                 Session.flush()
#                 request.session.flash("%s \"%s\" has been %s." % (
#                         fs.crud_title, fs.get_display_text(),
#                         'updated' if fs.edit else 'created'))

#             return HTTPFound(location=request.route_url('people.list'))

#     return {'fieldset': fs, 'crud': True}


# def edit_person(request):
#     """
#     View for editing a :class:`edbob.Person` instance.
#     """

#     from edbob.pyramid.views.users import user_fieldset

#     uuid = request.matchdict['uuid']
#     person = Session.query(edbob.Person).get(uuid) if uuid else None
#     assert person

#     fs = person_fieldset(person, request)
#     if request.POST:
#         fs.rebind(data=request.params)
#         if fs.validate():

#             with transaction.manager:
#                 fs.sync()
#                 fs.model = Session.merge(fs.model)
#                 request.session.flash("%s \"%s\" has been %s." % (
#                         fs.crud_title, fs.get_display_text(),
#                         'updated' if fs.edit else 'created'))
#                 home = request.route_url('people.list')

#             return HTTPFound(location=home)

#     user = fs.model.user
#     if user:
#         user = user_fieldset(user, request)
#         user.readonly = True
#         del user.person
#         del user.password
#         del user.confirm_password

#     return {'fieldset': fs, 'crud': True, 'user': user}


def includeme(config):

    config.add_route('people', '/people')
    config.add_view(PeopleGrid, route_name='people',
                    renderer='/people/index.mako',
                    permission='people.list')

#     config.add_route('people.list', '/people')
#     config.add_view(people, route_name='people.list', renderer='/people/index.mako',
#                     permission='people.list', http_cache=0)

    config.add_route('person.read', '/people/{uuid}')
    config.add_view(PersonCrud, attr='read', route_name='person.read',
                    renderer='/people/crud.mako',
                    permission='people.read')

#     config.add_route('person.new', '/people/new')
#     config.add_view(new_person, route_name='person.new', renderer='/people/person.mako',
#                     permission='people.create', http_cache=0)

#     config.add_route('person.edit', '/people/{uuid}/edit')
#     config.add_view(edit_person, route_name='person.edit', renderer='/people/person.mako',
#                     permission='people.edit', http_cache=0)

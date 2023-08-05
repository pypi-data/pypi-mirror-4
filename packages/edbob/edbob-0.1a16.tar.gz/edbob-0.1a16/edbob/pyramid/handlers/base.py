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
``edbob.pyramid.handlers.base`` -- Base Handlers
"""

from pyramid.renderers import render_to_response
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPOk, HTTPUnauthorized

# import sqlahelper

# # import rattail.pyramid.forms.util as util
# from rattail.db.perms import has_permission
# from rattail.pyramid.forms.formalchemy import Grid


class needs_perm(object):
    """
    Decorator to be used for handler methods which should restrict access based
    on the current user's permissions.
    """

    def __init__(self, permission, **kwargs):
        self.permission = permission
        self.kwargs = kwargs

    def __call__(self, fn):
        permission = self.permission
        kw = self.kwargs
        def wrapped(self):
            if not self.request.current_user:
                self.request.session['referrer'] = self.request.url_generator.current()
                self.request.session.flash("You must be logged in to do that.", 'error')
                return HTTPFound(location=self.request.route_url('login'))
            if not has_permission(self.request.current_user, permission):
                self.request.session.flash("You do not have permission to do that.", 'error')
                home = kw.get('redirect', self.request.route_url('home'))
                return HTTPFound(location=home)
            return fn(self)
        return wrapped


def needs_user(fn):
    """
    Decorator for handler methods which require simply that a user be currently
    logged in.
    """

    def wrapped(self):
        if not self.request.current_user:
            self.request.session['referrer'] = self.request.url_generator.current()
            self.request.session.flash("You must be logged in to do that.", 'error')
            return HTTPFound(location=self.request.route_url('login'))
        return fn(self)
    return wrapped


class Handler(object):

    def __init__(self, request):
        self.request = request
        self.Session = sqlahelper.get_session()

    # def json_response(self, data={}):
    #     response = render_to_response('json', data, request=self.request)
    #     response.headers['Content-Type'] = 'application/json'
    #     return response


class CrudHandler(Handler):
    # """
    # This handler provides all the goodies typically associated with general
    # CRUD functionality, e.g. search filters and grids.
    # """

    def crud(self, cls, fieldset_factory, home=None, delete=None, post_sync=None, pre_render=None):
        """
        Adds a common CRUD mechanism for objects.

        ``cls`` should be a SQLAlchemy-mapped class, presumably deriving from
        :class:`rattail.Object`.

        ``fieldset_factory`` must be a callable which accepts the fieldset's
        "model" as its only positional argument.

        ``home`` will be used as the redirect location once a form is fully
        validated and data saved.  If you do not speficy this parameter, the
        user will be redirected to be the CRUD page for the new object (e.g. so
        an object may be created before certain properties may be edited).

        ``delete`` may either be a string containing a URL to which the user
        should be redirected after the object has been deleted, or else a
        callback which will be executed *instead of* the normal algorithm
        (which is merely to delete the object via the Session).

        ``post_sync`` may be a callback which will be executed immediately
        after ``FieldSet.sync()`` is called, i.e. after validation as well.

        ``pre_render`` may be a callback which will be executed after any POST
        processing has occured, but just before rendering.
        """

        uuid = self.request.params.get('uuid')
        obj = self.Session.query(cls).get(uuid) if uuid else cls
        assert obj

        if self.request.params.get('delete'):
            if delete:
                if isinstance(delete, basestring):
                    self.Session.delete(obj)
                    return HTTPFound(location=delete)
                res = delete(obj)
                if res:
                    return res
            else:
                self.Session.delete(obj)
                if not home:
                    raise ValueError("Must specify 'home' or 'delete' url "
                                     "in call to CrudHandler.crud()")
                return HTTPFound(location=home)

        fs = fieldset_factory(obj)

        # if not fs.readonly and self.request.params.get('fieldset'):
        #     fs.rebind(data=self.request.params)
        #     if fs.validate():
        #         fs.sync()
        #         if post_sync:
        #             res = post_sync(fs)
        #             if isinstance(res, HTTPFound):
        #                 return res
        #         if self.request.params.get('partial'):
        #             self.Session.flush()
        #             return self.json_success(uuid=fs.model.uuid)
        #         return HTTPFound(location=self.request.route_url(objects, action='index'))

        if not fs.readonly and self.request.POST:
            # print self.request.POST
            fs.rebind(data=self.request.params)
            if fs.validate():
                fs.sync()
                if post_sync:
                    res = post_sync(fs)
                    if res:
                        return res
                if self.request.params.get('partial'):
                    self.Session.flush()
                    return self.json_success(uuid=fs.model.uuid)

                if not home:
                    self.Session.flush()
                    home = self.request.url_generator.current() + '?uuid=' + fs.model.uuid
                    self.request.session.flash("%s \"%s\" has been %s." % (
                            fs.crud_title, fs.get_display_text(),
                            'updated' if fs.edit else 'created'))
                return HTTPFound(location=home)

        data = {'fieldset': fs, 'crud': True}

        if pre_render:
            res = pre_render(fs)
            if res:
                if isinstance(res, HTTPException):
                    return res
                data.update(res)

        # data = {'fieldset':fs}
        # if self.request.params.get('partial'):
        #     return render_to_response('/%s/crud_partial.mako' % objects,
        #                               data, request=self.request)
        # return data

        return data

    def grid(self, *args, **kwargs):
        """
        Convenience function which returns a grid.  The only functionality this
        method adds is the ``session`` parameter.
        """

        return Grid(session=self.Session(), *args, **kwargs)

    # def get_grid(self, name, grid, query, search=None, url=None, **defaults):
    #     """
    #     Convenience function for obtaining the configuration for a grid,
    #     and then obtaining the grid itself.

    #     ``name`` is essentially the config key, e.g. ``'products.lookup'``, and
    #     in fact is expected to take that precise form (where the first part is
    #     considered the handler name and the second part the action name).

    #     ``grid`` must be a callable with a signature of ``grid(query,
    #     config)``, and ``query`` will be passed directly to the ``grid``
    #     callable.  ``search`` will be used to inform the grid of the search in
    #     effect, if any. ``defaults`` will be used to customize the grid config.
    #     """

    #     if not url:
    #         handler, action = name.split('.')
    #         url = self.request.route_url(handler, action=action)
    #     config = util.get_grid_config(name, self.request, search,
    #                                   url=url, **defaults)
    #     return grid(query, config)

    # def get_search_form(self, name, labels={}, **defaults):
    #     """
    #     Convenience function for obtaining the configuration for a search form,
    #     and then obtaining the form itself.

    #     ``name`` is essentially the config key, e.g. ``'products.lookup'``.
    #     The ``labels`` dictionary can be used to override the default labels
    #     displayed for the various search fields.  The ``defaults`` dictionary
    #     is used to customize the search config.
    #     """

    #     config = util.get_search_config(name, self.request,
    #                                     self.filter_map(), **defaults)
    #     form = util.get_search_form(config, **labels)
    #     return form

    # def object_crud(self, cls, objects=None, post_sync=None):
    #     """
    #     This method is a desperate attempt to encapsulate shared CRUD logic
    #     which is useful across all editable data objects.

    #     ``objects``, if provided, should be the plural name for the class as
    #     used in internal naming, e.g. ``'products'``.  A default will be used
    #     if you do not provide this value.

    #     ``post_sync``, if provided, should be a callable which accepts a
    #     ``formalchemy.Fieldset`` instance as its only argument.  It will be
    #     called immediately after the fieldset is synced.
    #     """

    #     if not objects:
    #         objects = cls.__name__.lower() + 's'

    #     uuid = self.request.params.get('uuid')
    #     obj = self.Session.query(cls).get(uuid) if uuid else cls
    #     assert obj

    #     fs = self.fieldset(obj)

    #     if not fs.readonly and self.request.params.get('fieldset'):
    #         fs.rebind(data=self.request.params)
    #         if fs.validate():
    #             fs.sync()
    #             if post_sync:
    #                 res = post_sync(fs)
    #                 if isinstance(res, HTTPFound):
    #                     return res
    #             if self.request.params.get('partial'):
    #                 self.Session.flush()
    #                 return self.json_success(uuid=fs.model.uuid)
    #             return HTTPFound(location=self.request.route_url(objects, action='index'))

    #     data = {'fieldset':fs}
    #     if self.request.params.get('partial'):
    #         return render_to_response('/%s/crud_partial.mako' % objects,
    #                                   data, request=self.request)
    #     return data

    # def render_grid(self, grid, search=None, **kwargs):
    #     """
    #     Convenience function to render a standard grid.  Really just calls
    #     :func:`dtail.forms.util.render_grid()`.
    #     """

    #     return util.render_grid(self.request, grid, search, **kwargs)

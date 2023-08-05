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
``edbob.db.extensions`` -- Database Extensions
"""

import logging
# from pkg_resources import iter_entry_points

import sqlalchemy.exc
from sqlalchemy import MetaData
# from sqlalchemy.orm import clear_mappers

# import migrate.versioning.api
# from migrate.versioning.schema import ControlledSchema

# import rattail
# from rattail.db import exc as exceptions
# from rattail.db import Session
# from rattail.db.classes import ActiveExtension
# from rattail.db.mappers import make_mappers
# from rattail.db.model import get_metadata
# from rattail.db.util import get_repository_path, get_repository_version

import edbob
import edbob.db
from edbob.db import exceptions
from edbob.db import Session
# from edbob.db.classes import ActiveExtension
from edbob.db.model import Base, ActiveExtension
# from edbob.db.util import (
#     get_database_version,
#     get_repository_path,
#     get_repository_version,
#     )
from edbob.modules import import_module_path
from edbob.util import entry_point_map, requires_impl


log = logging.getLogger(__name__)


class Extension(edbob.Object):
    """
    Base class for schema/ORM extensions.
    """

    # Set this to a list of strings (extension names) as needed within your
    # derived class.
    required_extensions = []

    # You can set this to any dotted module path you like.  If unset a default
    # will be assumed, of the form ``<path.to.extension>.model`` (see
    # :meth:`Extension.get_models_module()` for more info).
    model_module = ''

    # You can set this to any dotted module path you like.  If unset a default
    # will be assumed, of the form ``<path.to.extension>.enum`` (see
    # :meth:`Extension.get_enum_module()` for more info).
    enum_module = ''

    # @property
    # @requires_impl(is_property=True)
    # def name(self):
    #     """
    #     The name of the extension.
    #     """
    #     pass

    # @property
    # @requires_impl(is_property=True)
    # def schema(self):
    #     """
    #     Should return a reference to the extension's ``schema`` module, which
    #     is assumed to be a SQLAlchemy-Migrate repository.
    #     """
    #     pass

    # def add_class(self, cls):
    #     """
    #     Convenience method for use in :meth:`extend_classes()`.
    #     """

    #     from edbob.db import classes

    #     name = cls.__name__
    #     edbob.graft(classes, {name:cls}, name)

    # def extend_classes(self):
    #     """
    #     Any extra classes provided by the extension should be added to the ORM
    #     whenever this method is called.

    #     Note that the :meth:`add_class()` convenience method is designed to be
    #     used when adding classes.
    #     """
    #     pass

    def extend_framework(self):
        """
        Extends the framework...
        """

        edbob.graft(edbob, self.get_model_module())
        enum = self.get_enum_module()
        if enum:
            edbob.graft(edbob, enum)

    # def extend_mappers(self, metadata):
    #     """
    #     All SQLAlchemy mapping to be done by the extension should be done
    #     within this method.

    #     Any extra classes the extension provides will typically be mapped here.
    #     Any manipulation the extension needs to perform on the ``edbob`` core
    #     ORM should be done here as well.
    #     """
    #     pass

    def get_metadata(self, recurse=False):
        """
        Returns a :class:`sqlalchemy.MetaData` instance containing the schema
        definition for the extension.

        If ``recurse`` evaluates to true, then tables from any extensions upon
        which this one relies will be included as well.
        """

        meta = MetaData()
        self.populate_metadata(meta, recurse)
        return meta

    def get_enum_module(self):
        """
        Imports and returns a reference to the Python module providing
        enumeration data for the extension (if one exists).

        :attr:`Extension.enum_module` is first consulted to determine the
        dotted module path.  If nothing is found there, a default path is
        constructed by appending ``'.enum'`` to the extension module's own
        dotted path.
        """

        if self.enum_module:
            module = self.enum_module
        else:
            module = str(self.__class__.__module__) + '.enum'
        try:
            return import_module_path(module)
        except ImportError:
            return None

    def get_model_module(self):
        """
        Imports and returns a reference to the Python module providing schema
        definition for the extension.

        :attr:`Extension.model_module` is first consulted to determine the
        dotted module path.  If nothing is found there, a default path is
        constructed by appending ``'.model'`` to the extension module's own
        dotted path.
        """

        if self.model_module:
            module = self.model_module
        else:
            module = str(self.__class__.__module__) + '.model'
        return import_module_path(module)

    def populate_metadata(self, metadata, recurse=False):
        """
        Populates ``metadata`` with tables provided by the extension.

        If ``recurse`` evaluates to true, then tables for any extension upon
        which this one relies will also be included.
        """

        if recurse:
            for name in self.required_extensions:
                ext = get_extension(name)
                ext.populate_metadata(metadata, True)

        model = self.get_model_module()
        for name in model.__all__:
            obj = getattr(model, name)
            if isinstance(obj, type) and issubclass(obj, model.Base):
                if obj.__tablename__ not in metadata.tables:
                    obj.__table__.tometadata(metadata)

    # def remove_class(self, name):
    #     """
    #     Convenience method for use in :meth:`restore_classes()`.
    #     """

    #     from edbob.db import classes

    #     if name in classes.__all__:
    #         classes.__all__.remove(name)
    #     if hasattr(classes, name):
    #         del classes.__dict__[name]

    # def restore_classes(self):
    #     """
    #     This method should remove any extra classes which were added within
    #     :meth:`extend_classes()`.  Note that there is a :meth:`remove_class()`
    #     method for convenience in doing so.
    #     """
    #     pass


def activate_extension(extension, engine=None):
    """
    Activates the :class:`Extension` instance represented by ``extension``
    (which can be the actual instance, or the extension's name) by installing
    its schema and registering it within the database, and immediately applies
    it to the current ORM/API.

    If ``engine`` is not provided, then :attr:`edbob.db.engine` is assumed.
    """

    if engine is None:
        engine = edbob.db.engine

    if not isinstance(extension, Extension):
        extension = get_extension(extension)

    # Skip all this if already active.
    if extension_active(extension, engine):
        return

    log.debug("Activating extension: %s" % extension.name)

    # Activate all required extensions first.
    for name in extension.required_extensions:
        activate_extension(name, engine)

    # Install schema for this extension.
    install_extension_schema(extension, engine)

    # Add ActiveExtension record for this extension.
    session = Session(bind=engine)
    if not session.query(ActiveExtension).get(extension.name):
        session.add(ActiveExtension(name=extension.name))
        session.commit()
    session.close()

    # merge_extension_metadata(extension)
    # extension.extend_classes()
    # extension.extend_mappers(Base.metadata)
    extension.extend_framework()

    # Add extension to in-memory active extensions tracker.
    active_extensions(engine).append(extension.name)


_available_extensions = None
def available_extensions():
    """
    Returns the map of available :class:`Extension` classes, as determined by
    ``'edbob.db.extensions'`` entry points..
    """

    global _available_extensions

    if _available_extensions is None:
        _available_extensions = entry_point_map('edbob.db.extensions')
    return _available_extensions


def deactivate_extension(extension, engine=None):
    """
    Uninstalls an extension's schema from a database.

    If ``engine`` is not provided, :attr:`edbob.db.engine` is assumed.
    """

    if engine is None:
        engine = edbob.db.engine

    if not isinstance(extension, Extension):
        extension = get_extension(extension)

    log.debug("Deactivating extension: %s" % extension.name)
    active = active_extensions(engine)
    if extension.name in active:
        active.remove(extension.name)

    session = Session(bind=engine)
    ext = session.query(ActiveExtension).get(extension.name)
    if ext:
        session.delete(ext)
        session.commit()
    session.close()

    uninstall_extension_schema(extension, engine)
    # unmerge_extension_metadata(extension)
    # extension.restore_classes()

    # clear_mappers()
    # make_mappers(rattail.metadata)
    # for name in sorted(_active_extensions, extension_sorter(_active_extensions)):
    #     _active_extensions[name].extend_mappers(rattail.metadata)


def extend_framework():
    """
    Attempts to connect to the primary database and, if successful, inspects it
    to determine which extensions are active within it.  Any such extensions
    found will be used to extend the ORM/API in-place.
    """

    # Do we even have an engine?
    engine = edbob.db.engine
    if not engine:
        return

    # Check primary database connection.
    try:
        engine.connect()
    except sqlalchemy.exc.OperationalError:
        return

    # # Check database version to see if core schema is installed.
    # try:
    #     db_version = get_database_version(engine)
    # except exceptions.CoreSchemaNotInstalled:
    #     return

    # Since extensions may depend on one another, we must first retrieve the
    # list of active extensions' names from the database and *then* sort them
    # according to their stated dependencies.  (This information is only known
    # after instantiating the extensions.)

    session = Session()
    try:
        active = session.query(ActiveExtension).all()
    except sqlalchemy.exc.ProgrammingError:
        session.close()
        return

    extensions = {}
    for ext in active:
        extensions[ext.name] = get_extension(ext.name)
    session.close()

    for name in sorted(extensions, extension_sorter(extensions)):
        log.info("Applying active extension: %s" % name)
        ext = extensions[name]
        # merge_extension_metadata(ext)
        # ext.extend_classes()
        # ext.extend_mappers(rattail.metadata)
        ext.extend_framework()
        _active_extensions[name] = ext


def extension_active(extension, engine=None):
    """
    Returns boolean indicating whether or not the given ``extension`` is active
    within a database.

    If ``engine`` is not provided, :attr:`edbob.db.engine` is assumed.
    """

    if not engine:
        engine = edbob.db.engine

    if not isinstance(extension, Extension):
        extension = get_extension(extension)
    return extension.name in active_extensions(engine)


def extension_sorter(extensions):
    """
    Returns a function to be used for sorting extensions according to their
    inter-dependencies.  ``extensions`` should be a dictionary containing the
    extensions which are to be sorted.
    """

    def sorter(name_x, name_y):
        ext_x = extensions[name_x]
        ext_y = extensions[name_y]

        if name_y in ext_x.required_extensions:
            return 1
        if name_x in ext_y.required_extensions:
            return -1

        if ext_x.required_extensions and not ext_y.required_extensions:
            return 1
        if ext_y.required_extensions and not ext_x.required_extensions:
            return -1
        return 0

    return sorter        


def get_extension(name):
    """
    Returns a :class:`Extension` instance, according to ``name``.  An error is
    raised if the extension cannot be found.
    """

    extensions = available_extensions()
    if name in extensions:
        return extensions[name]()
    raise exceptions.ExtensionNotFound(name)


def install_extension_schema(extension, engine=None):
    """
    Installs an extension's schema to the database and adds version control for
    it.  ``extension`` must be a valid :class:`Extension` instance.

    If ``engine`` is not provided, :attr:`edbob.db.engine` is assumed.
    """

    if engine is None:
        engine = edbob.db.engine

    # # Extensions aren't required to provide metadata...
    # ext_meta = extension.get_metadata()
    # if not ext_meta:
    #     return

    # # ...but if they do they must also provide a SQLAlchemy-Migrate repository.
    # assert extension.schema, "Extension does not implement 'schema': %s" % extension.name
        
    # meta = edbob.db.metadata
    # for table in meta.sorted_tables:
    #     table.tometadata(ext_meta)
    # for table in ext_meta.sorted_tables:
    #     if table.name not in meta.tables:
    #         table.create(bind=engine, checkfirst=True)

    # TODO: This sucks, please fix.
    # edbob.db.Base.metadata.create_all(engine)

    # meta = MetaData(engine)
    # for tables in (edbob.db.iter_tables(), extension.iter_tables()):
    #     for table in tables:
    #         table.tometadata(meta)
    # meta.create_all()

    core_meta = edbob.db.get_core_metadata()
    ext_meta = extension.get_metadata(recurse=True)
    for table in ext_meta.sorted_tables:
        table.tometadata(core_meta)
    core_meta.create_all(engine)

    # migrate.versioning.api.version_control(
    #     str(engine.url), get_repository_path(extension), get_repository_version(extension))


def merge_extension_metadata(ext):
    """
    Merges an extension's metadata with the global ``edbob.db.metadata``
    instance.

    .. note::
       ``edbob`` uses this internally; you should not need to.
    """

    ext_meta = ext.get_metadata()
    if not ext_meta:
        return
    meta = Base.metadata
    for table in meta.sorted_tables:
        table.tometadata(ext_meta)
    for table in ext_meta.sorted_tables:
        if table.name not in meta.tables:
            table.tometadata(meta)


def uninstall_extension_schema(extension, engine=None):
    """
    Uninstalls an extension's tables from the database represented by
    ``engine`` (or :attr:`edbob.db.engine` if none is provided), and removes
    SQLAlchemy-Migrate version control for the extension.
    """

    if engine is None:
        engine = edbob.db.engine
    
    # ext_meta = extension.get_metadata()
    # if not ext_meta:
    #     return
    
    # schema = ControlledSchema(engine, get_repository_path(extension))
    # engine.execute(schema.table.delete().where(
    #         schema.table.c.repository_id == schema.repository.id))

    # meta = get_metadata()
    # for table in meta.sorted_tables:
    #     table.tometadata(ext_meta)
    # for table in reversed(ext_meta.sorted_tables):
    #     if table.name not in meta.tables:
    #         table.drop(bind=engine)

    # core_meta = edbob.db.get_core_metadata()
    # ext_meta = extension.get_metadata()
    # for table in ext_meta.sorted_tables:
    #     table.tometadata(core_meta)
    # core_meta.create_all(engine)

    # core_meta = edbob.db.get_core_metadata()
    # ext_meta = extension.get_metadata()
    # for table in ext_meta.sorted_tables:
    #     table.tometadata(core_meta)
    # for table in reversed(core_meta.sorted_tables):
    #     if table in ext_meta:
    #         table.drop(engine)

    core_meta = edbob.db.get_core_metadata()
    ext_fullmeta = extension.get_metadata(True)
    for table in ext_fullmeta.sorted_tables:
        table.tometadata(core_meta)
    ext_meta = extension.get_metadata()
    for table in reversed(core_meta.sorted_tables):
        if table in ext_meta:
            table.drop(engine)


# def unmerge_extension_metadata(extension):
#     """
#     Removes an extension's metadata from the global ``rattail.metadata``
#     instance.
#     """

#     ext_meta = extension.get_metadata()
#     if not ext_meta:
#         return

#     meta = rattail.metadata
#     ext_tables = ext_meta.tables.keys()
#     for table in reversed(meta.sorted_tables):
#         if table.name in ext_tables:
#             meta.remove(table)


# # def merge_extension_permissions(extension):
# #     '''
# #     Helper function to merge an extension's permission definitions with those of
# #     the framework.  (This should only be called by the framework itself.)
# #     '''
# #     from rattail.v1.perms import permissions
# #     log.debug('Merging permissions from extension: %s' % extension.name)
# #     for group_name in extension.permissions:
# #         if group_name not in permissions:
# #             permissions[group_name] = extension.permissions[group_name]
# #         elif extension.permissions[group_name][0] != permissions[group_name][0]:
# #             log.warning("Extension '%s' tries to override UUID of permission group '%s' (but is denied)" % (
# #                     extension.name, group_name))
# #         else:
# #             # Extensions may override permission group display names.
# #             if extension.permissions[group_name][1]:
# #                 permissions[group_name][1] = extension.permissions[group_name][1]
# #             perms = permissions[group_name][2]
# #             ext_perms = extension.permissions[group_name][2]
# #             for perm_name in ext_perms:
# #                 if perm_name not in perms:
# #                     perms[perm_name] = ext_perms[perm_name]
# #                 elif ext_perms[perm_name][0] != perms[perm_name][0]:
# #                     log.warning("Extension '%s' tries to override UUID of permission '%s' (but is denied)" % (
# #                             extension.name, '.'.join((group_name, perm_name))))
# #                 else:
# #                     # Extensions may override permission display names.
# #                     if ext_perms[perm_name][1]:
# #                         perms[perm_name][1] = ext_perms[perm_name][1]


_active_extensions = {}
def active_extensions(engine=None):
    """
    Returns a list of names for extensions which are active within a database.

    If ``engine`` is not provided, ``edbob.db.engine`` is assumed.
    """

    if not engine:
        engine = edbob.db.engine

    exts = _active_extensions.get(engine.url)
    if exts:
        return exts

    session = Session()
    q = session.query(ActiveExtension.name)
    exts = [x[0] for x in q]
    session.close()

    _active_extensions[engine.url] = exts
    return exts

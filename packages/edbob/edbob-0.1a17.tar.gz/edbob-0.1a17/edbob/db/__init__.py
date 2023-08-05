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
``edbob.db`` -- Database Framework
"""

from __future__ import absolute_import

from sqlalchemy import engine_from_config, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import edbob


__all__ = ['engines', 'engine', 'Session', 'get_setting', 'save_setting']

engines = None
engine = None
Session = sessionmaker()
Base = declarative_base(cls=edbob.Object)


def init(config):
    """
    Initializes the database connection(s); called by :func:`edbob.init()` if
    config includes something like::

       .. highlight:: ini

       [edbob]
       init = ['edbob.db']

       [edbob.db]
       sqlalchemy.urls = {
               'default':       'postgresql://user:pass@localhost/edbob,
               }

    This function reads connection info from ``config`` and builds a dictionary
    or :class:`sqlalchemy.Engine` instances accordingly.  It also extends the
    root ``edbob`` namespace with the ORM classes (:class:`edbob.Person`,
    :class:`edbob.User`, etc.), as well as a few other things
    (e.g. :attr:`edbob.engine`, :attr:`edbob.Session`, :attr:`edbob.metadata`).
    """

    import edbob.db
    from edbob.db import model
    from edbob.db import enum
    from edbob.db.extensions import extend_framework

    global engines, engine

    keys = config.get('edbob.db', 'keys')
    if keys:
        keys = keys.split(',')
    else:
        keys = ['default']

    engines = {}
    cfg = config.get_dict('edbob.db')
    for key in keys:
        key = key.strip()
        try:
            engines[key] = engine_from_config(cfg, '%s.' % key)
        except KeyError:
            if key == 'default':
                try:
                    engines[key] = engine_from_config(cfg, 'sqlalchemy.')
                except KeyError:
                    pass

    engine = engines.get('default')
    if engine:
        Session.configure(bind=engine)
    
    extend_framework()

    edbob.graft(edbob, edbob.db)
    edbob.graft(edbob, model)
    edbob.graft(edbob, enum)


def get_setting(name, session=None):
    """
    Returns a setting from the database.
    """

    _session = session
    if not session:
        session = Session()
    setting = session.query(edbob.Setting).get(name)
    if setting:
        setting = setting.value
    if not _session:
        session.close()
    return setting


def save_setting(name, value, session=None):
    """
    Saves a setting to the database.
    """

    _session = session
    if not session:
        session = Session()
    setting = session.query(edbob.Setting).get(name)
    if not setting:
        setting = edbob.Setting(name=name)
        session.add(setting)
    setting.value = value
    if not _session:
        session.commit()
        session.close()


def get_core_metadata():
    """
    Returns a :class:`sqlalchemy.MetaData` instance containing only those
    :class:`sqlalchemy.Table`s which are part of the core ``edbob`` schema.
    """

    from edbob.db import model

    meta = MetaData()
    for name in model.__all__:
        if name != 'Base':
            obj = getattr(model, name)
            if isinstance(obj, type) and issubclass(obj, model.Base):
                obj.__table__.tometadata(meta)
    return meta


def needs_session(func):
    """
    Decorator which adds helpful session handling.
    """

    def wrapped(*args, **kwargs):
        session = kwargs.pop('session', None)
        _orig_session = session
        if not session:
            session = Session()
        res = func(session, *args, **kwargs)
        if not _orig_session:
            session.commit()
            session.close()
        return res

    return wrapped

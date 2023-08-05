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
``edbob.time`` -- Date & Time Utilities
"""

import datetime
import pytz
import logging
import warnings

import edbob


__all__ = ['utc_time', 'local_time']

timezones = {}

log = logging.getLogger(__name__)


def init(config):
    """
    Reads configuration to become aware of all timezones which may concern the
    application.

    .. highlight:: ini

    The bare minimum configuration required is the ``zone.local`` setting::

       [edbob.time]
       zone.local = US/Pacific

    Multiple timezones may be configured like so::

       [edbob.time]
       zone.local = America/Los_Angeles
       zone.head_office = America/New_York
       zone.that_other_place = Asia/Manila
       zone.some_app = US/Central

    See `Wikipedia
    <http://en.wikipedia.org/wiki/List_of_tz_database_time_zones>`_ for a
    (presumably) full list of valid timezone names.

    .. note::
       A ``zone.utc`` option is automatically created for you; there is no need
       to define it.
    """

    for key in config.options('edbob.time'):
        if key.startswith('zone.'):
            tz = config.get('edbob.time', key)
            if tz:
                key = key[5:]
                log.info("'%s' timezone set to '%s'" % (key, tz))
                set_timezone(tz, key)

    if 'local' not in timezones:
        tz = config.get('edbob.time', 'timezone')
        if tz:
            warnings.warn("Config option 'timezone' in 'edbob.time' section is deprecated.  "
                          "Please set 'zone.local' instead.",
                          DeprecationWarning)
            set_timezone(tz)
        else:
            log.warning("'local' timezone not configured; falling back to 'America/Chicago'")
            set_timezone('America/Chicago')

    set_timezone('UTC', 'utc')


def get_timezone(key='local'):
    """
    Returns the timezone referenced by ``key``.
    """

    if key not in timezones:
        edbob.config.require('edbob.time', 'zone.%s' % key)
    return timezones[key]


def set_timezone(tz, key='local'):
    """
    Stores a timezone in the global dictionary, using ``key``.

    ``tz`` must be a valid "Olson" time zone name, e.g. ``'US/Central'``.  See
    `Wikipedia <http://en.wikipedia.org/wiki/List_of_tz_database_time_zones>`_
    for a (presumably) full list of valid names.
    """

    timezones[key] = pytz.timezone(tz)


def local_time(stamp=None, from_='local', naive=False):
    """
    Returns a :class:`datetime.datetime` instance, with its ``tzinfo`` member
    set to the timezone referenced by the key ``'local'``.  If ``naive`` is
    ``True``, the result is stripped of its ``tzinfo`` member.

    If ``stamp`` is provided, and it is not already "aware," then its value is
    interpreted as being local to the timezone referenced by ``from_``.

    If ``stamp`` is not provided, the current time is assumed.
    """

    if not stamp:
        stamp = utc_time()
    elif not stamp.tzinfo:
        stamp = localize(stamp, from_=from_)
    return localize(stamp, naive=naive)


def localize(stamp, from_='local', to='local', naive=False):
    """
    Creates a "localized" version of ``stamp`` and returns it.

    ``stamp`` must be a :class:`datetime.datetime` instance.  If it is naive,
    its value is interpreted as being local to the timezone referenced by
    ``from_``.  If it is already aware (i.e. not naive), then ``from_`` is
    ignored.

    The timezone referenced by ``to`` is used to determine the final, "local"
    value for the timestamp.  If ``naive`` is ``True``, the timestamp is
    stripped of its ``tzinfo`` member before being returned.  Otherwise, it
    will remain aware of its timezone.
    """

    if not stamp.tzinfo:
        tz = get_timezone(from_)
        stamp = tz.localize(stamp)
    tz = get_timezone(to)
    stamp = stamp.astimezone(tz)
    if naive:
        stamp = stamp.replace(tzinfo=None)
    return stamp


def utc_time(stamp=None, from_='local', naive=False):
    """
    Returns a :class:`datetime.datetime` instance, with its ``tzinfo`` member
    set to the UTC timezone.  If ``naive`` is ``True``, the result is stripped
    of its ``tzinfo`` member.

    If ``stamp`` is provided, and it is not already "aware," then its value is
    interpreted as being local to the timezone referenced by ``from_``.

    If ``stamp`` is not provided, the current time is assumed.
    """

    if not stamp:
        stamp = datetime.datetime.utcnow()
        stamp = pytz.utc.localize(stamp)
    elif not stamp.tzinfo:
        stamp = localize(stamp, from_=from_)
    return localize(stamp, to='utc', naive=naive)

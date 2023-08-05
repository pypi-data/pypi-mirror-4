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
``edbob.pyramid.tweens`` -- Tween Factories
"""

import sqlalchemy.exc

from transaction.interfaces import TransientError


def sqlerror_tween_factory(handler, registry):
    """
    Produces a tween which will convert ``sqlalchemy.exc.OperationalError``
    instances (caused by database server restart) into a retryable
    ``transaction.interfaces.TransientError`` instance, so that a second
    attempt may be made to connect to the database before really giving up.

    .. note::
       This tween alone is not enough to cause the transaction to be retried;
       it only marks the error as being *retryable*.  If you wish more than one
       attempt to be made, you must define the ``tm.attempts`` setting within
       your Pyramid app configuration.  See `Retrying
       <http://docs.pylonsproject.org/projects/pyramid_tm/en/latest/#retrying>`_
       for more information.
    """

    def sqlerror_tween(request):
        try:
            response = handler(request)
        except sqlalchemy.exc.OperationalError, error:
            if error.connection_invalidated:
                raise TransientError(str(error))
            raise
        return response

    return sqlerror_tween

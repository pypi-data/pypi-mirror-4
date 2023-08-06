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
``edbob.pyramid.auth`` -- Authentication & Authorization
"""

from zope.interface import implementer

from pyramid.interfaces import IAuthorizationPolicy
from pyramid.security import Everyone, Authenticated

import edbob
from edbob.db.auth import has_permission
from edbob.pyramid import Session


# def groupfinder(userid, request):
#     q = Session.query(edbob.UserRole)
#     q = q.filter(edbob.UserRole.user_uuid == userid)
#     return [x.role_uuid for x in q]


@implementer(IAuthorizationPolicy)
class EdbobAuthorizationPolicy(object):

    def permits(self, context, principals, permission):
        for userid in principals:
            if userid not in (Everyone, Authenticated):
                user = Session.query(edbob.User).get(userid)
                assert user
                return has_permission(user, permission)
        if Everyone in principals:
            return has_permission(None, permission, session=Session())
        return False

    def principals_allowed_by_permission(self, context, permission):
        raise NotImplementedError

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
``edbob.pyramid.progress`` -- Progress Indicator
"""

from beaker.session import Session


def get_progress_session(session, key):
    request = session.request
    id = '%s.progress.%s' % (session.id, key)
    session = Session(request, id)
    return session


class SessionProgress(object):
    """
    Provides a session-based progress bar mechanism.

    This class is only responsible for keeping the progress *data* current.  It
    is the responsibility of some client-side AJAX (etc.) to consume the data
    for display to the user.
    """

    def __init__(self, session, key):
        self.session = get_progress_session(session, key)
        self.cancelled = False

    def __call__(self, message, maximum):
        self.session['complete'] = False
        self.session['message'] = message
        self.session['maximum'] = maximum
        self.session['cancelled'] = False
        self.session['value'] = 0
        self.session.save()
        return self

    def update(self, value):
        self.session.load()
        if self.session.get('cancelled'):
            self.cancelled = True
        else:
            self.session['value'] = value
            self.session.save()
        return not self.cancelled

    def destroy(self):
        if not self.cancelled:
            self.session['complete'] = True
            self.session.save()

    def secondary_progress(self):
        return SecondarySessionProgress(self)
    

class SecondarySessionProgress(object):

    def __init__(self, parent):
        self.parent = parent
        self.session = parent.session

    def __call__(self, message, maximum):
        self.session['message'] = message
        self.session['value'] = 0
        self.session['maximum'] = maximum
        self.session.save()
        return self

    def update(self, value):
        return self.parent.update(value)

    def destroy(self):
        pass

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
``edbob.db.extensions.contact.enum`` -- Enumerations
"""


EMAIL_PREFERENCE_NONE           = 0
EMAIL_PREFERENCE_TEXT           = 1
EMAIL_PREFERENCE_HTML           = 2
EMAIL_PREFERENCE_MOBILE         = 3

EMAIL_PREFERENCE = {
    EMAIL_PREFERENCE_NONE       : "No Emails",
    EMAIL_PREFERENCE_TEXT       : "Text",
    EMAIL_PREFERENCE_HTML       : "HTML",
    EMAIL_PREFERENCE_MOBILE     : "Mobile",
    }

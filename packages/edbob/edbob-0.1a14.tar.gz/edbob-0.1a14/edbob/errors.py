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
``edbob.errors`` -- Error Alert Emails
"""

import sys
import socket
import logging
from traceback import format_exception
from cStringIO import StringIO

import edbob
from edbob.mail import sendmail_with_config


log = logging.getLogger(__name__)


def init(config):
    """
    Creates a system-wide exception hook which logs exceptions and emails them
    to configured recipient(s).
    """

    def excepthook(type, value, traceback):
        email_exception(type, value, traceback)
        sys.__excepthook__(type, value, traceback)

    sys.excepthook = excepthook


def email_exception(type=None, value=None, traceback=None):
    """
    Sends an email containing a traceback to the configured recipient(s).
    """

    if not (type and value and traceback):
        type, value, traceback = sys.exc_info()

    body = StringIO()

    hostname = socket.gethostname()
    body.write("An exception occurred.\n")
    body.write("\n")
    body.write("Machine Name:  %s (%s)\n" % (hostname, socket.gethostbyname(hostname)))
    body.write("Local Time:    %s\n" % (edbob.local_time().strftime('%Y-%m-%d %H:%M:%S %Z%z')))
    body.write("\n")
    body.write("%s\n" % ''.join(format_exception(type, value, traceback)))

    sendmail_with_config('errors', body.getvalue())
    body.close()

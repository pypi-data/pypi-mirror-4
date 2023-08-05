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

import os.path
import sys
import socket
import logging
from traceback import format_exception
from cStringIO import StringIO

import edbob
from edbob.files import resource_path
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

    hostname = socket.gethostname()
    traceback = ''.join(format_exception(type, value, traceback))
    traceback = traceback.strip()
    data = {
        'host_name':    hostname,
        'host_ip':      socket.gethostbyname(hostname),
        'host_time':    edbob.local_time(),
        'traceback':    traceback,
        }

    body, ctype = render_exception(data)
    ctype = edbob.config.get('edbob.errors', 'content_type', default=ctype)
    sendmail_with_config('errors', body, content_type=ctype)


def render_exception(data):
    """
    Renders the exception data using a Mako template if one is configured;
    otherwise as a simple string.
    """

    template = edbob.config.get('edbob.errors', 'template')
    if template:
        template = resource_path(template)
        if os.path.exists(template):

            # Assume Mako template; render and return.
            from mako.template import Template
            template = Template(filename=template)
            return template.render(**data), 'text/html'

    # If not a Mako template, return regular text with substitutions.
    body = StringIO()
    data['host_time'] = data['host_time'].strftime('%Y-%m-%d %H:%M:%S %Z%z')

    body.write("""\
An unhandled exception occurred.

Machine Name:  %(host_name)s (%(host_ip)s)

Machine Time:  %(host_time)s

%(traceback)s
""" % data)

    b = body.getvalue()
    body.close()

    return b, 'text/plain'

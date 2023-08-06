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
``edbob.mail`` -- Email Framework
"""

import logging
import smtplib
from email.message import Message

import edbob
from edbob import exceptions


log = logging.getLogger(__name__)


def sendmail(sender, recipients, subject, body, content_type='text/plain'):
    """
    Sends an email message from ``sender`` to each address in ``recipients``
    (which should be a sequence), with subject ``subject`` and body ``body``.

    If sending an HTML message instead of plain text, be sure to set
    ``content_type`` to ``'text/html'``.
    """
    message = Message()
    message.set_type(content_type)
    message['From'] = sender
    for recipient in recipients:
        message['To'] = recipient
    message['Subject'] = subject
    message.set_payload(body)

    server = edbob.config.get('edbob.mail', 'smtp.server',
                              default='localhost')
    username = edbob.config.get('edbob.mail', 'smtp.username')
    password = edbob.config.get('edbob.mail', 'smtp.password')

    log.debug("sendmail: connecting to server: %s" % server)
    session = smtplib.SMTP(server)
    if username and password:
        res = session.login(username, password)
        log.debug("sendmail: login result is: %s" % str(res))
    res = session.sendmail(message['From'], message.get_all('To'), message.as_string())
    log.debug("sendmail: sendmail result is: %s" % res)
    session.quit()


def get_sender(key):
    sender = edbob.config.get('edbob.mail', 'sender.'+key)
    if sender:
        return sender
    sender = edbob.config.get('edbob.mail', 'sender.default')
    if sender:
        return sender
    raise exceptions.SenderNotFound(key)


def get_recipients(key):
    recips = edbob.config.get('edbob.mail', 'recipients.'+key)
    if recips:
        return eval(recips)
    recips = edbob.config.get('edbob.mail', 'recipients.default')
    if recips:
        return eval(recips)
    raise exceptions.RecipientsNotFound(key)


def get_subject(key):
    subject = edbob.config.get('edbob.mail', 'subject.'+key)
    if subject:
        return subject
    subject = edbob.config.get('edbob.mail', 'subject.default')
    if subject:
        return subject
    return "[edbob]"


def sendmail_with_config(key, body, subject=None, **kwargs):
    """
    .. highlight:: ini

    Sends mail using sender/recipient/subject values found in config, according
    to ``key``.  Probably the easiest way to explain would be to show an example::
    
       [edbob.mail]
       smtp.server = localhost
       sender.default = Lance Edgar <lance@edbob.org>
       subject.default = A Nice Shrubbery, Not Too Expensive

       recipients.nightly_reports = ['Lance Edgar <lance@edbob.org>']

       subject.tragic_errors = The World Is Nearing The End!!
       recipients.tragic_errors = ['Lance Edgar <lance@edbob.org>']

    Anything not configured explicitly will fall back to defaults where
    possible.  Note however that a sender and recipients (default or otherwise)
    *must* be found or else an exception will be raised.

    The above does not include a default recipient list, but it would work the same
    as the subject and sender as far as the key goes.  To send these mails then::

       from edbob.mail import sendmail_with_config

       # just a report
       sendmail_with_config('nightly_reports', open('report.txt').read())

       # you might want to sit down for this one...
       sendmail_with_config('tragic_errors', open('OMGWTFBBQ.txt').read())

    If you do not provide ``subject`` to this function, and there is no
    ``subject.default`` setting found in config, a default of "[edbob]" will
    be used.
    """
    if subject is None:
        subject = get_subject(key)
    return sendmail(get_sender(key), get_recipients(key), subject, body, **kwargs)

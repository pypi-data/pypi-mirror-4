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
``edbob.csv`` -- CSV File Utilities
"""

from __future__ import absolute_import

import codecs
import csv


class UTF8Recoder(object):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8.

    .. note::
       This class was stolen from the Python 2.7 documentation.
    """

    def __init__(self, fileobj, encoding):
        self.reader = codecs.getreader(encoding)(fileobj)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode('utf_8')


class UnicodeReader(object):
    """
    A CSV reader which will iterate over lines in a CSV file, which is encoded
    in the given encoding.

    .. note::
       This class was stolen from the Python 2.7 documentation.
    """

    def __init__(self, fileobj, dialect=csv.excel, encoding='utf_8', **kwargs):
        fileobj = UTF8Recoder(fileobj, encoding)
        self.reader = csv.reader(fileobj, dialect=dialect, **kwargs)

    def __iter__(self):
        return self

    def next(self):
        row = self.reader.next()
        return [unicode(x, 'utf_8') for x in row]

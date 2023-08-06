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
``edbob.console`` -- Console-Specific Stuff
"""

import sys
import progressbar

import edbob


class Progress(edbob.Object):
    """
    Provides a console-based progress bar.
    """

    def __init__(self, message, maximum):
        sys.stderr.write("\n%s...(%u total)\n" % (message, maximum))
        widgets = [progressbar.Percentage(), ' ', progressbar.Bar(), ' ', progressbar.ETA()]
        self.progress = progressbar.ProgressBar(maxval=maximum, widgets=widgets).start()

    def update(self, value):
        self.progress.update(value)
        return True

    def destroy(self):
        sys.stderr.write("\n")

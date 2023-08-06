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
``edbob.filemon`` -- File Monitoring Service
"""

import os.path
import logging

import edbob


log = logging.getLogger(__name__)


class MonitorProfile(object):
    """
    This is a simple profile class, used to represent configuration of the file
    monitor service.
    """

    def __init__(self, appname, key):
        self.appname = appname
        self.key = key

        self.dirs = edbob.config.require('%s.filemon' % appname, '%s.dirs' % key)
        self.dirs = eval(self.dirs)

        actions = edbob.config.require('%s.filemon' % appname, '%s.actions' % key)
        actions = eval(actions)

        self.actions = []
        for action in actions:
            if isinstance(action, tuple):
                spec = action[0]
                args = list(action[1:])
            else:
                spec = action
                args = []
            func = edbob.load_spec(spec)
            self.actions.append((spec, func, args))

        self.locks = edbob.config.getboolean(
            '%s.filemon' % appname, '%s.locks' % key, default=False)


def get_monitor_profiles(appname):
    """
    Convenience function to load monitor profiles from config.
    """

    monitored = {}

    # Read monitor profile(s) from config.
    keys = edbob.config.require('%s.filemon' % appname, 'monitored')
    keys = keys.split(',')
    for key in keys:
        key = key.strip()
        profile = MonitorProfile(appname, key)
        monitored[key] = profile
        for path in profile.dirs[:]:

            # Ensure the monitored path exists.
            if not os.path.exists(path):
                log.warning("get_monitor_profiles: Profile '%s' has nonexistent "
                            "path, which will be pruned: %s" % (key, path))
                profile.dirs.remove(path)

            # Ensure the monitored path is a folder.
            elif not os.path.isdir(path):
                log.warning("get_monitor_profiles: Profile '%s' has non-folder "
                            "path, which will be pruned: %s" % (key, path))
                profile.dirs.remove(path)

    for key in monitored.keys():
        profile = monitored[key]

        # Prune any profiles with no valid folders to monitor.
        if not profile.dirs:
            log.warning("get_monitor_profiles: Profile '%s' has no folders to "
                        "monitor, and will be pruned." % key)
            del monitored[key]

        # Prune any profiles with no valid actions to perform.
        elif not profile.actions:
            log.warning("get_monitor_profiles: Profile '%s' has no actions to "
                        "perform, and will be pruned." % key)
            del monitored[key]

    return monitored

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

import os
import os.path
import sys
import Queue
import logging

import edbob
from edbob.errors import email_exception

if sys.platform == 'win32':
    import win32api
    from edbob.win32 import file_is_free


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

        self.process_existing = edbob.config.getboolean(
            '%s.filemon' % appname, '%s.process_existing' % key, default=True)

        self.stop_on_error = edbob.config.getboolean(
            '%s.filemon' % appname, '%s.stop_on_error' % key, default=False)


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


def queue_existing(profile, path):
    """
    Adds files found in a watched folder to a processing queue.  This is called
    when the monitor first starts, to handle the case of files which exist
    prior to startup.

    If files are found, they are first sorted by modification timestamp, using
    a lexical sort on the filename as a tie-breaker, and then added to the
    queue in that order.

    :param profile: Monitor profile for which the folder is to be watched.  The
    profile is expected to already have a queue attached; any existing files
    will be added to this queue.
    :type profile: :class:`edbob.filemon.MonitorProfile` instance

    :param path: Folder path which is to be checked for files.
    :type path: string

    :returns: ``None``
    """

    def sorter(x, y):
        mtime_x = os.path.getmtime(x)
        mtime_y = os.path.getmtime(y)
        if mtime_x < mtime_y:
            return -1
        if mtime_x > mtime_y:
            return 1
        return cmp(x, y)

    paths = [os.path.join(path, x) for x in os.listdir(path)]
    for path in sorted(paths, cmp=sorter):

        # Only process normal files.
        if not os.path.isfile(path):
            continue

        # If using locks, don't process "in transit" files.
        if profile.locks and path.endswith('.lock'):
            continue

        log.debug("queue_existing: queuing existing file for "
                  "profile '%s': %s" % (profile.key, path))
        profile.queue.put(path)


def perform_actions(profile):
    """
    Callable target for action threads.
    """

    keep_going = True
    while keep_going:

        try:
            path = profile.queue.get_nowait()
        except Queue.Empty:
            pass
        else:

            # In some cases, processing one file may cause other related files
            # to also be processed.  When this happens, a path on the queue may
            # point to a file which no longer exists.
            if not os.path.exists(path):
                log.info("perform_actions: path does not exist: %s" % path)
                continue

            log.debug("perform_actions: processing file: %s" % path)

            if sys.platform == 'win32':
                while not file_is_free(path):
                    win32api.Sleep(0)

            for spec, func, args in profile.actions:

                log.info("perform_actions: calling function '%s' on file: %s" %
                         (spec, path))

                try:
                    func(path, *args)

                except:
                    log.exception("perform_actions: exception occurred "
                                  "while processing file: %s" % path)
                    email_exception()

                    # Don't process any more files if the profile is so
                    # configured.
                    if profile.stop_on_error:
                        keep_going = False

                    # Either way this particular file probably shouldn't be
                    # processed any further.
                    log.warning("perform_actions: no further processing "
                                "will be done for file: %s" % path)
                    break

    log.warning("perform_actions: error encountered, and configuration "
                "dictates that no more actions will be processed for "
                "profile: %s" % profile.key)

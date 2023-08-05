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
``edbob.filemon.linux`` -- File Monitor for Linux
"""

import sys
import os
import os.path
import signal
import logging
import pyinotify

import edbob
from edbob.filemon import get_monitor_profiles


log = logging.getLogger(__name__)


class EventHandler(pyinotify.ProcessEvent):
    """
    Event processor for file monitor daemon.
    """

    def my_init(self, actions=[], locks=False, **kwargs):
        self.actions = actions
        self.locks = locks

    def process_IN_ACCESS(self, event):
        log.debug("EventHandler: IN_ACCESS: %s" % event.pathname)

    def process_IN_ATTRIB(self, event):
        log.debug("EventHandler: IN_ATTRIB: %s" % event.pathname)

    def process_IN_CLOSE_WRITE(self, event):
        log.debug("EventHandler: IN_CLOSE_WRITE: %s" % event.pathname)
        if not self.locks:
            self.perform_actions(event.pathname)

    def process_IN_CREATE(self, event):
        log.debug("EventHandler: IN_CREATE: %s" % event.pathname)

    def process_IN_DELETE(self, event):
        log.debug("EventHandler: IN_DELETE: %s" % event.pathname)
        if self.locks and event.pathname.endswith('.lock'):
            self.perform_actions(event.pathname[:-5])

    def process_IN_MODIFY(self, event):
        log.debug("EventHandler: IN_MODIFY: %s" % event.pathname)

    def process_IN_MOVED_TO(self, event):
        log.debug("EventHandler: IN_MOVED_TO: %s" % event.pathname)
        if not self.locks:
            self.perform_actions(event.pathname)

    def perform_actions(self, path):
        for spec, func, args in self.actions:
            func(path, *args)


def get_pid_path():
    """
    Returns the path to the PID file for the file monitor daemon.
    """

    basename = os.path.basename(sys.argv[0])
    return '/tmp/%s_filemon.pid' % basename


def start_daemon(appname, daemonize=True):
    """
    Starts the file monitor daemon.
    """

    pid_path = get_pid_path()
    if os.path.exists(pid_path):
        print "File monitor is already running"
        return

    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm)

    monitored = get_monitor_profiles(appname)

    mask = (pyinotify.IN_ACCESS | pyinotify.IN_ATTRIB
            | pyinotify.IN_CLOSE_WRITE | pyinotify.IN_CREATE
            | pyinotify.IN_DELETE | pyinotify.IN_MODIFY
            | pyinotify.IN_MOVED_TO)
    for profile in monitored.itervalues():
        for path in profile.dirs:
            wm.add_watch(path, mask, proc_fun=EventHandler(
                    actions=profile.actions, locks=profile.locks))

    if not daemonize:
        sys.stderr.write("Starting file monitor.  (Press Ctrl+C to quit.)\n")
    notifier.loop(daemonize=daemonize, pid_file=pid_path)


def stop_daemon():
    """
    Stops the file monitor daemon.
    """

    pid_path = get_pid_path()
    if not os.path.exists(pid_path):
        print "File monitor is not running"
        return

    f = open(pid_path)
    pid = f.read().strip()
    f.close()
    if not pid.isdigit():
        log.warning("stop_daemon: Found bogus PID (%s) in file: %s" % (pid, pid_path))
        return

    os.kill(int(pid), signal.SIGKILL)
    os.remove(pid_path)

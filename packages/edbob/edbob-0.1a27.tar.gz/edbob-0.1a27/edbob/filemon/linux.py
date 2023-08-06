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
import os.path
import pyinotify
import threading
import Queue
import logging

import edbob
from edbob import filemon
from edbob.daemon import Daemon
from edbob.errors import email_exception


log = logging.getLogger(__name__)


class EventHandler(pyinotify.ProcessEvent):
    """
    Event processor for file monitor daemon.
    """

    def my_init(self, profile=None, **kwargs):
        self.profile = profile

    def process_IN_ACCESS(self, event):
        log.debug("EventHandler: IN_ACCESS: %s" % event.pathname)

    def process_IN_ATTRIB(self, event):
        log.debug("EventHandler: IN_ATTRIB: %s" % event.pathname)

    def process_IN_CLOSE_WRITE(self, event):
        log.debug("EventHandler: IN_CLOSE_WRITE: %s" % event.pathname)
        if not self.profile.locks:
            self.profile.queue.put(event.pathname)

    def process_IN_CREATE(self, event):
        log.debug("EventHandler: IN_CREATE: %s" % event.pathname)

    def process_IN_DELETE(self, event):
        log.debug("EventHandler: IN_DELETE: %s" % event.pathname)
        if self.profile.locks and event.pathname.endswith('.lock'):
            self.profile.queue.put(event.pathname[:-5])

    def process_IN_MODIFY(self, event):
        log.debug("EventHandler: IN_MODIFY: %s" % event.pathname)

    def process_IN_MOVED_TO(self, event):
        log.debug("EventHandler: IN_MOVED_TO: %s" % event.pathname)
        if not self.profile.locks:
            self.profile.queue.put(event.pathname)


class FileMonitorDaemon(Daemon):

    def run(self):

        wm = pyinotify.WatchManager()
        notifier = pyinotify.Notifier(wm)

        mask = (pyinotify.IN_ACCESS
                | pyinotify.IN_ATTRIB
                | pyinotify.IN_CLOSE_WRITE
                | pyinotify.IN_CREATE
                | pyinotify.IN_DELETE
                | pyinotify.IN_MODIFY
                | pyinotify.IN_MOVED_TO)

        monitored = filemon.get_monitor_profiles(self.appname)
        for key, profile in monitored.iteritems():

            # Create a file queue for the profile.
            profile.queue = Queue.Queue()

            # Perform setup for each of the watched folders.
            for path in profile.dirs:

                # Maybe put all pre-existing files in the queue.
                if profile.process_existing:
                    filemon.queue_existing(profile, path)

                # Create a watch for the folder.
                log.debug("start_daemon: profile '%s' watches folder: %s" % (key, path))
                wm.add_watch(path, mask, proc_fun=EventHandler(profile=profile))

            # Create an action thread for the profile.
            name = 'actions-%s' % key
            log.debug("start_daemon: starting action thread: %s" % name)
            thread = threading.Thread(target=filemon.perform_actions,
                                      name=name, args=(profile,))
            thread.daemon = True
            thread.start()

        # Fire up the watchers.
        notifier.loop()


def get_daemon(appname=None):
    if appname is None:
        appname = os.path.basename(sys.argv[0])
    pid_path = edbob.config.get('%s.filemon' % appname, 'pid_path')
    if not pid_path:
        pid_path = '/tmp/%s_filemon.pid' % appname

    monitor = FileMonitorDaemon(pid_path)
    monitor.appname = appname
    return monitor


def start_daemon(appname):
    get_daemon(appname).start()


def stop_daemon(appname):
    get_daemon(appname).stop()

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
``edbob.filemon.win32`` -- File Monitoring Service for Windows
"""

import os.path
import sys
import Queue
import logging
import threading

import edbob
from edbob.errors import email_exception
from edbob.filemon import get_monitor_profiles
from edbob.win32 import Service, file_is_free

if sys.platform == 'win32': # docs should build for everyone
    import win32api
    import win32con
    import win32event
    import win32file
    import win32service
    import win32serviceutil
    import winnt


log = logging.getLogger(__name__)


class FileMonitorService(Service):
    """
    Implements edbob's file monitor Windows service.
    """

    _svc_name_ = 'EdbobFileMonitor'
    _svc_display_name_ = "Edbob : File Monitoring Service"
    _svc_description_ = ("Monitors one or more folders for incoming files, "
                         "and performs configured actions as new files arrive.")

    def Initialize(self):
        """
        Service initialization.
        """

        if not Service.Initialize(self):
            return False

        # Read monitor profile(s) from config.
        self.monitored = get_monitor_profiles(self.appname)

        # Make sure we have something to do.
        if not self.monitored:
            return False

        # Create monitor and action threads for each profile.
        for key, profile in self.monitored.iteritems():

            # Create a file queue for the profile.
            queue = Queue.Queue()

            # Create a monitor thread for each folder in profile.
            for i, path in enumerate(profile.dirs, 1):
                name = 'monitor-%s-%u' % (key, i)
                log.debug("Initialize: Starting '%s' thread for folder: %s" %
                          (name, path))
                thread = threading.Thread(
                    target=monitor_files,
                    name=name,
                    args=(queue, path, profile))
                thread.daemon = True
                thread.start()

            # Create an action thread for the profile.
            name = 'actions-%s' % key
            log.debug("Initialize: Starting '%s' thread" % name)
            thread = threading.Thread(
                target=perform_actions,
                name=name,
                args=(queue, profile))
            thread.daemon = True
            thread.start()

        return True

    
def monitor_files(queue, path, profile):
    """
    Callable target for file monitor threads.
    """

    hDir = win32file.CreateFile(
        path,
        winnt.FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None)

    if hDir == win32file.INVALID_HANDLE_VALUE:
        log.warning("monitor_files: Can't open directory with CreateFile(): %s" % path)
        return

    while True:
        results = win32file.ReadDirectoryChangesW(
            hDir,
            1024,
            False,
            win32con.FILE_NOTIFY_CHANGE_FILE_NAME)

        log.debug("monitor_files: ReadDirectoryChangesW() results: %s" % results)
        for action, fname in results:
            fpath = os.path.join(path, fname)
            if action in (winnt.FILE_ACTION_ADDED,
                          winnt.FILE_ACTION_RENAMED_NEW_NAME):
                log.debug("monitor_files: Queueing '%s' file: %s" %
                          (profile.key, fpath))
                queue.put(fpath)


def perform_actions(queue, profile):
    """
    Callable target for action threads.
    """

    while True:

        try:
            path = queue.get_nowait()
        except Queue.Empty:
            pass
        else:

            while not file_is_free(path):
                win32api.Sleep(0)

            for spec, func, args in profile.actions:

                log.info("perform_actions: Calling function '%s' on file: %s" %
                         (spec, path))

                try:
                    func(path, *args)

                except:
                    log.exception("perform_actions: An exception occurred "
                                  "while processing file: %s" % path)
                    email_exception()

                    # This file probably shouldn't be processed any further.
                    break


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(FileMonitorService)

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
``edbob.win32`` -- Stuff for Microsoft Windows
"""

import sys
import subprocess
import logging

if sys.platform == 'win32': # docs should build for everyone
    import pywintypes
    import win32api
    import win32con
    import win32event
    import win32file
    import win32print
    import win32service
    import win32serviceutil
    import winerror

import edbob


log = logging.getLogger(__name__)


class Service(win32serviceutil.ServiceFramework):
    """
    Base class for Windows service implementations.
    """

    appname = 'edbob'

    def __init__(self, args):
        """
        Constructor.
        """

        win32serviceutil.ServiceFramework.__init__(self, args)

        # Create "wait stop" event, for main worker loop.
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def Initialize(self):
        """
        Service initialization.
        """

        # Read configuration file(s).
        edbob.init(self.appname, service=self._svc_name_)

        return True

    def SvcDoRun(self):
        """
        This method is invoked when the service starts.
        """

        import servicemanager

        # Write start occurrence to Windows Event Log.
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ''))

        # Figure out what we're supposed to be doing.
        if self.Initialize():

            # Wait infinitely for stop request, while threads do their thing.
            log.info("SvcDoRun: All threads started; waiting for stop request.")
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            log.info("SvcDoRun: Stop request received.")

        else: # Nothing to be done...
            msg = "Nothing to do!  (Initialization failed.)"
            servicemanager.LogWarningMsg(msg)
            log.warning("SvcDoRun: %s" % msg)
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        # Write stop occurrence to Windows Event Log.
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STOPPED,
            (self._svc_name_, ''))

    def SvcStop(self):
        """
        This method is invoked when the service is requested to stop itself.
        """

        # Let the SCM know we're trying to stop.
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        # Let worker loop know its job is done.
        win32event.SetEvent(self.hWaitStop)


def RegDeleteTree(key, subkey):
    """
    This is a clone of ``win32api.RegDeleteTree()``, since that apparently
    requires Vista or later.
    """

    def delete_contents(key):
        subkeys = []
        for name, reserved, class_, mtime in win32api.RegEnumKeyEx(key):
            subkeys.append(name)
        for subkey_name in subkeys:
            subkey = win32api.RegOpenKeyEx(key, subkey_name, 0, win32con.KEY_ALL_ACCESS)
            delete_contents(subkey)
            win32api.RegCloseKey(subkey)
            win32api.RegDeleteKey(key, subkey_name)
        values = []
        i = 0
        while True:
            try:
                name, value, type_ = win32api.RegEnumValue(key, i)
            except pywintypes.error, e:
                if e[0] == winerror.ERROR_NO_MORE_ITEMS:
                    break
            values.append(name)
            i += 1
        for value in values:
            win32api.RegDeleteValue(key, value)

    orig_key = key
    try:
        key = win32api.RegOpenKeyEx(orig_key, subkey, 0, win32con.KEY_ALL_ACCESS)
    except pywintypes.error, e:
        if e[0] != winerror.ERROR_FILE_NOT_FOUND:
            raise
    else:
        delete_contents(key)
        win32api.RegCloseKey(key)
    try:
        win32api.RegDeleteKey(orig_key, subkey)
    except pywintypes.error, e:
        if e[0] == winerror.ERROR_FILE_NOT_FOUND:
            pass


def delayed_auto_start_service(name):
    """
    Configures the Windows service named ``name`` such that its startup type is
    "Automatic (Delayed Start)".

    .. note::
       It is assumed that the service is already configured to start
       automatically.  This function only modifies the service so that its
       automatic startup is delayed.
    """

    hSCM = win32service.OpenSCManager(
        None,
        None,
        win32service.SC_MANAGER_ENUMERATE_SERVICE)

    hService = win32service.OpenService(
        hSCM,
        name,
        win32service.SERVICE_CHANGE_CONFIG)

    win32service.ChangeServiceConfig2(
        hService,
        win32service.SERVICE_CONFIG_DELAYED_AUTO_START_INFO,
        True)

    win32service.CloseServiceHandle(hService)
    win32service.CloseServiceHandle(hSCM)


def execute_service_command(module, command, *args):
    """
    Executes ``command`` against the Windows service contained in ``module``.

    ``module`` must be a proper module object, which is assumed to implement a
    command line interface when invoked directly by the Python interpreter, a
    la ``win32serviceutil.HandleCommandLine()``.

    ``command`` may be anything supported by ``HandleCommandLine()``, e.g.:

    * ``'install'``
    * ``'remove'``
    * ``'start'``
    * ``'stop'``
    * ``'restart'``

    ``args``, if present, are assumed to be "option" arguments and will precede
    ``command`` when the command line is constructed.
    """

    command = [command]
    if args:
        command = list(args) + command
    subprocess.call([sys.executable, module.__file__] + command)


def file_is_free(path):
    """
    Returns boolean indicating whether or not the file located at ``path`` is
    currently tied up in any way by another process.
    """

    # This code was borrowed from Nikita Nemkin:
    # http://stackoverflow.com/a/2848266

    handle = None
    try:
        handle = win32file.CreateFile(
            path,
            win32file.GENERIC_WRITE,
            0,
            None,
            win32file.OPEN_EXISTING,
            win32file.FILE_ATTRIBUTE_NORMAL,
            None)
        return True
    except pywintypes.error, e:
        if e[0] == winerror.ERROR_SHARING_VIOLATION:
            return False
        raise
    finally:
        if handle:
            win32file.CloseHandle(handle)


def send_data_to_printer(data, printer_name, job_name):
    """
    Create and submit a new print job (named ``job_name``) which sends ``data``
    directly to the Windows printer identified by ``printer_name``.  Returns
    the number of bytes actually written to the printer port.

    This is designed for sending command strings to Zebra label printers, but
    could potentially be useful for other situations as well.
    """

    printer = win32print.OpenPrinter(printer_name)
    assert printer
    assert win32print.StartDocPrinter(printer, 1, (job_name, None, None))
    win32print.StartPagePrinter(printer)
    num_bytes = win32print.WritePrinter(printer, data)
    win32print.EndPagePrinter(printer)
    win32print.EndDocPrinter(printer)
    win32print.ClosePrinter(printer)
    return num_bytes

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
``edbob.commands`` -- Console Commands
"""

from __future__ import absolute_import

import sys
import argparse
import subprocess
import logging
import platform

import edbob
from edbob.util import entry_point_map, requires_impl


class ArgumentParser(argparse.ArgumentParser):
    """
    Customized version of ``argparse.ArgumentParser``, which overrides some of
    the argument parsing logic.  This is necessary for the application's
    primary command (:class:`Command` class); but is not used with
    :class:`Subcommand` derivatives.
    """

    def parse_args(self, args=None, namespace=None):
        args, argv = self.parse_known_args(args, namespace)
        args.argv = argv
        return args


class Command(edbob.Object):
    """
    The primary command for the application.  

    You should subclass this within your own application if you wish to
    leverage the command system provided by edbob.
    """
    
    name = 'edbob'
    version = edbob.__version__
    description = "Pythonic Software Framework"

    long_description = """
edbob is a Pythonic software framework.

Copyright (c) 2010-2012 Lance Edgar <lance@edbob.org>

This program comes with ABSOLUTELY NO WARRANTY.  This is free software,
and you are welcome to redistribute it under certain conditions.
See the file COPYING.txt for more information.
"""

    def __init__(self, **kwargs):
        edbob.Object.__init__(self, **kwargs)
        self.subcommands = entry_point_map('%s.commands' % self.name)

    def __str__(self):
        return str(self.name)

    def iter_subcommands(self):
        """
        Generator which yields associated :class:`Subcommand` classes, sorted
        by :attr:`Subcommand.name`.
        """

        for name in sorted(self.subcommands):
            yield self.subcommands[name]

    def print_help(self):
        """
        Prints help text for the primary command, including a list of available
        subcommands.
        """

        print """%(description)s

Usage: %(name)s [options] <command> [command-options]

Options:
  -c PATH, --config=PATH
                    Config path (may be specified more than once)
  -n, --no-init     Don't load config before executing command
  -d, --debug       Increase logging level to DEBUG
  -v, --verbose     Increase logging level to INFO
  -V, --version     Display program version and exit

Commands:""" % self

        for cmd in self.iter_subcommands():
            print "  %-16s  %s" % (cmd.name, cmd.description)

        print """
Try '%(name)s help <command>' for more help.""" % self

    def run(self, *args):
        """
        Parses ``args`` and executes the appropriate subcommand action
        accordingly (or displays help text).
        """

        parser = ArgumentParser(
            prog=self.name,
            description=self.description,
            add_help=False,
            )

        parser.add_argument('-c', '--config', action='append', dest='config_paths',
                            metavar='PATH')
        parser.add_argument('-d', '--debug', action='store_true', dest='debug')
        parser.add_argument('-n', '--no-init', action='store_true', default=False)
        parser.add_argument('-v', '--verbose', action='store_true', dest='verbose')
        parser.add_argument('-V', '--version', action='version',
                            version="%%(prog)s %s" % self.version)
        parser.add_argument('command', nargs='*')

        # Parse args and determind subcommand.
        args = parser.parse_args(list(args))
        if not args or not args.command:
            self.print_help()
            return

        # Show (sub)command help if so instructed, or unknown subcommand.
        cmd = args.command.pop(0)
        if cmd == 'help':
            if len(args.command) != 1:
                self.print_help()
                return
            cmd = args.command[0]
            if cmd not in self.subcommands:
                self.print_help()
                return
            cmd = self.subcommands[cmd](parent=self)
            cmd.parser.print_help()
            return
        elif cmd not in self.subcommands:
            self.print_help()
            return

        # Basic logging should be established before init()ing.

        # Use root logger if setting logging flags.
        log = logging.getLogger()
        edbob.basic_logging()
        if args.verbose:
            log.setLevel(logging.INFO)
        if args.debug:
            log.setLevel(logging.DEBUG)

        # Initialize everything...
        if not args.no_init:
            edbob.init(self.name, *(args.config_paths or []))

            # Command line logging flags should override config.
            if args.verbose:
                log.setLevel(logging.INFO)
            if args.debug:
                log.setLevel(logging.DEBUG)
        
        # And finally, do something of real value...
        cmd = self.subcommands[cmd](parent=self)
        cmd._run(*(args.command + args.argv))


class Subcommand(edbob.Object):
    """
    Base class for application "subcommands."  You'll want to derive from this
    class as needed to implement most of your application's command logic.
    """

    def __init__(self, **kwargs):
        edbob.Object.__init__(self, **kwargs)
        self.parser = argparse.ArgumentParser(
            prog='%s %s' % (self.parent, self.name),
            description=self.description,
            )
        self.add_parser_args(self.parser)

    @property
    @requires_impl(is_property=True)
    def name(self):
        """
        The name of the subcommand.

        .. note::
           The subcommand name should ideally be limited to 12 characters in
           order to preserve formatting consistency when displaying help text.
        """
        pass

    @property
    @requires_impl(is_property=True)
    def description(self):
        """
        The description for the subcommand.
        """
        pass

    def __repr__(self):
        return "<Subcommand: %s>" % self.name

    def add_parser_args(self, parser):
        """
        If your subcommand accepts optional (or positional) arguments, you
        should override this and add the possible arguments directly to
        ``parser`` (which is a :class:`argparse.ArgumentParser` instance) via
        its ``add_argument()`` method.
        """
        pass
            
    def _run(self, *args):
        args = self.parser.parse_args(list(args))
        return self.run(args)

    @requires_impl()
    def run(self, args):
        """
        Runs the subcommand.  You must override this method within your
        subclass.  ``args`` will be a :class:`argparse.Namespace` object
        containing all parsed arguments found on the original command line
        executed by the user.
        """
        pass


class DatabaseCommand(Subcommand):
    """
    Provides tools for managing an ``edbob`` database; called as ``edbob db``.

    This command requires additional arguments; see ``edbob help db`` for more
    information.
    """

    name = 'db'
    description = "Tools for managing edbob databases"

    def add_parser_args(self, parser):
        parser.add_argument('-D', '--database', metavar='URL',
                            help="Database engine (default is edbob.db.engine)")
        # parser.add_argument('command', choices=['upgrade', 'extensions', 'activate', 'deactivate'],
        #                     help="Command to execute against database")
        subparsers = parser.add_subparsers(title='subcommands')

        extensions = subparsers.add_parser('extensions',
                                           help="Display current extension status for the database")
        extensions.set_defaults(func=self.extensions)

        activate = subparsers.add_parser('activate',
                                         help="Activate an extension within the database")
        activate.add_argument('extension', help="Name of extension to activate")
        activate.set_defaults(func=self.activate)

        deactivate = subparsers.add_parser('deactivate',
                                           help="Deactivate an extension within the database")
        deactivate.add_argument('extension', help="Name of extension to deactivate")
        deactivate.set_defaults(func=self.deactivate)

    def activate(self, engine, args):
        from edbob.db.extensions import (
            available_extensions,
            extension_active,
            activate_extension,
            )

        if args.extension in available_extensions():
            if not extension_active(args.extension, engine):
                activate_extension(args.extension, engine)
                print "Activated extension '%s' in database:" % args.extension
                print '  %s' % engine.url
            else:
                print >> sys.stderr, "Extension already active: %s" % args.extension
        else:
            print >> sys.stderr, "Extension unknown: %s" % args.extension

    def deactivate(self, engine, args):
        from edbob.db.extensions import (
            available_extensions,
            extension_active,
            deactivate_extension,
            )

        if args.extension in available_extensions():
            if extension_active(args.extension, engine):
                deactivate_extension(args.extension, engine)
                print "Deactivated extension '%s' in database:" % args.extension
                print '  %s' % engine.url
            else:
                print >> sys.stderr, "Extension already inactive: %s" % args.extension
        else:
            print >> sys.stderr, "Extension unknown: %s" % args.extension

    def extensions(self, engine, args):
        from edbob.db.extensions import (
            available_extensions,
            extension_active,
            )

        print "Extensions for database:"
        print '  %s' % engine.url
        print ''
        print " Name            Active?"
        print "------------------------"
        for name in sorted(available_extensions()):
            print " %-16s  %s" % (
                name, 'Yes' if extension_active(name, engine) else 'No')
        print ''
        print "Use 'edbob db [de]activate <extension>' to change."

    def run(self, args):
        if args.database:
            from sqlalchemy import create_engine
            from sqlalchemy.exc import ArgumentError
            try:
                engine = create_engine(args.database)
            except ArgumentError, err:
                print err
                return
        else:
            from edbob.db import engine
        if not engine:
            print >> sys.stderr, "Database not configured; please change that or specify -D URL"
            return
        args.func(engine, args)


# class ExtensionsCommand(RattailCommand):
#     """
#     Displays the currently-installed (available) extensions, and whether or not
#     each has been activated within the configured database.  Called as
#     ``rattail extensions``.
#     """

#     short_description = "Displays available extensions and their statuses"

#     def __call__(self, options, **args):
#         from sqlalchemy.exc import OperationalError
#         from rattail import engine
#         from rattail.db.util import core_schema_installed
#         from rattail.db.ext import get_available_extensions, extension_active

#         try:
#             engine.connect()
#         except OperationalError, e:
#             print >> sys.stderr, "Cannot connect to database:"
#             print >> sys.stderr, engine.url
#             print >> sys.stderr, e[0].strip()
#             return

#         if not core_schema_installed():
#             print >> sys.stderr, "Database lacks core schema:"
#             print >> sys.stderr, engine.url
#             return

#         extensions = get_available_extensions()
#         print ''
#         print ' %-25s %-10s' % ("Extension", "Active?")
#         print '-' * 35
#         for name in sorted(extensions):
#             active = 'Y' if extension_active(name) else 'N'
#             print ' %-28s %s' % (name, active)
#         print ''
#         print "Use 'rattail {activate|deactivate} EXTENSION' to change."

        
class FileMonitorCommand(Subcommand):
    """
    Interacts with the file monitor service; called as ``edbob filemon``.  This
    command expects a subcommand; one of the following:

    * ``edbob filemon start``
    * ``edbob filemon stop``

    On Windows platforms, the following additional subcommands are available:

    * ``edbob filemon install``
    * ``edbob filemon uninstall``

    .. note::
       The Windows Vista family of operating systems requires you to launch
       ``cmd.exe`` as an Administrator in order to have sufficient rights to
       run the above commands.

       .. todo::
          Verify the previous statement...  (Maybe test with/out UAC?)

    See :doc:`howto.use_filemon` for more information.
    """

    name = 'filemon'
    description = "Manage the file monitor service"

    appname = 'edbob'

    def add_parser_args(self, parser):
        subparsers = parser.add_subparsers(title='subcommands')

        start = subparsers.add_parser('start', help="Start service")
        start.set_defaults(subcommand='start')
        stop = subparsers.add_parser('stop', help="Stop service")
        stop.set_defaults(subcommand='stop')

        if sys.platform == 'win32':
            install = subparsers.add_parser('install', help="Install service")
            install.set_defaults(subcommand='install')
            install.add_argument('-a', '--auto-start', action='store_true',
                                 help="Configure service to start automatically")
            remove = subparsers.add_parser('remove', help="Uninstall (remove) service")
            remove.set_defaults(subcommand='remove')
            uninstall = subparsers.add_parser('uninstall', help="Uninstall (remove) service")
            uninstall.set_defaults(subcommand='remove')

        else:
            parser.add_argument('-D', '--dont-daemonize',
                                action='store_false', dest='daemonize',
                                help="Don't daemonize when starting")

    def get_win32_module(self):
        from edbob.filemon import win32
        return win32

    def get_win32_service(self):
        from edbob.filemon.win32 import FileMonitorService
        return FileMonitorService

    def get_win32_service_name(self):
        service = self.get_win32_service()
        return service._svc_name_

    def run(self, args):
        if sys.platform == 'linux2':
            from edbob.filemon import linux as filemon

            if args.subcommand == 'start':
                filemon.start_daemon(self.appname, daemonize=args.daemonize)

            elif args.subcommand == 'stop':
                filemon.stop_daemon()

        elif sys.platform == 'win32':
            from edbob import win32

            filemon = self.get_win32_module()

            # Execute typical service command.
            options = []
            if args.subcommand == 'install' and args.auto_start:
                options = ['--startup', 'auto']
            win32.execute_service_command(filemon, args.subcommand, *options)

            # If installing auto-start service on Windows 7, we should update
            # its startup type to be "Automatic (Delayed Start)".
            if args.subcommand == 'install' and args.auto_start:
                if platform.release() == '7':
                    name = self.get_win32_service_name()
                    win32.delayed_auto_start_service(name)

        else:
            print "Sorry, file monitor is not supported on platform %s." % sys.platform


class ShellCommand(Subcommand):
    """
    Launches a Python shell (of your choice) with ``edbob`` pre-loaded; called
    as ``edbob shell``.

    You can define the shell within your config file (otherwise ``python`` is
    assumed)::

    .. highlight:: ini

       [edbob]
       shell.python = ipython
    """

    name = 'shell'
    description = "Launch Python shell with edbob pre-loaded"

    def run(self, args):
        code = ['import edbob']
        if edbob.inited:
            code.append("edbob.init('edbob', %s, shell=True)" %
                        edbob.config.paths_loaded)
        code.append('from edbob import *')
        code = '; '.join(code)
        print "edbob v%s launching Python shell...\n" % edbob.__version__
        python = 'python'
        if edbob.inited:
            python = edbob.config.get('edbob', 'shell.python', default=python)
        proc = subprocess.Popen([python, '-i', '-c', code])
        while True:
            try:
                proc.wait()
            except KeyboardInterrupt:
                pass
            else:
                break


class UuidCommand(Subcommand):
    """
    Command for generating an UUID; called as ``edbob uuid``.

    If the ``--gui`` option is specified, this command launches a small
    wxPython application for generating UUIDs; otherwise a single UUID will be
    printed to the console.
    """

    name = 'uuid'
    description = "Generate an universally-unique identifier"

    def add_parser_args(self, parser):
        parser.add_argument('--gui', action='store_true',
                            help="Display graphical interface")

    def run(self, args):
        if args.gui:
            from edbob.wx.GenerateUuid import main
            main()
        else:
            print edbob.get_uuid()


def main(*args):
    """
    The primary entry point for the edbob command system.

    .. note::
       This entry point is really for ``edbob`` proper.  Your application
       should provide its own command entry point which leverages *your*
       :class:`Command` subclass instead of using this entry point (which uses
       :class:`Command` directly).

       There's not much involved in doing so; see the source code for
       implementation details.
    """

    if args:
        args = list(args)
    else:
        args = sys.argv[1:]

    cmd = Command()
    cmd.run(*args)

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
``edbob.configuration`` -- Configuration
"""

import os
import os.path
import sys
import ConfigParser
import logging
import logging.config

import edbob
from edbob import exceptions


__all__ = ['AppConfigParser']

log = logging.getLogger(__name__)


class AppConfigParser(ConfigParser.SafeConfigParser):
    """
    Subclass of ``ConfigParser.SafeConfigParser``, with some conveniences
    added.
    """

    def __init__(self, appname, *args, **kwargs):
        ConfigParser.SafeConfigParser.__init__(self, *args, **kwargs)
        self.appname = appname
        self.paths_attempted = []
        self.paths_loaded = []

    def clear(self):
        """
        Completely clears the contents of the config instance.
        """

        for section in self.sections():
            self.remove_section(section)
        del self.paths_attempted[:]
        del self.paths_loaded[:]

    def configure_logging(self):
        """
        Saves the current (possibly cascaded) configuration to a temporary
        file, and passes that to ``logging.config.fileConfig()``.
        """

        if self.getboolean('edbob', 'basic_logging', default=False):
            edbob.basic_logging()
        if self.getboolean('edbob', 'configure_logging', default=False):
            path = edbob.temp_path(suffix='.conf')
            self.save(path)
            try:
                logging.config.fileConfig(path, disable_existing_loggers=False)
            except ConfigParser.NoSectionError:
                pass
            os.remove(path)
        log.debug("Configured logging")

    def get(self, section, option, raw=False, vars=None, default=None):
        """
        Overridden version of ``ConfigParser.SafeConfigParser.get()``; this one
        adds the ``default`` keyword parameter and will return it instead of
        raising an error when the option doesn't exist.
        """

        if self.has_option(section, option):
            return ConfigParser.SafeConfigParser.get(self, section, option, raw, vars)
        return default

    def getboolean(self, section, option, default=None):
        """
        Overriddes base class method to allow for a default.
        """

        try:
            val = ConfigParser.SafeConfigParser.getboolean(self, section, option)
        except AttributeError:
            return default
        return val

    def get_dict(self, section):
        """
        Convenience method which returns a dictionary of options contained
        within the given section.
        """

        d = {}
        for opt in self.options(section):
            d[opt] = self.get(section, opt)
        return d

    def get_user_dir(self, create=False):
        """
        Returns a path to the "preferred" user-level folder, in which
        additional config files (etc.) may be placed as needed.  This
        essentially returns a platform-specific variation of ``~/.appname``.

        If ``create`` is ``True``, then the folder will be created if it does
        not already exist.
        """

        path = os.path.expanduser('~/.%s' % self.appname)
        if sys.platform == 'win32':
            from win32com.shell import shell, shellcon
            path = os.path.join(
                shell.SHGetSpecialFolderPath(0, shellcon.CSIDL_APPDATA),
                self.appname)
        if create and not os.path.exists(path):
            os.mkdir(path)
        return path

    def get_user_file(self, filename, create=False):
        """
        Returns a full path to a user-level config file location.  This is
        obtained by first calling :meth:`get_user_dir()` and then joining the
        result with ``filename``.

        The ``create`` argument will be passed directly to
        :meth:`get_user_dir()`, and may be used to ensure the user-level folder
        exists.
        """

        return os.path.join(self.get_user_dir(create=create), filename)

    def options(self, section):
        """
        Overridden version of ``ConfigParser.SafeConfigParser.options()``.
        This one doesn't raise an error if ``section`` doesn't exist, but
        instead returns an empty list.
        """

        if not self.has_section(section):
            return []
        return ConfigParser.SafeConfigParser.options(self, section)

    def read(self, paths, recurse=True):
        r"""
        .. highlight:: ini

        Overrides the ``RawConfigParser`` method by implementing the following
        logic:

        Prior to actually reading the contents of the file(s) specified by
        ``paths`` into the current config instance, a recursive algorithm will
        inspect the config found in the file(s) to see if additional config
        file(s) are to be included.  All config files, whether specified
        directly by ``paths`` or indirectly by way of primary configuration,
        are finally read into the current config instance in the proper order
        so that cascading works as expected.

        If you pass ``recurse=False`` to this method then none of the magical
        inclusion logic will happen at all.

        Note that when a config file indicates that another file(s) is to be
        included, the referenced file will be read into this config instance
        *before* the original (primary) file is read into it.  A convenient
        setup then could be to maintain a "site-wide" config file, shared on
        the network, including something like this::

           # //file-server/share/edbob/site.conf
           #
           # This file contains settings relevant to all machines on the
           # network.  Mail and logging configuration at least would be good
           # candidates for inclusion here.

           [edbob.mail]
           smtp.server = mail.example.com
           # smtp.username = user
           # smtp.password = pass
           sender.default = noreply@example.com
           recipients.default = ['tech-support@example.com']

           [loggers]
           keys = root, edbob

           # ...etc.  The bulk of logging configuration would go here.

        Then a config file local to a particular machine could look something
        like this::

           # C:\ProgramData\edbob\edbob.conf
           #
           # This file contains settings specific to the local machine.

           [edbob]
           include_config = [r'\\file-server\share\edbob\site.conf']

           # Add any local app config here, e.g. connection details for a
           # database, etc.

           # All logging config is inherited from the site-wide file, except
           # we'll override the output file location so that it remains local.
           # And maybe we need the level bumped up while we troubleshoot
           # something.

           [handler_file]
           args = (r'C:\ProgramData\edbob\edbob.log', 'a')

           [logger_edbob]
           level = DEBUG

        There is no right way to do this of course; the need should drive the
        method.  Since recursion is used, there is also no real limit to how
        you go about it.  A config file specific to a particular app on a
        particular machine can further include a config file specific to the
        local user on that machine, which in turn can include a file specific
        to the local machine generally, which could then include one or more
        site-wide files, etc.  Or the "most specific" (initially read; primary)
        config file could indicate which other files to include for every level
        of that, in which case recursion would be less necessary (though still
        technically used).
        """

        if isinstance(paths, basestring):
            paths = [paths]
        for path in paths:
            self.read_path(path, recurse=recurse)
        return self.paths_loaded

    def read_path(self, path, recurse=True):
        """
        .. highlight:: ini
        
        Reads a "single" config file into the instance.  If ``recurse`` is ``True``,
        *and* the config file references other "parent" config file(s), then the
        parent(s) are read also in recursive fashion.

        "Parent" config file paths may be specified in this way::
        
           [edbob]
           include_config = [
                r'\\file-server\share\edbob\site.conf',
                r'C:\ProgramData\edbob\special-stuff.conf',
                ]

        See :meth:`read()` for more information.
        """

        if path in self.paths_attempted:
            return

        self.paths_attempted.append(path)
        log.debug("Reading config file: %s" % path)
        if not os.path.exists(path):
            log.debug("File doesn't exist")
            return
        config = ConfigParser.SafeConfigParser(dict(
                here=os.path.abspath(os.path.dirname(path))))
        if not config.read(path):
            log.debug("Read failed")
            return
        include = None
        if recurse:
            if (config.has_section('edbob') and
                config.has_option('edbob', 'include_config')):
                include = config.get('edbob', 'include_config')
                if include:
                    for p in eval(include):
                        self.read_path(os.path.abspath(p))
        ConfigParser.SafeConfigParser.read(self, path)
        if include:
            self.remove_option('edbob', 'include_config')
        self.paths_loaded.append(path)
        log.info("Read config file: %s" % path)

    def read_service(self, service, paths):
        """
        "Special" version of :meth:`read()` which will first inspect the
        file(s) for a service-specific directive, the presence of which
        indicates the *true* config file to be used for the service.

        This method is pretty much a hack to get around certain limitations of
        Windows service implementations; it is not used otherwise.
        """

        config = ConfigParser.SafeConfigParser()
        config.read(paths)
        
        if (config.has_section('edbob.service_config')
            and config.has_option('edbob.service_config', service)):
            paths = eval(config.get('edbob.service_config', service))

        self.read(paths, recurse=True)

    def require(self, section, option, msg=None):
        """
        Convenience method which will raise an exception if the given option
        does not exist.  ``msg`` can be used to override (some of) the error
        text.
        """

        value = self.get(section, option)
        if value:
            return value
        raise exceptions.ConfigError(section, option, msg)

    def save(self, filename, create_dir=True):
        """
        Saves the current config contents to a file.  Optionally can create the
        parent folder(s) as necessary.
        """

        config_folder = os.path.dirname(filename)
        if create_dir and not os.path.exists(config_folder):
            os.makedirs(config_folder)
        config_file = open(filename, 'w')
        self.write(config_file)
        config_file.close()

    def set(self, section, option, value):
        """
        Overrides ``ConfigParser.SafeConfigParser.set()`` so that ``section``
        is created if it doesn't already exist, instead of raising an error.
        """

        if not self.has_section(section):
            self.add_section(section)
        ConfigParser.SafeConfigParser.set(self, section, option, value)


def default_system_paths(appname):
    r"""
    Returns a list of default system-level config file paths for the given
    ``appname``, according to ``sys.platform``.

    For example, assuming an app name of ``'rattail'``, the following would be
    returned:

    ``win32``:
       * ``<COMMON_APPDATA>\rattail.conf``
       * ``<COMMON_APPDATA>\rattail\rattail.conf``

    Any other platform:
       * ``/etc/rattail.conf``
       * ``/etc/rattail/rattail.conf``
       * ``/usr/local/etc/rattail.conf``
       * ``/usr/local/etc/rattail/rattail.conf``
    """

    if sys.platform == 'win32':
        from win32com.shell import shell, shellcon
        return [
            os.path.join(shell.SHGetSpecialFolderPath(
                    0, shellcon.CSIDL_COMMON_APPDATA), '%s.conf' % appname),
            os.path.join(shell.SHGetSpecialFolderPath(
                    0, shellcon.CSIDL_COMMON_APPDATA), appname, '%s.conf' % appname),
            ]

    return [
        '/etc/%s.conf' % appname,
        '/etc/%s/%s.conf' % (appname, appname),
        '/usr/local/etc/%s.conf' % appname,
        '/usr/local/etc/%s/%s.conf' % (appname, appname),
        ]


def default_user_paths(appname):
    r"""
    Returns a list of default user-level config file paths for the given
    ``appname``, according to ``sys.platform``.

    For example, assuming an app name of ``'rattail'``, the following would be
    returned:

    ``win32``:
       * ``<APPDATA>\rattail.conf``
       * ``<APPDATA>\rattail\rattail.conf``

    Any other platform:
       * ``~/.rattail.conf``
       * ``~/.rattail/rattail.conf``
    """

    if sys.platform == 'win32':
        from win32com.shell import shell, shellcon
        return [
            os.path.join(shell.SHGetSpecialFolderPath(
                    0, shellcon.CSIDL_APPDATA), '%s.conf' % appname),
            os.path.join(shell.SHGetSpecialFolderPath(
                    0, shellcon.CSIDL_APPDATA), appname, '%s.conf' % appname),
            ]

    return [
        os.path.expanduser('~/.%s.conf' % appname),
        os.path.expanduser('~/.%s/%s.conf' % (appname, appname)),
        ]

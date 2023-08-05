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


try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()


import sys
import os.path
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
execfile(os.path.join(here, 'edbob', '_version.py'))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()


requires = [
    #
    # Version numbers within comments below have specific meanings.
    # Basically the 'low' value is a "soft low," and 'high' a "soft high."
    # In other words:
    #
    # If either a 'low' or 'high' value exists, the primary point to be
    # made about the value is that it represents the most current (stable)
    # version available for the package (assuming typical public access
    # methods) whenever this project was started and/or documented.
    # Therefore:
    #
    # If a 'low' version is present, you should know that attempts to use
    # versions of the package significantly older than the 'low' version
    # may not yield happy results.  (A "hard" high limit may or may not be
    # indicated by a true version requirement.)
    #
    # Similarly, if a 'high' version is present, and especially if this
    # project has laid dormant for a while, you may need to refactor a bit
    # when attempting to support a more recent version of the package.  (A
    # "hard" low limit should be indicated by a true version requirement
    # when a 'high' version is present.)
    #
    # In any case, developers and other users are encouraged to play
    # outside the lines with regard to these soft limits.  If bugs are
    # encountered then they should be filed as such.
    #
    # package                           # low                   high

    'decorator',                        # 3.3.2
    'lockfile',                         # 0.9.1
    'progressbar',                      # 2.3
    'pytz',                             # 2012b
    ]

if sys.version_info < (2, 7):
    # Python < 2.7 has a standard library in need of supplementation.

    requires += [
        #
        # package                       # low                   high

        'argparse',                     # 1.2.1
        'ordereddict',                  # 1.1
        ]

    
extras = {

    'db': [
        #
        # package                       # low                   high

        'alembic',                      # 0.3.1
        'SQLAlchemy',                   # 0.7.6
        # 'Tempita',                      # 0.5.1
        ],

    'docs': [
        #
        # package                       # low                   high

        'Sphinx',                       # 1.1.3
        ],

    'filemon': [
        #
        # package                       # low                   high

        # This is just a placeholder on Windows; Linux requires this extra.
        ],

    'pyramid': [
        #
        # package                       # low                   high

        # Beaker dependency included here because 'pyramid_beaker' uses incorrect
        # case in its requirement declaration.
        'Beaker',                       # 1.6.3

        # Pyramid 1.3 introduced 'pcreate' command (and friends) to replace
        # deprecated 'paster create' (and friends).
        'pyramid>=1.3a1',               #                       1.3b2

        'FormAlchemy',                  # 1.4.2
        'FormEncode',                   # 1.2.4
        'Mako',                         # 0.6.2
        'pyramid_beaker>=0.6',          #                       0.6.1
        'pyramid_debugtoolbar',         # 1.0
        'pyramid_exclog',               # 0.6
        'pyramid_simpleform',           # 0.6.1
        'pyramid_tm',                   # 0.3
        # 'Tempita',                      # 0.5.1
        'transaction',                  # 1.2.0
        'waitress',                     # 0.8.1
        'WebHelpers',                   # 1.3
        'zope.sqlalchemy',              # 0.7
        ],
    }

if sys.platform == 'win32':

    extras['db'] += [
        #
        # package                       # low                   high

        'py-bcrypt-w32',                # 0.2.2
        ]

    extras['pyramid'] += [
        #
        # package                       # low                   high

        'py-bcrypt-w32',                # 0.2.2
        ]

elif sys.platform == 'linux2':

    extras['db'] += [
        #
        # package                       # low                   high

        'py-bcrypt',                    # 0.2
        ]

    extras['filemon'] += [
        #
        # package                       # low                   high

        'pyinotify',                    # 0.9.3
        ]

    extras['pyramid'] += [
        #
        # package                       # low                   high

        'py-bcrypt',                    # 0.2
        ]


setup(
    name = "edbob",
    version = __version__,
    author = "Lance Edgar",
    author_email = "lance@edbob.org",
    url = "http://edbob.org/",
    license = "GNU Affero GPL v3",
    description = "Pythonic Software Framework",
    long_description = README + '\n\n' +  CHANGES,

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

    install_requires = requires,
    extras_require = extras,

    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,

    entry_points = """

[console_scripts]
edbob = edbob.commands:main

[gui_scripts]
edbobw = edbob.commands:main

[pyramid.scaffold]
edbob = edbob.scaffolds:Template

[edbob.commands]
db = edbob.commands:DatabaseCommand
filemon = edbob.commands:FileMonitorCommand
shell = edbob.commands:ShellCommand
uuid = edbob.commands:UuidCommand

[edbob.db.extensions]
auth = edbob.db.extensions.auth:AuthExtension
contact = edbob.db.extensions.contact:ContactExtension

""",
    )

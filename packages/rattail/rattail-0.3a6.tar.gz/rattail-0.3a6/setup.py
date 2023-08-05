#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################


import os.path
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
execfile(os.path.join(here, 'rattail', '_version.py'))
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

    'edbob[filemon]>=0.1a14',           #                       0.1a15.dev
    ]


setup(
    name = "rattail",
    version = __version__,
    author = "Lance Edgar",
    author_email = "lance@edbob.org",
    url = "http://rattail.edbob.org/",
    license = "GNU Affero GPL v3",
    description = "Retail Software Framework",
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
        'Topic :: Office/Business',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

    install_requires = requires,

    namespace_packages = ['rattail'],
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,

    entry_points = """

[console_scripts]
rattail = rattail.commands:main

[gui_scripts]
rattailw = rattail.commands:main

[edbob.db.extensions]
rattail = rattail.db.extension:RattailExtension

[rattail.commands]
dbsync = rattail.commands:DatabaseSyncCommand
filemon = rattail.commands:FileMonitorCommand
load-host-data = rattail.commands:LoadHostDataCommand

[rattail.batches.providers]
print_labels = rattail.batches.providers.labels:PrintLabels

[rattail.sil.column_providers]
rattail = rattail.sil.columns:provide_columns

""",
    )

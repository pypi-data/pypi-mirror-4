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

"""
``rattail.commands`` -- Commands
"""

import sys

from edbob import commands

import rattail


class Command(commands.Command):
    """
    The primary command for Rattail.
    """
    
    name = 'rattail'
    version = rattail.__version__
    description = "Retail Software Framework"
    long_description = """
Rattail is a retail software framework.

Copyright (c) 2010-2012 Lance Edgar <lance@edbob.org>

This program comes with ABSOLUTELY NO WARRANTY.  This is free software,
and you are welcome to redistribute it under certain conditions.
See the file COPYING.txt for more information.
"""


class FileMonitorCommand(commands.FileMonitorCommand):
    """
    Interacts with the file monitor service; called as ``rattail filemon``.

    See :class:`edbob.commands.FileMonitorCommand` for more information.
    """

    appname = 'rattail'

    def get_win32_module(self):
        from rattail import filemon
        return filemon

    def get_win32_service(self):
        from rattail.filemon import RattailFileMonitor
        return RattailFileMonitor


class InitCommand(commands.Subcommand):
    """
    Initializes the database; called as ``{{package}} initialize``.  This is
    meant to be leveraged as part of setting up the application.  The database
    used by this command will be determined by config, for example::

    .. highlight:: ini

       [edbob.db]
       sqlalchemy.url = postgresql://user:pass@localhost/{{package}}
    """

    name = 'initialize'
    description = "Initialize the database"

    def run(self, args):
        from edbob.db import engine
        from edbob.db.util import install_core_schema
        from edbob.db.exceptions import CoreSchemaAlreadyInstalled
        from edbob.db.extensions import activate_extension

        # Install core schema to database.
        try:
            install_core_schema(engine)
        except CoreSchemaAlreadyInstalled, err:
            print '%s:' % err
            print '  %s' % engine.url
            return

        # Activate any extensions you like here...
        # activate_extension('shrubbery')

        # Okay, on to bootstrapping...

        from edbob.db import Session
        from edbob.db.classes import Role, User
        from edbob.db.auth import administrator_role

        session = Session()

        # Create 'admin' user with full rights.
        admin = User(username='admin', password='admin')
        admin.roles.append(administrator_role(session))
        session.add(admin)

        # Do any other bootstrapping you like here...
        
        session.commit()
        session.close()
        
        print "Initialized database:"
        print '  %s' % engine.url


def main(*args):
    """
    The primary entry point for the Rattail command system.
    """

    if args:
        args = list(args)
    else:
        args = sys.argv[1:]

    cmd = Command()
    cmd.run(*args)

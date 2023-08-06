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

import edbob
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


class DatabaseSyncCommand(commands.Subcommand):
    """
    Interacts with the database synchronization service; called as ``rattail
    dbsync``.
    """

    name = 'dbsync'
    description = "Manage the database synchronization service"

    def add_parser_args(self, parser):
        subparsers = parser.add_subparsers(title='subcommands')

        start = subparsers.add_parser('start', help="Start service")
        start.set_defaults(subcommand='start')
        stop = subparsers.add_parser('stop', help="Stop service")
        stop.set_defaults(subcommand='stop')

    def run(self, args):
        from rattail.db.sync import linux as dbsync

        if args.subcommand == 'start':
            dbsync.start_daemon()

        elif args.subcommand == 'stop':
            dbsync.stop_daemon()


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


class LoadHostDataCommand(commands.Subcommand):
    """
    Loads data from the Rattail host database, if one is configured.
    """

    name = 'load-host-data'
    description = "Load data from host database"

    def run(self, args):
        from edbob.console import Progress
        from rattail.db import load

        edbob.init_modules(['edbob.db'])

        if 'host' not in edbob.engines:
            print "Host engine URL not configured."
            return

        proc = load.LoadProcessor()
        proc.load_all_data(edbob.engines['host'], Progress)


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

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
``rattail.db.sync.linux`` -- Database Synchronization for Linux
"""

from edbob.daemon import Daemon

from rattail.db.sync import get_sync_engines, synchronize_changes


class SyncDaemon(Daemon):

    def run(self):
        engines = get_sync_engines()
        if engines:
            synchronize_changes(engines)


def get_daemon():
    return SyncDaemon('/tmp/rattail_dbsync.pid')


def start_daemon():
    get_daemon().start()


def stop_daemon():
    get_daemon().stop()

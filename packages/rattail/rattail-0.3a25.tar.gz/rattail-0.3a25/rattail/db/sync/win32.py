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
``rattail.db.sync.win32`` -- Database Synchronization for Windows
"""

import sys
import logging
import threading

import edbob
from edbob.win32 import Service

from rattail.db.sync import get_sync_engines, synchronize_changes


log = logging.getLogger(__name__)


class DatabaseSynchronizerService(Service):
    """
    Implements database synchronization as a Windows service.
    """

    _svc_name_ = 'RattailDatabaseSynchronizer'
    _svc_display_name_ = "Rattail : Database Synchronization Service"
    _svc_description_ = ("Monitors the local Rattail database for changes, "
                         "and synchronizes them to the configured remote "
                         "database(s).")

    appname = 'rattail'

    def Initialize(self):
        """
        Service initialization.
        """

        if not Service.Initialize(self):
            return False

        edbob.init_modules(['rattail.db'])

        engines = get_sync_engines()
        if not engines:
            return False

        thread = threading.Thread(target=synchronize_changes,
                                  args=(engines,))
        thread.daemon = True
        thread.start()

        return True


if __name__ == '__main__':
    if sys.platform == 'win32':
        import win32serviceutil
        win32serviceutil.HandleCommandLine(DatabaseSynchronizerService)

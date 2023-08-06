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
``rattail.palm`` -- Palm OS Application Interface
"""

import os
import os.path
import socket
import getpass
import datetime
import logging

import edbob

import rattail
from rattail.csvutil import DictWriter

# Hack for docs' sake (building on Linux).
try:
    import pythoncom
except ImportError:
    pythoncom = object()
    pythoncom.CLSCTX_LOCAL_SERVER = 4


log = logging.getLogger(__name__)


class PalmConduit(object):
    """
    Implements a conduit for Palm's Hotsync Manager.
    """

    _reg_clsid_ = '{F2FDDEEC-254F-42C3-8801-C41E8A243F13}'
    _reg_progid_ = 'Rattail.PalmConduit'
    _reg_desc_ = "Rattail Conduit for Palm Hotsync Manager"

    # Don't let pythoncom guess this, for several reasons.  This way Python
    # will go about determining its path etc. as normal, and __name__ will be
    # "rattail.palm" instead of just "palm".
    _reg_class_spec_ = 'rattail.palm.PalmConduit'

    # Don't let Hotsync Manager run our code in-process, so that we may launch
    # wxPython dialogs as needed for configuration etc.
    _reg_clsctx_ = pythoncom.CLSCTX_LOCAL_SERVER

    _typelib_guid_ = '{6FD7A7A0-FA1F-11D2-AC32-006008E3F0A2}'
    _typelib_version_ = 1, 0
    _com_interfaces_ = ['IPDClientNotify']

    _public_methods_ = ['BeginProcess', 'CfgConduit',
                        'ConfigureConduit', 'GetConduitInfo']

    def BeginProcess(self):
        """
        Called by Hotsync Manager when synchronization is ready to happen.
        This method implements the actual data sync.
        """

        from win32com.client import Dispatch

        edbob.init('rattail')
        data_dir = edbob.config.require('rattail.palm', 'collection_dir')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        db_query = Dispatch('PDDirect.PDDatabaseQuery')
        db = db_query.OpenRecordDatabase('Rattail_Scan', 'PDDirect.PDRecordAdapter')
        if db.RecordCount:
            
            sys_adapter = Dispatch('PDDirect.PDSystemAdapter')
            fname = '%s,%s,%s,%s.csv' % (socket.gethostname(), getpass.getuser(),
                                         sys_adapter.PDUserInfo.UserName,
                                         datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S'))
            data_path = os.path.join(data_dir, fname)
            log.info("PalmConduit.BeginProcess: writing %u handheld records to file: %s" %
                     (db.RecordCount, data_path))

            data_file = open(data_path, 'wb')
            writer = DictWriter(data_file, ['upc', 'cases', 'units'])
            writer.writeheader()
            for i in range(db.RecordCount):
                rec, unique_id, category, attrs = db.ReadByIndex(i)

                writer.writerow({
                        'upc': rec[:15].rstrip('\x00'),
                        'cases': rec[15:19].rstrip('\x00'),
                        'units': rec[19:23].rstrip('\x00'),
                        })

            data_file.close()

            log.info("PalmConduit.BeginProcess: removing all records from handheld")
            db.RemoveSet(0)
            log.info("PalmConduit.BeginProcess: done")

        else:
            log.info("PalmConduit.BeginProcess: nothing to do")

        return False

    def CfgConduit(self, nCreatorId, nUserId, bstrUserName, bstrPathName,
                   nSyncPerm, nSyncTemp, nSyncNew, nSyncPref):
        pass

    def ConfigureConduit(self, pPathName, pRegistry, nSyncPref, nSyncType):
        pass

    def GetConduitInfo(self, infoType, dwCreatorID, dwUserID, bstrUsername):
        return None


def register_conduit():
    """
    Registers the conduit with Palm Hotsync Manager.
    """

    import pywintypes
    from win32com.client import Dispatch

    conduit_mgr = Dispatch('PDStandard.PDSystemCondMgr')
    creator_id = conduit_mgr.StringToCreatorID('RTTL')
    assert creator_id

    try:
        info = conduit_mgr.GetConduitInfo(creator_id)
    except pywintypes.com_error:
        pass
    else:
        return # already registered

    info = Dispatch('PDStandard.PDConduitInfo')
    info.COMClassID = 'Rattail.PalmConduit'
    info.CreatorID = creator_id
    info.DesktopDataDirectory = 'Rattail'
    info.DisplayName = 'Rattail'
    conduit_mgr.RegisterConduit(info)


def unregister_conduit():
    """
    Unregisters the conduit from Hotsync Manager.
    """

    from win32com.client import Dispatch

    conduit_mgr = Dispatch('PDStandard.PDSystemCondMgr')
    creator_id = conduit_mgr.StringToCreatorID('RTTL')
    assert creator_id
    conduit_mgr.UnregisterConduit(creator_id)

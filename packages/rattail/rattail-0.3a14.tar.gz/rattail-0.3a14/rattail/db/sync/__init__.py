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
``rattail.db.sync`` -- Database Synchronization
"""

import sys
import time
import logging

if sys.platform == 'win32':
    import win32api

from sqlalchemy.orm import class_mapper

import edbob

import rattail


log = logging.getLogger(__name__)


def get_sync_engines():
    edbob.init_modules(['edbob.db'])

    keys = edbob.config.get('rattail.db', 'syncs')
    if not keys:
        return None

    engines = {}
    for key in keys.split(','):
        key = key.strip()
        engines[key] = edbob.engines[key]
    log.info("get_sync_engines: Found engine keys: %s" % ','.join(engines.keys()))
    return engines


def dependency_sort(x, y):
    map_x = class_mapper(getattr(edbob, x))
    map_y = class_mapper(getattr(edbob, y))

    dep_x = []
    table_y = map_y.tables[0].name
    for column in map_x.columns:
        for key in column.foreign_keys:
            if key.column.table.name == table_y:
                return 1
            dep_x.append(key)

    dep_y = []
    table_x = map_x.tables[0].name
    for column in map_y.columns:
        for key in column.foreign_keys:
            if key.column.table.name == table_x:
                return -1
            dep_y.append(key)

    if dep_x and not dep_y:
        return 1
    if dep_y and not dep_x:
        return -1
    return 0


def merge_instance(instance, session):
    """
    Merge ``instance`` into ``session``.

    This function is somewhat of a hack, in order to properly handle
    :class:`rattail.Product` instances and the independent nature of the
    related :class:`rattail.ProductPrice` instances.
    """

    if not isinstance(instance, rattail.Product):
        return session.merge(instance)

    product = session.merge(instance)
    product.regular_price_uuid = None
    product.current_price_uuid = None
    if instance.regular_price_uuid:
        product.regular_price = session.merge(instance.regular_price)
    if instance.current_price_uuid:
        product.current_price = session.merge(instance.current_price)
    return product


def synchronize_changes(engines):

    log.info("synchronize_changes: Using engine keys: %s" % ','.join(engines.keys()))

    while True:
        local_session = edbob.Session()
        local_changes = local_session.query(rattail.Change)

        if local_changes.count():
            log.debug("synchronize_changes: found %d changes" % local_changes.count())

            class_names = []
            for class_name in local_session.query(rattail.Change.class_name.distinct()):
                class_names.append(class_name[0])
            class_names.sort(cmp=dependency_sort)

            remote_sessions = []
            for remote_engine in engines.itervalues():
                remote_sessions.append(
                    edbob.Session(bind=remote_engine))

            for class_name in class_names:

                for change in local_changes.filter_by(class_name=class_name):
                    log.debug("synchronize_changes: processing change: %s" % change)
                    cls = getattr(edbob, change.class_name)

                    if change.deleted:
                        for remote_session in remote_sessions:
                            remote_instance = remote_session.query(cls).get(change.uuid)
                            if remote_instance:
                                remote_session.delete(remote_instance)
                                remote_session.flush()

                    else: # new/dirty
                        local_instance = local_session.query(cls).get(change.uuid)
                        if local_instance:
                            for remote_session in remote_sessions:
                                merge_instance(local_instance, remote_session)
                                remote_session.flush()

                    local_session.delete(change)
                    local_session.flush()

            for remote_session in remote_sessions:
                remote_session.commit()
                remote_session.close()
            local_session.commit()

        local_session.close()
        if sys.platform == 'win32':
            win32api.Sleep(3000)
        else:
            time.sleep(3)

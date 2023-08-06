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

import sqlalchemy.exc
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


class Synchronizer(object):
    """
    Default implementation of database synchronization logic.  Subclass this if
    you have special processing needs.
    """

    def synchronize_changes(self, engines):

        log.info("synchronize_changes: Using engine keys: %s" % ','.join(engines.keys()))

        while True:
            try:
                local_session = edbob.Session()
                local_changes = local_session.query(rattail.Change)

                if local_changes.count():
                    log.debug("synchronize_changes: found %d changes" % local_changes.count())

                    # First we must determine which types of instances are in need of
                    # syncing.  The order will matter because of class dependencies.
                    # However the dependency_sort() call doesn't *quite* take care of
                    # everything - notably the Product/ProductPrice situation.  Since
                    # those classes are mutually dependent, we start with a hackish
                    # lexical sort and hope for the best...
                    q = local_session.query(rattail.Change.class_name.distinct())
                    q = q.order_by('class_name')
                    class_names = [x[0] for x in q]
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
                                        self.delete_instance(remote_session, remote_instance)
                                        remote_session.flush()

                            else: # new/dirty
                                local_instance = local_session.query(cls).get(change.uuid)
                                if local_instance:
                                    for remote_session in remote_sessions:
                                        self.merge_instance(remote_session, local_instance)
                                        remote_session.flush()

                            local_session.delete(change)
                            local_session.flush()

                    for remote_session in remote_sessions:
                        remote_session.commit()
                        remote_session.close()
                    local_session.commit()

                local_session.close()
                self.sleep(3)

            except sqlalchemy.exc.OperationalError, error:
                if error.connection_invalidated:
                    # Presumably a database server restart; give it a moment
                    # and try again.
                    self.sleep(5)
                else:
                    raise

    def sleep(self, seconds):
        if sys.platform == 'win32':
            win32api.Sleep(seconds * 1000)
        else:
            time.sleep(seconds)

    def merge_instance(self, session, instance):
        """
        Merge ``instance`` into ``session``.

        This method checks for other "special" methods based on the class of
        ``instance``.  If such a method is found, it is invoked; otherwise a
        simple merge is done.
        """

        cls = instance.__class__.__name__
        if hasattr(self, 'merge_%s' % cls):
            return getattr(self, 'merge_%s' % cls)(session, instance)

        return session.merge(instance)

    def merge_Product(self, session, source_product):
        """
        This method is somewhat of a hack, in order to properly handle
        :class:`rattail.Product` instances and the interdependent nature of the
        related :class:`rattail.ProductPrice` instances.
        """

        target_product = session.merge(source_product)

        # I'm not 100% sure I understand this correctly, but here's my
        # thinking: First we clear the price relationships in case they've
        # actually gone away; then we re-establish any which are currently
        # valid.

        # Setting the price relationship attributes to ``None`` isn't enough to
        # force the ORM to notice a change, since the UUID field is ultimately
        # what it's watching.  So we must explicitly use that field here.
        target_product.regular_price_uuid = None
        target_product.current_price_uuid = None

        # If the source instance has currently valid price relationships, then
        # we re-establish them.  We must merge the source price instance in
        # order to be certain it will exist in the target session, and avoid
        # foreign key errors.  However we *still* must also set the UUID fields
        # because again, the ORM is watching those...  This was noticed to be
        # the source of some bugs where successive database syncs were
        # effectively "toggling" the price relationship.  Setting the UUID
        # field explicitly seems to solve it.
        if source_product.regular_price_uuid:
            target_product.regular_price = session.merge(source_product.regular_price)
            target_product.regular_price_uuid = target_product.regular_price.uuid
        if source_product.current_price_uuid:
            target_product.current_price = session.merge(source_product.current_price)
            target_product.current_price_uuid = target_product.current_price.uuid

        return target_product

    def delete_instance(self, session, instance):
        """
        Delete ``instance`` using ``session``.

        This method checks for other "special" methods based on the class of
        ``instance``.  If such a method is found, it is invoked before the
        instance is officially deleted from ``session``.
        """

        cls = instance.__class__.__name__
        if hasattr(self, 'delete_%s' % cls):
            getattr(self, 'delete_%s' % cls)(session, instance)

        session.delete(instance)

    def delete_Department(self, session, department):

        # Remove association from Subdepartment records.
        q = session.query(rattail.Subdepartment)
        q = q.filter(rattail.Subdepartment.department == department)
        for subdepartment in q:
            subdepartment.department = None

        # Remove association from Product records.
        q = session.query(rattail.Product)
        q = q.filter(rattail.Product.department == department)
        for product in q:
            product.department = None

    def delete_Subdepartment(self, session, subdepartment):

        # Remove association from Product records.
        q = session.query(rattail.Product)
        q = q.filter(rattail.Product.subdepartment == subdepartment)
        for product in q:
            product.subdepartment = None

    def delete_Vendor(self, session, vendor):

        # Remove associated ProductCost records.
        q = session.query(rattail.ProductCost)
        q = q.filter(rattail.ProductCost.vendor == vendor)
        for cost in q:
            session.delete(cost)


def synchronize_changes(engines):
    """
    This function will instantiate a ``Synchronizer`` class according to
    configuration.  (The default class is :class:`Synchronizer`.)  This
    instance is then responsible for implementing the sync logic.

    .. highlight:: ini

    If you need to override the default synchronizer class, put something like
    the following in your config file::

       [rattail.db]
       sync.synchronizer_class = myapp.sync:MySynchronizer
    """

    cls = edbob.config.get('rattail.db', 'sync.synchronizer_class')
    if cls:
        cls = edbob.load_spec(cls)
    else:
        cls = Synchronizer
    sync = cls()

    sync.synchronize_changes(engines)

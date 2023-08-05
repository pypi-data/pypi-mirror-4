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
``rattail.db`` -- Database Stuff
"""

import logging
import warnings

from sqlalchemy.event import listen
from sqlalchemy.orm import object_mapper, RelationshipProperty

import edbob

import rattail


ignore_role_changes = None

log = logging.getLogger(__name__)


def before_flush(session, flush_context, instances):
    """
    Listens for session flush events.  This function is responsible for adding
    stub records to the 'changes' table, which will in turn be used by the
    database synchronizer.
    """

    def record_change(instance, deleted=False):

        # No need to record changes for Change. :)
        if isinstance(instance, rattail.Change):
            return

        # No need to record changes for batch data.
        if isinstance(instance, (rattail.Batch,
                                 rattail.BatchColumn,
                                 rattail.BatchRow)):
            return

        # Ignore instances which don't use UUID.
        if not hasattr(instance, 'uuid'):
            return

        # Ignore Role instances, if so configured.
        if ignore_role_changes and isinstance(instance, edbob.Role):
            return

        # Provide an UUID value, if necessary.
        if not instance.uuid:

            # If the 'uuid' column is actually a foreign key to another
            # table...well, then we can't just generate a new value for it.
            # Instead we must traverse the relationship and fetch the existing
            # foreign key value...

            mapper = object_mapper(instance)
            uuid = mapper.columns['uuid']
            if uuid.foreign_keys:

                for prop in mapper.iterate_properties:
                    if (isinstance(prop, RelationshipProperty)
                        and len(prop.remote_side) == 1
                        and prop.remote_side[0].key == 'uuid'):

                        instance.uuid = getattr(instance, prop.key).uuid
                        break
                assert instance.uuid

            # ...but if there is no foreign key, just generate a new UUID.
            else:
                instance.uuid = edbob.get_uuid()

        # Record the change.
        change = session.query(rattail.Change).get(
            (instance.__class__.__name__, instance.uuid))
        if not change:
            change = rattail.Change(
                class_name=instance.__class__.__name__,
                uuid=instance.uuid)
            session.add(change)
        change.deleted = deleted
        log.debug("before_flush: recorded change: %s" % repr(change))

    for instance in session.deleted:
        log.debug("before_flush: deleted instance: %s" % repr(instance))
        record_change(instance, deleted=True)

    for instance in session.new:
        log.debug("before_flush: new instance: %s" % repr(instance))
        record_change(instance)

    for instance in session.dirty:
        if session.is_modified(instance, passive=True):
            log.debug("before_flush: dirty instance: %s" % repr(instance))
            record_change(instance)


def record_changes(session):
    listen(session, 'before_flush', before_flush)


def init(config):
    """
    Initialize the Rattail database framework.
    """

    from rattail.db.extension import model
    edbob.graft(rattail, model)

    from rattail.db.extension import enum
    edbob.graft(rattail, enum)

    global ignore_role_changes
    ignore_role_changes = config.getboolean(
        'rattail.db', 'changes.ignore_roles', default=True)

    if config.getboolean('rattail.db', 'changes.record'):
        record_changes(edbob.Session)

    elif config.getboolean('rattail.db', 'record_changes'):
        warnings.warn("Config setting 'record_changes' in section [rattail.db] "
                      "is deprecated; please use 'changes.record' instead.",
                      DeprecationWarning)
        record_changes(edbob.Session)

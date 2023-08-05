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

from sqlalchemy.event import listen

import edbob

import rattail


log = logging.getLogger(__name__)


def before_flush(session, flush_context, instances):
    """
    Listens for session flush events.  This function is responsible for adding
    stub records to the 'changes' table, which will in turn be used by the
    database synchronizer.
    """

    def record_change(instance, deleted=False):
        if instance.__class__ is rattail.Change:
            return
        if not hasattr(instance, 'uuid'):
            return
        if not instance.uuid:
            instance.uuid = edbob.get_uuid()
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

    if config.get('rattail.db', 'record_changes') == 'True':
        record_changes(edbob.Session)

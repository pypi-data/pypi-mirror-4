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
``rattail.db.batches.types`` -- Batch Types
"""

import datetime
import pkg_resources

from edbob.time import local_time

from rattail.exceptions import BatchTypeNotFound


__all__ = ['get_batch_type', 'BatchType']


batch_types = None


def get_batch_type(name):
    global batch_types
    if batch_types is None:
        batch_types = {}
        for entrypoint in pkg_resources.iter_entry_points('rattail.batches.types'):
            batch_types[entrypoint.name] = entrypoint.load()
    if name in batch_types:
        return batch_types[name]()
    raise BatchTypeNotFound(name)


class BatchType(object):

    name = None
    description = None
    source = None
    destination = None
    action_type = None

    purge_date_offset = None

    def initialize(self, batch):
        batch.provider = self.name
        batch.description = self.description
        batch.source = self.source
        batch.destination = self.destination
        batch.action_type = self.action_type
        self.set_purge_date(batch)
        self.add_columns(batch)

    def set_purge_date(self, batch):
        if self.purge_date_offset is not None:
            today = local_time().date()
            purge_offset = datetime.timedelta(days=self.purge_date_offset)
            batch.purge = today + purge_offset

    def add_columns(self, batch):
        raise NotImplementedError


# class LabelsBatchType(BatchType):

#     name = 'labels'
#     description = "Print Labels"

#     def add_columns(self, batch):
#         batch.add_column('F01')
#         batch.add_column('F155')
#         batch.add_column('F02')
#         batch.add_column('F22', display_name="Size")
#         batch.add_column('F95', display_name="Label")
#         batch.add_column('F94', display_name="Quantity")

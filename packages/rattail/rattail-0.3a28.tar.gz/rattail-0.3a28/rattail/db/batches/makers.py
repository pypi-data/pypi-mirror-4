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
``rattail.db.batches.makers`` -- Batch Makers
"""

from rattail.db.batches.types import get_batch_type
from rattail.db.batches.data import BatchDataProvider
# from rattail.db.model import Batch, LabelProfile
from rattail.db.extension.model import Batch
from rattail.sil import consume_batch_id


class BatchMaker(object):

    progress_message = "Making batch(es)"

    def __init__(self, session, source=None):
        self.session = session
        self.source = source
        self.batches = {}

    def get_batch(self, name):
        if name not in self.batches:
            self.batches[name] = self.make_batch(name)
        return self.batches[name]

    def make_batch(self, name):
        if hasattr(self, 'make_batch_%s' % name):
            batch = getattr(self, 'make_batch_%s' % name)()

        else:
            batch_type = get_batch_type(name)
            batch = Batch()
            batch_type.initialize(batch)
            if self.source:
                batch.source = self.source
            batch.id = consume_batch_id()

        self.session.add(batch)
        self.session.flush()
        batch.create_table()
        return batch

    def make_batches_begin(self, data):
        pass

    def make_batches(self, data, progress=None):
        if not isinstance(data, BatchDataProvider):
            raise TypeError("Sorry, you must pass a BatchDataProvider instance")

        result = self.make_batches_begin(data)
        if result is not None and not result:
            return False

        prog = None
        if progress and len(data):
            prog = progress(self.progress_message, len(data))

        cancel = False
        for i, data_row in enumerate(data, 1):
            self.process_data_row(data_row)
            if prog and not prog.update(i):
                cancel = True
                break
            self.session.flush()

        if prog:
            prog.destroy()

        if not cancel:
            result = self.make_batches_end()
            if result is not None:
                cancel = not result

        return not cancel

    def make_batches_end(self):
        pass

    def process_data_row(self, data_row):
        raise NotImplementedError


# class LabelsBatchMaker(BatchMaker):

#     default_profile = None
#     default_quantity = 1

#     def make_batches_begin(self, data):
#         if not self.default_profile:
#             q = self.session.query(LabelProfile)
#             q = q.order_by(LabelProfile.ordinal)
#             self.default_profile = q.first()
#             assert self.default_profile

#     def process_data_row(self, data_row):
#         batch = self.get_batch('labels')
#         row = batch.rowclass()
#         row.F01 = data_row.F01
#         row.F155 = data_row.F155
#         row.F02 = data_row.F02
#         row.F22 = data_row.F22
#         row.F95 = self.default_profile.code
#         row.F94 = self.default_quantity
#         batch.add_row(row)        

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
``rattail.db.batches.executors`` -- Batch Executors
"""

import pkg_resources

from sqlalchemy.orm import object_session

# from rattail.db.model import LabelProfile, Product
from rattail.exceptions import BatchExecutorNotFound, BatchTypeNotSupported


__all__ = ['get_batch_executor', 'BatchExecutor']


batch_executors = None


def get_batch_executor(name):
    global batch_executors
    if batch_executors is None:
        batch_executors = {}
        for entrypoint in pkg_resources.iter_entry_points('rattail.batches.executors'):
            batch_executors[entrypoint.name] = entrypoint.load()
    if name in batch_executors:
        return batch_executors[name]()
    raise BatchExecutorNotFound(name)


class BatchExecutor(object):

    batch_type = None

    def execute(self, batch, progress=None):
        # if batch.type != self.batch_type:
        #     raise BatchTypeNotSupported(self, batch.type)
        session = object_session(batch)
        return self.execute_batch(session, batch, progress)

    def execute_batch(self, session, batch, progress=None):
        raise NotImplementedError


# class LabelsBatchExecutor(BatchExecutor):

#     batch_type = 'labels'

#     def execute_batch(self, session, batch, progress=None):
#         prog = None
#         if progress:
#             prog = progress("Loading product data", batch.rowcount)

#         profiles = {}

#         cancel = False
#         for i, row in enumerate(batch.rows, 1):

#             profile = profiles.get(row.F95)
#             if not profile:
#                 q = session.query(LabelProfile)
#                 q = q.filter(LabelProfile.code == row.F95)
#                 profile = q.one()
#                 profile.labels = []
#                 profiles[row.F95] = profile

#             q = session.query(Product)
#             q = q.filter(Product.upc == row.F01)
#             product = q.one()

#             profile.labels.append((product, row.F94))
#             if prog and not prog.update(i):
#                 cancel = True
#                 break

#         if not cancel:
#             for profile in profiles.itervalues():
#                 printer = profile.get_printer()
#                 assert printer
#                 if not printer.print_labels(profile.labels):
#                     cancel = True
#                     break

#         if prog:
#             prog.destroy()
#         return not cancel

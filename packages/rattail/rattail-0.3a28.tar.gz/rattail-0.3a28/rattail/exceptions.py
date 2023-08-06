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
``rattail.exceptions`` -- Exceptions
"""


class RattailError(Exception):
    """
    Base class for all Rattail exceptions.
    """


class BatchError(RattailError):
    """
    Base class for all batch-related errors.
    """


class BatchTypeNotFound(BatchError):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Batch type not found: %s" % self.name

    
class BatchTypeNotSupported(BatchError):
    """
    Raised when a :class:`rattail.db.batches.BatchExecutor` instance is asked
    to execute a batch, but the batch is of an unsupported type.
    """

    def __init__(self, executor, batch_type):
        self.executor = executor
        self.batch_type = batch_type

    def __str__(self):
        return "Batch type '%s' is not supported by executor: %s" % (
            self.batch_type, repr(self.executor))


class BatchExecutorNotFound(BatchError):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Batch executor not found: %s" % self.name

    
class LabelPrintingError(Exception):

    pass

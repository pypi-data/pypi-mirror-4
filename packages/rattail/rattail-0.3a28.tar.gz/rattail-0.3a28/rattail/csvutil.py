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
``rattail.csvutil`` -- CSV File Utilities

Contains various utilities relating to CSV file processing.

.. note::
   This module is named ``csvutil`` instead of ``csv`` primarily as a
   workaround to the problem of ``PythonService.exe`` insisting on doing
   relative imports.
"""

import csv


class DictWriter(csv.DictWriter):
    """
    Convenience class which derives from the standard ``csv.DictWriter``.  This
    currently exists only to provide the :meth:`writeheader()` method.
    """

    def writeheader(self):
        """
        Provide a ``writeheader()`` method in case the ``csv`` library in use
        doesn't (i.e. for Python < 2.7).
        """

        if hasattr(csv.DictWriter, 'writeheader'):
            return csv.DictWriter.writeheader(self)
        self.writerow(self.fieldnames)

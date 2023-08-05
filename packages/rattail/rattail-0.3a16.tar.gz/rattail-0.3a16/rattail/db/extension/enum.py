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
``rattail.db.extension.enum`` -- Enumerations
"""


EMPLOYEE_STATUS_CURRENT         = 1
EMPLOYEE_STATUS_FORMER          = 2

EMPLOYEE_STATUS = {
    EMPLOYEE_STATUS_CURRENT     : "current",
    EMPLOYEE_STATUS_FORMER      : "former",
    }


# VENDOR_CATALOG_NOT_PARSED       = 1
# VENDOR_CATALOG_PARSED           = 2
# VENDOR_CATALOG_COGNIZED         = 3
# VENDOR_CATALOG_PROCESSED        = 4

# VENDOR_CATALOG_STATUS = {
#     VENDOR_CATALOG_NOT_PARSED   : "not parsed",
#     VENDOR_CATALOG_PARSED       : "parsed",
#     VENDOR_CATALOG_COGNIZED     : "cognized",
#     VENDOR_CATALOG_PROCESSED    : "processed",
#     }

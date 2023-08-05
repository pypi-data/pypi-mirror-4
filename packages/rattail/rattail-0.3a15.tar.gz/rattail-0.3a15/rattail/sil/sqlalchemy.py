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
``rattail.sil.sqlalchemy`` -- SQLAlchemy Utilities
"""

from __future__ import absolute_import

import re

from sqlalchemy import types

from rattail.gpc import GPCType


__all__ = ['get_sqlalchemy_type']


sil_type_pattern = re.compile(r'^(CHAR|NUMBER)\((\d+(?:\,\d+)?)\)$')


def get_sqlalchemy_type(sil_type):
    """
    Returns a SQLAlchemy data type according to a SIL data type.
    """

    if sil_type == 'GPC(14)':
        return GPCType

    if sil_type == 'FLAG(1)':
        return types.Boolean

    m = sil_type_pattern.match(sil_type)
    if m:
        data_type, precision = m.groups()
        if precision.isdigit():
            precision = int(precision)
            scale = 0
        else:
            precision, scale = precision.split(',')
            precision = int(precision)
            scale = int(scale)
        if data_type == 'CHAR':
            assert not scale, "FIXME"
            return types.String(precision)
        if data_type == 'NUMBER':
            return types.Numeric(precision, scale)

    assert False, "FIXME"

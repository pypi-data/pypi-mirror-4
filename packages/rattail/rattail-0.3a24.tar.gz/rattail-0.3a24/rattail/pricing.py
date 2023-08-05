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
``rattail.pricing`` -- Pricing Utilities
"""


__all__ = ['gross_margin']


def gross_margin(price, cost):
    """
    Calculate and return a gross margin percentage based on ``price`` and
    ``cost``.

    If ``price`` is empty (or zero), returns ``None``.

    If ``cost`` is empty (or zero), returns ``100``.
    """

    if not price:
        return None

    if not cost:
        return 100

    return 100 * (price - cost) / price

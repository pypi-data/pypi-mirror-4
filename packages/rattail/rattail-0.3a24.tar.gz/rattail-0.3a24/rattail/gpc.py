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
``rattail.gpc`` -- Global Product Code
"""

from rattail import barcodes


class GPC(object):
    """
    Class to abstract the details of Global Product Code data.  Examples of
    this would be UPC or EAN barcodes.

    The initial motivation for this class was to provide better SIL support.
    To that end, the instances are assumed to always be comprised of only
    numeric digits, and must include a check digit.  If you do not know the
    check digit, provide a ``calc_check_digit`` value to the constructor.
    """

    def __init__(self, value, calc_check_digit=False):
        """
        Constructor.  ``value`` must be either an integer or a long value, or a
        string containing only digits.

        If ``calc_check_digit`` is ``False``, then ``value`` is assumed to
        include the check digit.  If the value does not include a check digit
        and needs one to be calculated, then ``calc_check_digit`` should be a
        keyword signifying the algorithm to be used.

        Currently the only check digit algorithm keyword supported is
        ``'upc'``.  As that is likely to always be the default, a
        ``calc_check_digit`` value of ``True`` will be perceived as equivalent
        to ``'upc'``.
        """

        value = str(value)
        if calc_check_digit is True or calc_check_digit == 'upc':
            value += str(barcodes.upc_check_digit(value))
        self.value = int(value)

    def __eq__(self, other):
        try:
            return int(self) == int(other)
        except (TypeError, ValueError):
            return False

    def __ne__(self, other):
        try:
            return int(self) != int(other)
        except (TypeError, ValueError):
            return True

    def __cmp__(self, other):
        if int(self) < int(other):
            return -1
        if int(self) > int(other):
            return 1
        if int(self) == int(other):
            return 0
        assert False

    def __hash__(self):
        return hash(self.value)

    def __int__(self):
        return int(self.value)

    def __long__(self):
        return long(self.value)

    def __repr__(self):
        return "GPC('%014d')" % self.value

    def __str__(self):
        return str(unicode(self))

    def __unicode__(self):
        return u'%014d' % self.value

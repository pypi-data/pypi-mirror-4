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
``rattail.sil.batches`` -- Batch Stuff
"""

import edbob


__all__ = ['consume_batch_id']


def consume_batch_id(source='RATAIL'):
    """
    Returns the next available batch identifier for ``source``, incrementing
    the number to preserve uniqueness.
    """

    option = 'next_batch_id.%s' % source

    config = edbob.AppConfigParser('rattail')
    config_path = config.get_user_file('rattail.conf', create=True)
    config.read(config_path)

    batch_id = config.get('rattail.sil', option, default='')
    if not batch_id.isdigit():
        batch_id = '1'
    batch_id = int(batch_id)

    config.set('rattail.sil', option, str(batch_id + 1))
    config_file = open(config_path, 'w')
    config.write(config_file)
    config_file.close()
    return '%08u' % batch_id

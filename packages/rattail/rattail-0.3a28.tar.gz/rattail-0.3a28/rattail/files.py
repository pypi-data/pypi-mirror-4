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
``rattail.files`` -- File Utilities

This module contains various utility functions for use with the filesystem.
"""

import os.path
import shutil
import lockfile
from datetime import datetime


def count_lines(path):
    """
    Counts the number of lines in a text file.  Some attempt is made to ensure
    cross-platform compatibility.

    :param path: Path to the file.
    :type path: string

    :returns: Number of lines in the file.
    :rtype: integer
    """

    f = open(path, 'rb')
    lines = f.read().count('\n') + 1
    f.close()
    return lines


def creation_time(path):
    """
    Returns the "naive" (i.e. not timezone-aware) creation timestamp for a
    file.

    :param path: Path to the file.
    :type path: string

    :returns: The creation timestamp for the file.
    :rtype: ``datetime.datetime`` instance
    """

    time = os.path.getctime(path)
    return datetime.fromtimestamp(time)


def locking_copy(src, dst):
    """
    Implements a "locking" version of ``shutil.copy()``.

    This function exists to provide a more atomic method for copying a file
    into a folder which is being watched by a file monitor.  The assumption is
    that the monitor is configured to expect "locks" and therefore only process
    files once they have had their locks removed.

    :param src: Path to the source file.
    :type src: string

    :param dst: Path to the destination file (or directory).
    :type dst: string

    :returns: ``None``
    """

    if os.path.isdir(dst):
        fn = os.path.basename(src)
        dst = os.path.join(dst, fn)

    with lockfile.FileLock(dst):
        shutil.copy(src, dst)

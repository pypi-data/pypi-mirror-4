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
``rattail.labels`` -- Label Printing
"""

import os
import os.path
import socket
import shutil
from cStringIO import StringIO

import edbob
from edbob.util import requires_impl

from rattail.exceptions import LabelPrintingError


class LabelPrinter(edbob.Object):
    """
    Base class for all label printers.

    Label printing devices which are "natively" supported by Rattail will each
    derive from this class in order to provide implementation details specific
    to the device.  You will typically instantiate one of those subclasses (or
    one of your own design) in order to send labels to your physical printer.
    """

    profile_name = None
    formatter = None
    required_settings = None

    @requires_impl()
    def print_labels(self, labels, *args, **kwargs):
        """
        Prints labels found in ``labels``.
        """

        pass


class CommandFilePrinter(LabelPrinter):
    """
    Generic :class:`LabelPrinter` subclass which "prints" labels to a file in
    the form of native printer (textual) commands.  The output file is then
    expected to be picked up by a file monitor, and finally sent to the printer
    from there.
    """

    required_settings = {'output_dir': "Output Folder"}
    output_dir = None

    def batch_header_commands(self):
        """
        This method, if implemented, must return a sequence of string commands
        to be interpreted by the printer.  These commands will be the first
        which are written to the file.
        """

        return None

    def batch_footer_commands(self):
        """
        This method, if implemented, must return a sequence of string commands
        to be interpreted by the printer.  These commands will be the last
        which are written to the file.
        """

        return None

    def print_labels(self, labels, output_dir=None, progress=None):
        """
        "Prints" ``labels`` by generating a command file in the output folder.
        The full path of the output file to which commands are written will be
        returned to the caller.

        If ``output_dir`` is not specified, and the printer instance is
        associated with a :class:`LabelProfile` instance, then config will be
        consulted for the output path.  If a path still is not found, the
        current (working) directory will be assumed.
        """

        if not output_dir:
            output_dir = self.output_dir
        if not output_dir:
            raise LabelPrintingError("Printer does not have an output folder defined")

        labels_path = edbob.temp_path(prefix='rattail.', suffix='.labels')
        labels_file = open(labels_path, 'w')

        header = self.batch_header_commands()
        if header:
            labels_file.write('%s\n' % '\n'.join(header))

        commands = self.formatter.format_labels(labels, progress=progress)
        if commands is None:
            labels_file.close()
            os.remove(labels_path)
            return None

        labels_file.write(commands)

        footer = self.batch_footer_commands()
        if footer:
            labels_file.write('%s\n' % '\n'.join(footer))

        labels_file.close()
        fn = '%s_%s.labels' % (socket.gethostname(),
                               edbob.local_time().strftime('%Y-%m-%d_%H-%M-%S'))
        final_path = os.path.join(output_dir, fn)
        shutil.move(labels_path, final_path)
        return final_path


class LabelFormatter(edbob.Object):
    """
    Base class for all label formatters.
    """

    format = None

    @requires_impl()
    def format_labels(self, labels, progress=None, *args, **kwargs):
        """
        Formats ``labels`` and returns the result.
        """

        pass


class CommandFormatter(LabelFormatter):
    """
    Generic subclass of :class:`LabelFormatter` which generates native printer
    (textual) commands.
    """

    def format_labels(self, labels, progress=None):
        prog = None
        if progress:
            prog = progress("Formatting labels", len(labels))

        fmt = StringIO()

        cancel = False
        for i, (product, quantity) in enumerate(labels, 1):
            for j in range(quantity):
                header = self.label_header_commands()
                if header:
                    fmt.write('%s\n' % '\n'.join(header))
                fmt.write('%s\n' % '\n'.join(self.label_body_commands(product)))
                footer = self.label_footer_commands()
                if footer:
                    fmt.write('%s\n' % '\n'.join(footer))
            if prog and not prog.update(i):
                cancel = True
                break

        if prog:
            prog.destroy()

        if cancel:
            fmt.close()
            return None

        val = fmt.getvalue()
        fmt.close()
        return val

    def label_header_commands(self):
        """
        This method, if implemented, must return a sequence of string commands
        to be interpreted by the printer.  These commands will immediately
        precede each *label* in one-up printing, and immediately precede each
        *label pair* in two-up printing.
        """

        return None

    @requires_impl()
    def label_body_commands(self):
        pass

    def label_footer_commands(self):
        """
        This method, if implemented, must return a sequence of string commands
        to be interpreted by the printer.  These commands will immedately
        follow each *label* in one-up printing, and immediately follow each
        *label pair* in two-up printing.
        """

        return None


class TwoUpCommandFormatter(CommandFormatter):
    """
    Generic subclass of :class:`LabelFormatter` which generates native printer
    (textual) commands.

    This class contains logic to implement "two-up" label printing.
    """

    @property
    @requires_impl(is_property=True)
    def half_offset(self):
        """
        The X-coordinate value by which the second label should be offset, when
        two labels are printed side-by-side.
        """

        pass

    def format_labels(self, labels, progress=None):
        prog = None
        if progress:
            prog = progress("Formatting labels", len(labels))

        fmt = StringIO()

        cancel = False
        half_started = False
        for i, (product, quantity) in enumerate(labels, 1):
            for j in range(quantity):
                if half_started:
                    fmt.write('%s\n' % '\n'.join(
                            self.label_body_commands(product, x=self.half_offset)))
                    footer = self.label_footer_commands()
                    if footer:
                        fmt.write('%s\n' % '\n'.join(footer))
                    half_started = False
                else:
                    header = self.label_header_commands()
                    if header:
                        fmt.write('%s\n' % '\n'.join(header))
                    fmt.write('%s\n' % '\n'.join(
                            self.label_body_commands(product, x=0)))
                    half_started = True
            if prog and not prog.update(i):
                cancel = True
                break

        if prog:
            prog.destroy()

        if cancel:
            fmt.close()
            return None

        if half_started:
            footer = self.label_footer_commands()
            if footer:
                fmt.write('%s\n' % '\n'.join(footer))

        val = fmt.getvalue()
        fmt.close()
        return val

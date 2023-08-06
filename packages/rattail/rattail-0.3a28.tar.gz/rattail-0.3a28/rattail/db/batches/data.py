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
``rattail.db.batches.data`` -- Batch Data Providers
"""

import csv

from edbob.files import count_lines


__all__ = ['ProductQueryDataProvider', 'CSVDataProxy', 'CSVDataProvider']


class BatchDataProvider(object):

    def __len__(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError


class QueryDataProvider(BatchDataProvider):

    def __init__(self, query):
        self.query = query

    def __len__(self):
        return self.query.count()

    def __iter__(self):
        for data in self.query:
            yield data


class ProductDataProxy(object):

    def __init__(self, product):
        self.product = product

    def __getattr__(self, name):
        if name == 'F01':
            return self.product.upc
        if name == 'F02':
            return self.product.description
        if name == 'F22':
            return self.product.size
        if name == 'F155':
            if self.product.brand:
                return self.product.brand.name
            return ''
        raise AttributeError("Product has no attribute '%s'" % name)


class ProductQueryDataProvider(QueryDataProvider):

    def __iter__(self):
        for product in self.query:
            yield ProductDataProxy(product)


class CSVDataProxy(object):

    def __init__(self, row):
        self.row = row

    def __getattr__(self, name):
        if name in self.row:
            return self.row[name]
        raise AttributeError("CSV data row has no attribute '%s'" % name)


class CSVDataProvider(BatchDataProvider):

    proxy_class = CSVDataProxy

    def __init__(self, csv_path):
        self.csv_path = csv_path

    def __len__(self):
        return count_lines(self.csv_path)

    def __iter__(self):
        csv_file = open(self.csv_path, 'rb')
        reader = csv.DictReader(csv_file)
        for row in reader:
            yield self.proxy_class(row)
        csv_file.close()

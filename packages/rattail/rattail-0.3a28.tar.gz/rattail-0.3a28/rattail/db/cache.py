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
``rattail.db.cache`` -- Cache Helpers
"""

import edbob
from edbob.util import requires_impl

import rattail


class DataCacher(edbob.Object):

    def __init__(self, session=None, **kwargs):
        super(DataCacher, self).__init__(session=session, **kwargs)

    @property
    @requires_impl(is_property=True)
    def class_(self):
        pass
    
    @property
    def name(self):
        return self.class_.__name__

    def get_cache(self, progress):
        self.instances = {}

        query = self.session.query(self.class_)
        count = query.count()
        if not count:
            return self.instances
        
        prog = None
        # if progress:
        #     prog = progress("Reading %s records into cache" % self.name, count)

        cancel = False
        for i, instance in enumerate(query, 1):
            self.cache_instance(instance)
            if prog and not prog.update(i):
                cancel = True
                break

        if prog:
            prog.destroy()

        if cancel:
            session.close()
            return None
        return self.instances


class DepartmentCacher(DataCacher):

    class_ = rattail.Department

    def cache_instance(self, dept):
        self.instances[dept.number] = dept


class SubdepartmentCacher(DataCacher):

    class_ = rattail.Subdepartment

    def cache_instance(self, subdept):
        self.instances[subdept.number] = subdept


class BrandCacher(DataCacher):

    class_ = rattail.Brand

    def cache_instance(self, brand):
        self.instances[brand.name] = brand


class VendorCacher(DataCacher):

    class_ = rattail.Vendor

    def cache_instance(self, vend):
        self.instances[vend.id] = vend


class ProductCacher(DataCacher):

    class_ = rattail.Product

    def cache_instance(self, prod):
        self.instances[prod.upc] = prod


class CustomerGroupCacher(DataCacher):

    class_ = rattail.CustomerGroup

    def cache_instance(self, group):
        self.instances[group.id] = group


class CustomerCacher(DataCacher):

    class_ = rattail.Customer

    def cache_instance(self, customer):
        self.instances[customer.id] = customer

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
``rattail.db.load`` -- Load Data from Host
"""

from sqlalchemy.orm import joinedload

import edbob
import edbob.db

import rattail


class LoadProcessor(edbob.Object):

    def load_all_data(self, host_engine, progress=None):

        edbob.init_modules(['edbob.db', 'rattail.db'])

        self.host_session = edbob.Session(bind=host_engine)
        self.session = edbob.Session()

        cancel = False
        for cls in self.relevant_classes():
            if not self.load_class_data(cls, progress):
                cancel = True
                break

        self.host_session.close()
        if cancel:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()
        return not cancel

    def load_class_data(self, cls, progress=None):
        query = self.host_session.query(cls)
        if hasattr(self, 'query_%s' % cls.__name__):
            query = getattr(self, 'query_%s' % cls.__name__)(query)

        count = query.count()
        if not count:
            return True

        prog = None
        if progress:
            prog = progress("Loading %s data" % cls.__name__, count)

        cancel = False
        for i, instance in enumerate(query, 1):
            if hasattr(self, 'merge_%s' % cls.__name__):
                getattr(self, 'merge_%s' % cls.__name__)(instance)
            else:
                self.session.merge(instance)
            self.session.flush()
            if prog and not prog.update(i):
                cancel = True
                break

        if prog:
            prog.destroy()
        return not cancel

    def relevant_classes(self):
        yield edbob.Person
        yield edbob.User
        yield rattail.Store
        yield rattail.Department
        yield rattail.Subdepartment
        yield rattail.Category
        yield rattail.Brand
        yield rattail.Vendor
        yield rattail.Product
        yield rattail.CustomerGroup
        yield rattail.Customer
        yield rattail.Employee

    def query_Customer(self, q):
        q = q.options(joinedload(rattail.Customer.phones))
        q = q.options(joinedload(rattail.Customer.emails))
        q = q.options(joinedload(rattail.Customer._people))
        q = q.options(joinedload(rattail.Customer._groups))
        return q

    def query_CustomerPerson(self, q):
        q = q.options(joinedload(rattail.CustomerPerson.person))
        return q

    def query_Employee(self, q):
        q = q.options(joinedload(rattail.Employee.phones))
        q = q.options(joinedload(rattail.Employee.emails))
        return q

    def query_Person(self, q):
        q = q.options(joinedload(edbob.Person.phones))
        q = q.options(joinedload(edbob.Person.emails))
        return q

    def query_Product(self, q):
        q = q.options(joinedload(rattail.Product.costs))
        q = q.options(joinedload(rattail.Product.prices))
        return q

    def merge_Product(self, host_product):
        # This logic is necessary due to the inter-dependency between Product
        # and ProductPrice tables.  merge() will cause a flush(); however it
        # apparently will not honor the 'post_update=True' flag on the relevant
        # relationships..  I'm unclear whether this is a "bug" with SQLAlchemy,
        # but the workaround is simple enough that I'm leaving it for now.
        product = self.session.merge(host_product)
        product.regular_price_uuid = None
        product.current_price_uuid = None
        if host_product.regular_price_uuid:
            product.regular_price = self.session.merge(host_product.regular_price)
        if host_product.current_price_uuid:
            product.current_price = self.session.merge(host_product.current_price)

    def query_Store(self, q):
        q = q.options(joinedload(rattail.Store.phones))
        q = q.options(joinedload(rattail.Store.emails))
        return q

    def query_Vendor(self, q):
        q = q.options(joinedload(rattail.Vendor.contacts))
        q = q.options(joinedload(rattail.Vendor.phones))
        q = q.options(joinedload(rattail.Vendor.emails))
        return q

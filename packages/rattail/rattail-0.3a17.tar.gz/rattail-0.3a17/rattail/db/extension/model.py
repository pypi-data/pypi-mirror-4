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
``rattail.db.extension.model`` -- Schema Definition
"""

import logging

from sqlalchemy import Column, ForeignKey
from sqlalchemy import String, Integer, DateTime, Date, Boolean, Numeric, Text
from sqlalchemy import types
from sqlalchemy import and_
from sqlalchemy.orm import relationship, object_session
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import ordering_list

import edbob
from edbob.db.model import Base, uuid_column
from edbob.db.extensions.contact import Person, EmailAddress, PhoneNumber
from edbob.exceptions import LoadSpecError
from edbob.sqlalchemy import getset_factory

from rattail import sil
from rattail import batches
from rattail.gpc import GPCType


__all__ = ['Change', 'Store', 'StoreEmailAddress', 'StorePhoneNumber',
           'Department', 'Subdepartment', 'Brand', 'Category', 'Vendor',
           'VendorContact', 'VendorPhoneNumber', 'VendorEmailAddress',
           'Product', 'ProductCost', 'ProductPrice', 'Customer',
           'CustomerEmailAddress', 'CustomerPhoneNumber', 'CustomerGroup',
           'CustomerGroupAssignment', 'CustomerPerson', 'Employee',
           'EmployeeEmailAddress', 'EmployeePhoneNumber',
           'BatchColumn', 'Batch', 'BatchRow', 'LabelProfile']


log = logging.getLogger(__name__)


class Change(Base):
    """
    Represents a changed (or deleted) record, which is pending synchronization
    to another database.
    """

    __tablename__ = 'changes'

    class_name = Column(String(25), primary_key=True)
    uuid = Column(String(32), primary_key=True)
    deleted = Column(Boolean)

    def __repr__(self):
        status = 'deleted' if self.deleted else 'new/changed'
        return "<Change: %s, %s, %s>" % (self.class_name, self.uuid, status)


class BatchColumn(Base):
    """
    Represents a :class:`SilColumn` associated with a :class:`Batch`.
    """

    __tablename__ = 'batch_columns'

    uuid = uuid_column()
    batch_uuid = Column(String(32), ForeignKey('batches.uuid'))
    ordinal = Column(Integer, nullable=False)
    name = Column(String(20))
    display_name = Column(String(50))
    sil_name = Column(String(10))
    data_type = Column(String(15))
    description = Column(String(50))
    visible = Column(Boolean, default=True)

    def __init__(self, sil_name=None, **kwargs):
        if sil_name:
            kwargs['sil_name'] = sil_name
            sil_column = sil.get_column(sil_name)
            kwargs.setdefault('name', sil_name)
            kwargs.setdefault('data_type', sil_column.data_type)
            kwargs.setdefault('description', sil_column.description)
            kwargs.setdefault('display_name', sil_column.display_name)
        super(BatchColumn, self).__init__(**kwargs)

    def __repr__(self):
        return "<BatchColumn: %s>" % self.name

    def __unicode__(self):
        return unicode(self.display_name or '')


class BatchRow(edbob.Object):
    """
    Superclass of batch row objects.
    """

    def __unicode__(self):
        return u"Row %d" % self.ordinal


class Batch(Base):
    """
    Represents a SIL-compliant batch of data.
    """

    __tablename__ = 'batches'

    uuid = uuid_column()
    provider = Column(String(50))
    id = Column(String(8))
    source = Column(String(6))
    destination = Column(String(6))
    action_type = Column(String(6))
    description = Column(String(50))
    rowcount = Column(Integer, default=0)
    executed = Column(DateTime)
    purge = Column(Date)

    columns = relationship(BatchColumn, backref='batch',
                           collection_class=ordering_list('ordinal'),
                           order_by=BatchColumn.ordinal,
                           cascade='save-update, merge, delete, delete-orphan')

    _rowclasses = {}

    def __repr__(self):
        return "<Batch: %s>" % self.description

    def __unicode__(self):
        return unicode(self.description or '')

    @property
    def rowclass(self):
        """
        Returns the mapped class for the underlying row (data) table.
        """

        if not self.uuid:
            object_session(self).flush()
            assert self.uuid

        if self.uuid not in self._rowclasses:

            kwargs = {
                '__tablename__': 'batch.%s' % self.uuid,
                'uuid': uuid_column(),
                'ordinal': Column(Integer, nullable=False),
                }

            for column in self.columns:
                data_type = sil.get_sqlalchemy_type(column.data_type)
                kwargs[column.name] = Column(data_type)
            rowclass = type('BatchRow_%s' % str(self.uuid), (Base, BatchRow), kwargs)

            batch_uuid = self.uuid
            def batch(self):
                return object_session(self).query(Batch).get(batch_uuid)
            rowclass.batch = property(batch)

            self._rowclasses[self.uuid] = rowclass

        return self._rowclasses[self.uuid]

    def add_column(self, sil_name=None, **kwargs):
        column = BatchColumn(sil_name, **kwargs)
        self.columns.append(column)

    def add_row(self, row, **kwargs):
        """
        Adds a row to the batch data table.
        """

        session = object_session(self)
        # FIXME: This probably needs to use a func.max() query.
        row.ordinal = self.rowcount + 1
        session.add(row)
        self.rowcount += 1
        session.flush()

    def create_table(self):
        """
        Creates the batch's data table within the database.
        """

        session = object_session(self)
        self.rowclass.__table__.create(session.bind)

    def drop_table(self):
        """
        Drops the batch's data table from the database.
        """

        log.debug("Batch.drop_table: Dropping table for batch: %s, %s (%s)"
                  % (self.id, self.description, self.uuid))
        session = object_session(self)
        self.rowclass.__table__.drop(session.bind)

    def execute(self, progress=None):
        provider = self.get_provider()
        assert provider
        if not provider.execute(self, progress):
            return False
        self.executed = edbob.utc_time(naive=True)
        object_session(self).flush()
        return True

    def get_provider(self):
        assert self.provider
        return batches.get_provider(self.provider)

    def iter_rows(self):
        session = object_session(self)
        q = session.query(self.rowclass)
        q = q.order_by(self.rowclass.ordinal)
        return q


class StoreEmailAddress(EmailAddress):
    """
    Represents an email address associated with a :class:`Store`.
    """

    __mapper_args__ = {'polymorphic_identity': 'Store'}


class StorePhoneNumber(PhoneNumber):
    """
    Represents a phone (or fax) number associated with a :class:`Store`.
    """

    __mapper_args__ = {'polymorphic_identity': 'Store'}


class Store(Base):
    """
    Represents a store (physical or otherwise) within the organization.
    """

    __tablename__ = 'stores'

    uuid = uuid_column()
    id = Column(String(10))
    name = Column(String(100))

    def __repr__(self):
        return "<Store: %s, %s>" % (self.id, self.name)

    def __unicode__(self):
        return unicode(self.name or '')

    def add_email_address(self, address, type='Info'):
        email = StoreEmailAddress(address=address, type=type)
        self.emails.append(email)

    def add_phone_number(self, number, type='Voice'):
        phone = StorePhoneNumber(number=number, type=type)
        self.phones.append(phone)

Store.emails = relationship(
    StoreEmailAddress,
    backref='store',
    primaryjoin=StoreEmailAddress.parent_uuid == Store.uuid,
    foreign_keys=[StoreEmailAddress.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=StoreEmailAddress.preference,
    cascade='save-update, merge, delete, delete-orphan')

Store.email = relationship(
    StoreEmailAddress,
    primaryjoin=and_(
        StoreEmailAddress.parent_uuid == Store.uuid,
        StoreEmailAddress.preference == 1),
    foreign_keys=[StoreEmailAddress.parent_uuid],
    uselist=False,
    viewonly=True)

Store.phones = relationship(
    StorePhoneNumber,
    backref='store',
    primaryjoin=StorePhoneNumber.parent_uuid == Store.uuid,
    foreign_keys=[StorePhoneNumber.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=StorePhoneNumber.preference,
    cascade='save-update, merge, delete, delete-orphan')

Store.phone = relationship(
    StorePhoneNumber,
    primaryjoin=and_(
        StorePhoneNumber.parent_uuid == Store.uuid,
        StorePhoneNumber.preference == 1),
    foreign_keys=[StorePhoneNumber.parent_uuid],
    uselist=False,
    viewonly=True)


class Brand(Base):
    """
    Represents a brand or similar product line.
    """

    __tablename__ = 'brands'

    uuid = uuid_column()
    name = Column(String(100))

    def __repr__(self):
        return "<Brand: %s>" % self.name

    def __unicode__(self):
        return unicode(self.name or '')


class Department(Base):
    """
    Represents an organizational department.
    """

    __tablename__ = 'departments'

    uuid = uuid_column()
    number = Column(Integer)
    name = Column(String(30))

    def __repr__(self):
        return "<Department: %s>" % self.name

    def __unicode__(self):
        return unicode(self.name or '')


class Subdepartment(Base):
    """
    Represents an organizational subdepartment.
    """

    __tablename__ = 'subdepartments'

    uuid = uuid_column()
    number = Column(Integer)
    name = Column(String(30))
    department_uuid = Column(String(32), ForeignKey('departments.uuid'))

    department = relationship(Department)

    def __repr__(self):
        return "<Subdepartment: %s>" % self.name

    def __unicode__(self):
        return unicode(self.name or '')


class Category(Base):
    """
    Represents an organizational category for products.
    """

    __tablename__ = 'categories'

    uuid = uuid_column()
    number = Column(Integer)
    name = Column(String(50))
    department_uuid = Column(String(32), ForeignKey('departments.uuid'))

    department = relationship(Department)

    def __repr__(self):
        return "<Category: %s, %s>" % (self.number, self.name)

    def __str__(self):
        return str(self.name or '')

    def __unicode__(self):
        return unicode(self.name or '')


class VendorEmailAddress(EmailAddress):
    """
    Represents an email address associated with a :class:`Vendor`.
    """

    __mapper_args__ = {'polymorphic_identity': 'Vendor'}


class VendorPhoneNumber(PhoneNumber):
    """
    Represents a phone (or fax) number associated with a :class:`Vendor`.
    """

    __mapper_args__ = {'polymorphic_identity': 'Vendor'}


class VendorContact(Base):
    """
    Represents a point of contact (e.g. salesperson) for a vendor, from the
    retailer's perspective.
    """

    __tablename__ = 'vendor_contacts'

    uuid = uuid_column()
    vendor_uuid = Column(String(32), ForeignKey('vendors.uuid'), nullable=False)
    person_uuid = Column(String(32), ForeignKey('people.uuid'), nullable=False)
    preference = Column(Integer, nullable=False)

    person = relationship(Person)

    def __repr__(self):
        return "<VendorContact: %s, %s>" % (self.vendor, self.person)

    def __unicode__(self):
        return unicode(self.person)


class Vendor(Base):
    """
    Represents a vendor from which products are purchased by the store.
    """

    __tablename__ = 'vendors'

    uuid = uuid_column()
    id = Column(String(15))
    name = Column(String(40))
    special_discount = Column(Numeric(5,3))

    contacts = relationship(VendorContact, backref='vendor',
                            collection_class=ordering_list('preference', count_from=1),
                            order_by=VendorContact.preference,
                            cascade='save-update, merge, delete, delete-orphan')

    def __repr__(self):
        return "<Vendor: %s>" % self.name

    def __unicode__(self):
        return unicode(self.name or '')

    def add_contact(self, person):
        contact = VendorContact(person=person)
        self.contacts.append(contact)

    def add_email_address(self, address, type='Info'):
        email = VendorEmailAddress(address=address, type=type)
        self.emails.append(email)

    def add_phone_number(self, number, type='Voice'):
        phone = VendorPhoneNumber(number=number, type=type)
        self.phones.append(phone)

Vendor.emails = relationship(
    VendorEmailAddress,
    backref='vendor',
    primaryjoin=VendorEmailAddress.parent_uuid == Vendor.uuid,
    foreign_keys=[VendorEmailAddress.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=VendorEmailAddress.preference,
    cascade='save-update, merge, delete, delete-orphan')

Vendor.email = relationship(
    VendorEmailAddress,
    primaryjoin=and_(
        VendorEmailAddress.parent_uuid == Vendor.uuid,
        VendorEmailAddress.preference == 1),
    foreign_keys=[VendorEmailAddress.parent_uuid],
    uselist=False,
    viewonly=True)

Vendor.phones = relationship(
    VendorPhoneNumber,
    backref='vendor',
    primaryjoin=VendorPhoneNumber.parent_uuid == Vendor.uuid,
    foreign_keys=[VendorPhoneNumber.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=VendorPhoneNumber.preference,
    cascade='save-update, merge, delete, delete-orphan')

Vendor.phone = relationship(
    VendorPhoneNumber,
    primaryjoin=and_(
        VendorPhoneNumber.parent_uuid == Vendor.uuid,
        VendorPhoneNumber.preference == 1),
    foreign_keys=[VendorPhoneNumber.parent_uuid],
    uselist=False,
    viewonly=True)

Vendor.contact = relationship(
    VendorContact,
    primaryjoin=and_(
        VendorContact.vendor_uuid == Vendor.uuid,
        VendorContact.preference == 1),
    uselist=False,
    viewonly=True)


class ProductCost(Base):
    """
    Represents a source from which a product may be obtained via purchase.
    """

    __tablename__ = 'product_costs'

    uuid = uuid_column()
    product_uuid = Column(String(32), ForeignKey('products.uuid'), nullable=False)
    vendor_uuid = Column(String(32), ForeignKey('vendors.uuid'), nullable=False)
    preference = Column(Integer, nullable=False)
    code = Column(String(15))

    case_size = Column(Integer)
    case_cost = Column(Numeric(9,5))
    pack_size = Column(Integer)
    pack_cost = Column(Numeric(9,5))
    unit_cost = Column(Numeric(9,5))
    effective = Column(DateTime)

    vendor = relationship(Vendor)

    def __repr__(self):
        return "<ProductCost: %s : %s>" % (self.product, self.vendor)


class ProductPrice(Base):
    """
    Represents a price for a product.
    """

    __tablename__ = 'product_prices'

    uuid = uuid_column()
    product_uuid = Column(String(32), ForeignKey('products.uuid'), nullable=False)
    type = Column(Integer)
    level = Column(Integer)
    starts = Column(DateTime)
    ends = Column(DateTime)
    price = Column(Numeric(8,3))
    multiple = Column(Integer)
    pack_price = Column(Numeric(8,3))
    pack_multiple = Column(Integer)

    def __repr__(self):
        return "<ProductPrice: %s : %s>" % (self.product, self.price)


class Product(Base):
    """
    Represents a product for sale and/or purchase.
    """

    __tablename__ = 'products'

    uuid = uuid_column()
    upc = Column(GPCType, index=True)
    department_uuid = Column(String(32), ForeignKey('departments.uuid'))
    subdepartment_uuid = Column(String(32), ForeignKey('subdepartments.uuid'))
    category_uuid = Column(String(32), ForeignKey('categories.uuid'))
    brand_uuid = Column(String(32), ForeignKey('brands.uuid'))
    description = Column(String(60))
    description2 = Column(String(60))
    size = Column(String(30))
    unit_of_measure = Column(String(4))

    regular_price_uuid = Column(
        String(32),
        ForeignKey('product_prices.uuid',
                   use_alter=True,
                   name='products_regular_price_uuid_fkey'))

    current_price_uuid = Column(
        String(32),
        ForeignKey('product_prices.uuid',
                   use_alter=True,
                   name='products_current_price_uuid_fkey'))

    department = relationship(Department)
    subdepartment = relationship(Subdepartment)
    category = relationship(Category)
    brand = relationship(Brand)

    costs = relationship(ProductCost, backref='product',
                         collection_class=ordering_list('preference', count_from=1),
                         order_by=ProductCost.preference,
                         cascade='save-update, merge, delete, delete-orphan')

    def __repr__(self):
        return "<Product: %s>" % self.description

    def __unicode__(self):
        return unicode(self.description or '')

Product.prices = relationship(
    ProductPrice, backref='product',
    primaryjoin=ProductPrice.product_uuid == Product.uuid,
    cascade='save-update, merge, delete, delete-orphan')

Product.regular_price = relationship(
    ProductPrice,
    primaryjoin=Product.regular_price_uuid == ProductPrice.uuid,
    lazy='joined',
    post_update=True)

Product.current_price = relationship(
    ProductPrice,
    primaryjoin=Product.current_price_uuid == ProductPrice.uuid,
    lazy='joined',
    post_update=True)

Product.cost = relationship(
    ProductCost,
    primaryjoin=and_(
        ProductCost.product_uuid == Product.uuid,
        ProductCost.preference == 1,
        ),
    uselist=False,
    viewonly=True)

Product.vendor = relationship(
    Vendor,
    secondary=ProductCost.__table__,
    primaryjoin=and_(
        ProductCost.product_uuid == Product.uuid,
        ProductCost.preference == 1,
        ),
    secondaryjoin=Vendor.uuid == ProductCost.vendor_uuid,
    uselist=False,
    viewonly=True)


class EmployeeEmailAddress(EmailAddress):
    """
    Represents an email address associated with a :class:`Employee`.
    """

    __mapper_args__ = {'polymorphic_identity': 'Employee'}


class EmployeePhoneNumber(PhoneNumber):
    """
    Represents a phone (or fax) number associated with a :class:`Employee`.
    """

    __mapper_args__ = {'polymorphic_identity': 'Employee'}


class Employee(Base):
    """
    Represents an employee within the organization.
    """

    __tablename__ = 'employees'

    uuid = uuid_column()
    id = Column(Integer)
    person_uuid = Column(String(32), ForeignKey('people.uuid'), nullable=False)
    status = Column(Integer)
    display_name = Column(String(100))

    person = relationship(Person)

    first_name = association_proxy('person', 'first_name')
    last_name = association_proxy('person', 'last_name')

    def __repr__(self):
        return "<Employee: %s>" % self.person

    def __unicode__(self):
        return unicode(self.display_name or self.person)

    def add_email_address(self, address, type='Home'):
        email = EmployeeEmailAddress(address=address, type=type)
        self.emails.append(email)

    def add_phone_number(self, number, type='Home'):
        phone = EmployeePhoneNumber(number=number, type=type)
        self.phones.append(phone)

Employee.emails = relationship(
    EmployeeEmailAddress,
    backref='employee',
    primaryjoin=EmployeeEmailAddress.parent_uuid == Employee.uuid,
    foreign_keys=[EmployeeEmailAddress.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=EmployeeEmailAddress.preference,
    cascade='save-update, merge, delete, delete-orphan')

Employee.email = relationship(
    EmployeeEmailAddress,
    primaryjoin=and_(
        EmployeeEmailAddress.parent_uuid == Employee.uuid,
        EmployeeEmailAddress.preference == 1),
    foreign_keys=[EmployeeEmailAddress.parent_uuid],
    uselist=False,
    viewonly=True)

Employee.phones = relationship(
    EmployeePhoneNumber,
    backref='employee',
    primaryjoin=EmployeePhoneNumber.parent_uuid == Employee.uuid,
    foreign_keys=[EmployeePhoneNumber.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=EmployeePhoneNumber.preference,
    cascade='save-update, merge, delete, delete-orphan')

Employee.phone = relationship(
    EmployeePhoneNumber,
    primaryjoin=and_(
        EmployeePhoneNumber.parent_uuid == Employee.uuid,
        EmployeePhoneNumber.preference == 1),
    foreign_keys=[EmployeePhoneNumber.parent_uuid],
    uselist=False,
    viewonly=True)


class CustomerEmailAddress(EmailAddress):
    """
    Represents an email address associated with a :class:`Customer`.
    """

    __mapper_args__ = {'polymorphic_identity': 'Customer'}


class CustomerPhoneNumber(PhoneNumber):
    """
    Represents a phone (or fax) number associated with a :class:`Customer`.
    """

    __mapper_args__ = {'polymorphic_identity': 'Customer'}


class CustomerPerson(Base):
    """
    Represents the association between a :class:`Person` and a customer account
    (:class:`Customer`).
    """

    __tablename__ = 'customers_people'

    uuid = uuid_column()
    customer_uuid = Column(String(32), ForeignKey('customers.uuid'))
    person_uuid = Column(String(32), ForeignKey('people.uuid'))
    ordinal = Column(Integer, nullable=False)

    person = relationship(Person)


class Customer(Base):
    """
    Represents a customer account.  Customer accounts may consist of more than
    one :class:`Person`, in some cases.
    """

    __tablename__ = 'customers'

    uuid = uuid_column()
    id = Column(String(20))
    name = Column(String(255))
    email_preference = Column(Integer)

    def __repr__(self):
        return "<Customer: %s, %s>" % (self.id, self.name or self.person)

    def __unicode__(self):
        return unicode(self.name or self.person)

    def add_email_address(self, address, type='Home'):
        email = CustomerEmailAddress(address=address, type=type)
        self.emails.append(email)

    def add_phone_number(self, number, type='Home'):
        phone = CustomerPhoneNumber(number=number, type=type)
        self.phones.append(phone)

Customer.emails = relationship(
    CustomerEmailAddress,
    backref='customer',
    primaryjoin=CustomerEmailAddress.parent_uuid == Customer.uuid,
    foreign_keys=[CustomerEmailAddress.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=CustomerEmailAddress.preference,
    cascade='save-update, merge, delete, delete-orphan')

Customer.email = relationship(
    CustomerEmailAddress,
    primaryjoin=and_(
        CustomerEmailAddress.parent_uuid == Customer.uuid,
        CustomerEmailAddress.preference == 1),
    foreign_keys=[CustomerEmailAddress.parent_uuid],
    uselist=False,
    viewonly=True)

Customer.phones = relationship(
    CustomerPhoneNumber,
    backref='customer',
    primaryjoin=CustomerPhoneNumber.parent_uuid == Customer.uuid,
    foreign_keys=[CustomerPhoneNumber.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=CustomerPhoneNumber.preference,
    cascade='save-update, merge, delete, delete-orphan')

Customer.phone = relationship(
    CustomerPhoneNumber,
    primaryjoin=and_(
        CustomerPhoneNumber.parent_uuid == Customer.uuid,
        CustomerPhoneNumber.preference == 1),
    foreign_keys=[CustomerPhoneNumber.parent_uuid],
    uselist=False,
    viewonly=True)

Customer._people = relationship(
    CustomerPerson, backref='customer',
    primaryjoin=CustomerPerson.customer_uuid == Customer.uuid,
    collection_class=ordering_list('ordinal', count_from=1),
    order_by=CustomerPerson.ordinal)

Customer.people = association_proxy(
    '_people', 'person',
    getset_factory=getset_factory,
    creator=lambda x: CustomerPerson(person=x))

Customer._person = relationship(
    CustomerPerson,
    primaryjoin=and_(
        CustomerPerson.customer_uuid == Customer.uuid,
        CustomerPerson.ordinal == 1),
    uselist=False,
    viewonly=True)

Customer.person = association_proxy(
    '_person', 'person',
    getset_factory=getset_factory)


class CustomerGroup(Base):
    """
    Represents an arbitrary group to which :class:`Customer` instances may (or
    may not) belong.
    """

    __tablename__ = 'customer_groups'

    uuid = uuid_column()
    id = Column(String(20))
    name = Column(String(255))

    def __repr__(self):
        return "<CustomerGroup: %s, %s>" % (self.id, self.name)

    def __unicode__(self):
        return unicode(self.name or '')


class CustomerGroupAssignment(Base):
    """
    Represents the assignment of a :class:`Customer` to a
    :class:`CustomerGroup`.
    """

    __tablename__ = 'customers_groups'

    uuid = uuid_column()
    customer_uuid = Column(String(32), ForeignKey('customers.uuid'))
    group_uuid = Column(String(32), ForeignKey('customer_groups.uuid'))
    ordinal = Column(Integer, nullable=False)

    group = relationship(CustomerGroup)

Customer._groups = relationship(
    CustomerGroupAssignment, backref='customer',
    collection_class=ordering_list('ordinal', count_from=1),
    order_by=CustomerGroupAssignment.ordinal)

Customer.groups = association_proxy(
    '_groups', 'group',
    getset_factory=getset_factory,
    creator=lambda x: CustomerGroupAssignment(group=x))


class LabelProfile(Base):
    """
    Represents a "profile" (collection of settings) for product label printing.
    """

    __tablename__ = 'label_profiles'

    uuid = uuid_column()
    ordinal = Column(Integer)
    code = Column(String(3))
    description = Column(String(50))
    printer_spec = Column(String(255))
    formatter_spec = Column(String(255))
    format = Column(Text)

    _printer = None
    _formatter = None

    def __repr__(self):
        return "<LabelProfile: %s>" % self.code

    def __unicode__(self):
        return unicode(self.description or '')

    def get_formatter(self):
        if not self._formatter and self.formatter_spec:
            try:
                formatter = edbob.load_spec(self.formatter_spec)
            except LoadSpecError:
                pass
            else:
                self._formatter = formatter()
        return self._formatter        

    def get_printer(self):
        if not self._printer and self.printer_spec:
            try:
                printer = edbob.load_spec(self.printer_spec)
            except LoadSpecError:
                pass
            else:
                self._printer = printer()
                for name in printer.required_settings:
                    setattr(printer, name, self.get_printer_setting(name))
                self._printer.formatter = self.get_formatter()
        return self._printer

    def get_printer_setting(self, name):
        session = object_session(self)
        if not self.uuid:
            session.flush()
        name = 'labels.%s.printer.%s' % (self.uuid, name)
        return edbob.get_setting(name, session)

    def save_printer_setting(self, name, value):
        session = object_session(self)
        if not self.uuid:
            session.flush()
        name = 'labels.%s.printer.%s' % (self.uuid, name)
        edbob.save_setting(name, value, session)

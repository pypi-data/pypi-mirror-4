# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2008-2013 Async Open Source <http://www.async.com.br>
## All rights reserved
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
## Author(s): Stoq Team <stoq-devel@async.com.br>
##

"""Viewable implementation using python

Using Viewable, you can create an special object that will have properties from
different tables, for instance, given this to ORM classes:

   >>> from storm.expr import LeftJoin, Count, Sum
   >>> from stoqlib.api import api
   >>> from stoqlib.database.orm import ORMObject
   >>> from stoqlib.database.properties import DecimalCol, DateTimeCol
   >>> from stoqlib.database.properties import IntCol, UnicodeCol

   >>> class Person(ORMObject):
   ...     __storm_table__ = 'person'
   ...     id = IntCol(primary=True)
   ...     name = UnicodeCol()

   >>> class Client(ORMObject):
   ...     __storm_table__ = 'client'
   ...     id = IntCol(primary=True)
   ...     person_id = IntCol()
   ...     salary = DecimalCol()
   ...     status = IntCol()

You can create a viewable like this:

    >>> class ClientView(Viewable):
    ...     id = Client.id
    ...     name = Person.name
    ...     salary = Client.salary
    ...
    ...     tables = [Client,
    ...               LeftJoin(Person, Person.id == Client.person_id)]

And use it like a regular table with storm:

    >>> store = api.new_store()
    >>> for v in store.find(ClientView).order_by(Person.name):
    ...     print v.name, v.salary
    Alessandra Almeida Itaberá 0.00
    Franciso Elisio de Lima Junior 0.00
    Luis Sergio da Silva Marin 0.00
    Vitalina Claudino 0.00

You can also define another class as properties of the viewable. For instance:

    >>> class ClientView(Viewable):
    ...     client = Client
    ...     person = Person
    ...
    ...     name = Person.name
    ...     nick = Client.salary
    ...
    ...     tables = [Client,
    ...               LeftJoin(Person, Person.id == Client.person_id)]

When you query using this viewable, not only the name and nick properties
will be fetched, but the whole Client and Person objects will be also fetched
(on the same sql select), and the objects will be added to the cache, so you can
use them later, without going to the database for another query.

Another interesting feature is the possiblity to use aggregates in the viewable.
Lets consider this sales table:

    >>> class Sale(ORMObject):
    ...     __storm_table__ = 'sale'
    ...     id = IntCol(primary=True)
    ...     client_id = IntCol()
    ...     total_amount = DecimalCol()
    ...     status = IntCol()

Now we can create this viewable:


    >>> class ClientSalesView(Viewable):
    ...    id = Client.id
    ...    name = Person.name
    ...    total_sales = Count(Sale.id)
    ...    total_value = Sum(Sale.total_amount)
    ...
    ...    tables = [Client,
    ...              LeftJoin(Person, Person.id == Client.person_id),
    ...              LeftJoin(Sale, Sale.client_id == Client.id)]
    ...
    ...    group_by = [id, name]

    >>> store = api.new_store()
    >>> for v in store.find(ClientSalesView).order_by(Person.name):
    ...     print v.name, v.total_sales, v.total_value
    Alessandra Almeida Itaberá 1 706.00
    Franciso Elisio de Lima Junior 0 None
    Luis Sergio da Silva Marin 1 873.00
    Vitalina Claudino 1 436.00

    >>> store.close()

"""

import warnings
import inspect

from kiwi.python import ClassInittableObject
from storm.expr import Expr
from storm.properties import PropertyColumn

from stoqlib.database.orm import ORMObject


class Viewable(ClassInittableObject):
    # This is only used by query executer, and can be removed once all viewables
    # are converted to the new api
    __storm_table__ = 'viewable'

    #: This is the cls_spec that should be used with store.find(). Will be
    #: created by StoqlibStore when the viewable is first used.
    cls_spec = None

    #: Corresponding attributes for each cls_spec. Will be created by
    #: StoqlibStore when the viewable is first used.
    cls_attributes = None

    #: A list of tables that will be queried
    tables = []

    #: If any property defined in this viewable is an aggregate funcion (that
    #: needs grouping), this should have all the columns or table that should be
    #: grouped.
    group_by = []

    #: If not ``None``, this will be appended to the query passed to
    #: store.find()
    clause = None

    #: This is a list of column names that should not be selected, but should
    #: still be possible to filter by.
    hidden_columns = []

    @property
    def store(self):
        warnings.warn("Dont use self.store - get it from some other object)",
                      DeprecationWarning, stacklevel=2)
        return self._store

    # Maybe we could try to use the same api from storm (autoreload)
    def sync(self):
        """Update the values of this object from the database
        """
        new_obj = self.store.find(type(self), id=self.id).one()
        self.__dict__.update(new_obj.__dict__)

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.id == other.id
        return False

    @classmethod
    def __class_init__(cls, new_attrs):
        cls_spec = []
        attributes = []

        # We can ignore the last two items, since they are the Viewable class
        # and ``object``
        for base in inspect.getmro(cls)[:-2]:
            for attr, value in base.__dict__.iteritems():
                if attr == 'clause':
                    continue
                if attr in cls.hidden_columns:
                    continue

                try:
                    is_domain = issubclass(value, ORMObject)
                except TypeError:
                    is_domain = False

                # XXX: This is to workaround the viewables sometimes defining
                # aliases for some tables - They are valid domain classes, but
                # should not be used in the store.find() call
                if is_domain and value.__name__.endswith('Alias'):
                    continue

                if (is_domain or isinstance(value, PropertyColumn) or
                    isinstance(value, Expr)):
                    attributes.append(attr)
                    cls_spec.append(value)

        cls.cls_spec = tuple(cls_spec)
        cls.cls_attributes = attributes

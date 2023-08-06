# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005-2013 Async Open Source <http://www.async.com.br>
## All rights reserved
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
## Author(s): Stoq Team <stoq-devel@async.com.br>
##
"""
The base :class:`Domain` class for Stoq.

"""

import warnings

from storm.expr import And, Like
from storm.info import get_cls_info, get_obj_info
from storm.references import Reference
from storm.store import AutoReload

# pylint: disable=E1101
from stoqlib.database.expr import  StatementTimestamp
from stoqlib.database.orm import ORMObject
from stoqlib.database.properties import IntCol
from stoqlib.database.runtime import get_current_user, get_current_station
from stoqlib.domain.system import TransactionEntry


class Domain(ORMObject):
    """The base domain for Stoq.

    This builds on top of :class:`stoqlib.database.properties.ORMObject` and adds:

    * created and modified |transactionentry|, a log which is mainly used
      by database synchonization, it allows us to find out what has been
      modified and created within a specific time frame.
    * create/update/modify hooks, which some domain objects implement to
      fire of events that can be used to find out when a specific
      domain event is triggered, eg a |sale| is created, a |product| is
      modified. etc.
    * cloning of domains, when you want to create a new similar domain
    * function to check if an value of a column is unique within a domain.

    Not all domain objects need to subclass Domain, some, such as
    :class:`stoqlib.domain.system.SystemTable` inherit from ORMObject.
    """

    # FIXME: this is only used by pylint
    __storm_table__ = 'invalid'

    id = IntCol(primary=True, default=AutoReload)

    te_id = IntCol(default=None)

    #: a |transactionentry| for when the domain object was created and last
    #: modified
    te = Reference(te_id, 'TransactionEntry.id')

    def __init__(self, *args, **kwargs):
        self._listen_to_events()
        self._creating = True
        ORMObject.__init__(self, *args, **kwargs)
        self._creating = False

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.id)

    def __storm_loaded__(self):
        self._listen_to_events()
        self._creating = False

    # Private

    def _listen_to_events(self):
        event = get_obj_info(self).event
        event.hook('added', self._on_object_added)
        event.hook('changed', self._on_object_changed)
        event.hook('before-removed', self._on_object_before_removed)

    def _on_object_changed(self, obj_info, variable, old_value, new_value,
                           fromdb):
        if new_value is not AutoReload and not fromdb:
            if self._creating:
                return
            store = obj_info.get("store")
            store.add_modified_object(self)

    def _on_object_added(self, obj_info):
        store = obj_info.get("store")
        store.block_implicit_flushes()
        user = get_current_user(store)
        station = get_current_station(store)
        store.unblock_implicit_flushes()

        self.te = TransactionEntry(store=store,
            te_time=StatementTimestamp(),
            user_id=user and user.id,
            station_id=station and station.id)

        store.add_created_object(self)

    def _on_object_before_removed(self, obj_info):
        # This is emited right before the object is removed from the store.
        # We must also remove the transaction entry, but the entry should be
        # deleted *after* the object is deleted, thats why we need to specify
        # the flush order.

        # This cannot be done on _on_object_removed, since by then, the object
        # will no longer have valid properties (and sometimes we cannot get the
        # transaction entry)
        store = obj_info.get("store")
        store.remove(self.te)
        store.add_flush_order(self, self.te)

        # FIXME: We should remove the add_deleted_object, since that object will
        # be processed only when the transaction is commited, and that is to
        # late to trust the values of the object.
        store.add_deleted_object(self)

    #
    # Public API
    #

    def on_create(self):
        """Called when *self* is about to be created on the database

        This hook can be overridden on child classes for improved functionality.

        A trick you may want to use: Use :meth:`ORMObject.get_store` to get the
        :class:`store <stoqlib.database.runtime.StoqlibStore>` in which
        *self* lives and do your modifications in it.
        """

    def on_update(self):
        """Called when *self* is about to be updated on the database

        This hook can be overridden on child classes for improved
        functionality.

        A trick you may want to use: Use :meth:`ORMObject.get_store` to get the
        :class:`store <stoqlib.database.runtime.StoqlibStore>` in which
        *self* lives and do your modifications in it.
        """

    def on_delete(self):
        """Called when *self* is about to be removed from the database

        This hook can be overridden on child classes for improved
        functionality.

        A trick you may want to use: Use :meth:`ORMObject.get_store` to get the
        :class:`store <stoqlib.database.runtime.StoqlibStore>` in which
        *self* lives and do your modifications in it.

        Do not try to modify *self*, as it was marked as obsolete by
        :class:`stoqlib.database.properties.ORMObject` and it will result in errors.
        """

    def clone(self):
        """Get a persistent copy of an existent object. Remember that we can
        not use copy because this approach will not activate ORMObject
        methods which allow creating persitent objects. We also always
        need a new id for each copied object.

        :returns: the copy of ourselves
        """

        warnings.warn("don't use this", DeprecationWarning, stacklevel=2)
        kwargs = {}
        for column in get_cls_info(self.__class__).columns:
            # FIXME: Make sure this is cloning correctly
            name = column.name
            if name in ['id', 'identifier',
                        'te_id']:
                continue
            if name.endswith('_id'):
                name = name[:-3]
            kwargs[name] = getattr(self, name)

        klass = type(self)
        return klass(store=self.store, **kwargs)

    def check_unique_value_exists(self, attribute, value,
                                  case_sensitive=True):
        """Returns ``True`` if we already have the given attribute
        and value in the database, but ignoring myself.

        :param attribute: the attribute that should be unique
        :param value: value that we will check if exists in the database
        :param case_sensitive: If the checking should be case sensitive or
          not.
        """
        return self.check_unique_tuple_exists({attribute: value},
                                              case_sensitive)

    def check_unique_tuple_exists(self, values, case_sensitive=True):
        """Returns ``True`` if we already have the given attributes and values
        in the database, but ignoring myself.

        :param values: dictionary of attributes:values that we will check if
          exists in the database.
        :param case_sensitive: If the checking should be case sensitive or
          not.
        """

        if all([value in ['', None] for value in values.values()]):
            return False

        clauses = []
        for attr, value, in values.items():
            if not isinstance(value, unicode) or case_sensitive:
                clauses.append(attr == value)
            else:
                clauses.append(Like(attr, value, case_sensitive=False))

        cls = type(self)
        # Remove myself from the results.
        if hasattr(self, 'id'):
            clauses.append(cls.id != self.id)
        query = And(*clauses)

        return not self.store.find(cls, query).is_empty()

# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2008 Async Open Source <http://www.async.com.br>
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
""" Dialog to register the initial stock of a product in a certain branch """

from decimal import Decimal
from sys import maxint as MAXINT

import gtk

from kiwi import ValueUnset
from kiwi.enums import ListType
from kiwi.ui.objectlist import Column
from kiwi.ui.listdialog import ListSlave

from stoqlib.api import api
from stoqlib.domain.product import Storable
from stoqlib.gui.editors.baseeditor import BaseEditor
from stoqlib.lib.message import yesno
from stoqlib.lib.translation import stoqlib_gettext

_ = stoqlib_gettext


class _TemporaryStorableItem(object):
    def __init__(self, item):
        self.obj = item
        sellable = item.product.sellable
        self.code = sellable.code
        self.barcode = sellable.barcode
        self.category_description = sellable.get_category_description()
        self.description = sellable.get_description()
        self.initial_stock = 0


class InitialStockDialog(BaseEditor):
    gladefile = "InitialStockDialog"
    model_type = object
    title = _(u"Product  - Initial Stock")
    size = (750, 450)
    help_section = 'stock-register-initial'

    def __init__(self, store, branch=None):
        if branch is None:
            self._branch = api.get_current_branch(store)
        else:
            self._branch = branch
        BaseEditor.__init__(self, store, model=object())

        self._setup_widgets()

    def _setup_widgets(self):
        self.branch_label.set_markup(
            _(u"Registering initial stock for products in <b>%s</b>") %
            api.escape(self._branch.person.name))

        self._storables = [_TemporaryStorableItem(s)
            for s in self.store.find(Storable)
                if s.get_stock_item(self._branch) is None]

        self.slave.listcontainer.add_items(self._storables)

    def _get_columns(self):
        adj = gtk.Adjustment(upper=MAXINT, step_incr=1)
        return [Column("code", title=_(u"Code"), data_type=str, sorted=True,
                       width=100),
                Column("barcode", title=_(u"Barcode"), data_type=str,
                       width=100),
                Column("category_description", title=_(u"Category"),
                       data_type=str, width=100),
                Column("description", title=_(u"Description"),
                       data_type=str, expand=True),
                Column('manufacturer', title=_("Manufacturer"),
                       data_type=str, visible=False),
                Column('model', title=_("Model"),
                       data_type=str, visible=False),
                Column("initial_stock", title=_(u"Initial Stock"),
                       data_type=Decimal, format_func=self._format_qty,
                       editable=True, spin_adjustment=adj, width=115)]

    def _format_qty(self, quantity):
        if quantity is ValueUnset:
            return None
        if quantity >= 0:
            return quantity

    def _validate_initial_stock_quantity(self, item, store):
        positive = item.initial_stock > 0
        if item.initial_stock is not ValueUnset and positive:
            storable = store.fetch(item.obj)
            storable.register_initial_stock(item.initial_stock, self._branch)

    def _add_initial_stock(self):
        for item in self._storables:
            self._validate_initial_stock_quantity(item, self.store)

    #
    # BaseEditorSlave
    #

    def setup_slaves(self):
        self.slave = ListSlave(self._get_columns())
        self.slave.set_list_type(ListType.READONLY)
        self.slave.listcontainer.list.connect(
            "cell-edited", self._on_objectlist__cell_edited)
        self.attach_slave("on_slave_holder", self.slave)

    def on_confirm(self):
        self._add_initial_stock()

    def on_cancel(self):
        if self._storables:
            msg = _('Save data before close the dialog ?')
            if yesno(msg, gtk.RESPONSE_NO, _("Save data"), _("Don't save")):
                self._add_initial_stock()
                # change retval to True so the store gets commited
                self.retval = True

    #
    # Callbacks
    #

    def _on_objectlist__cell_edited(self, objectlist, item, attr):
        # After filling a value, jump to the next cell or to the ok
        # button if we are at the last one
        treeview = objectlist.get_treeview()
        rows, column = treeview.get_cursor()
        next_row = rows[0] + 1
        nitems = len(self._storables)
        if next_row < nitems:
            treeview.set_cursor(next_row, column)
        else:
            objectlist.unselect_all()
            self.main_dialog.ok_button.grab_focus()

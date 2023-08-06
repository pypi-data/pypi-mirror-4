# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2007-2009 Async Open Source <http://www.async.com.br>
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
""" Stock transfer wizard definition """

import datetime
from decimal import Decimal
import operator

import gtk
from kiwi.datatypes import ValidationError
from kiwi.python import Settable
from kiwi.ui.widgets.list import Column
from storm.expr import And

from stoqlib.api import api
from stoqlib.domain.person import Branch, Employee
from stoqlib.domain.product import ProductStockItem
from stoqlib.domain.sellable import Sellable
from stoqlib.domain.transfer import TransferOrder, TransferOrderItem
from stoqlib.domain.views import ProductWithStockView
from stoqlib.gui.base.columns import AccessorColumn
from stoqlib.gui.base.wizards import (BaseWizard, BaseWizardStep)
from stoqlib.gui.events import StockTransferWizardFinishEvent
from stoqlib.gui.printing import print_report
from stoqlib.gui.wizards.abstractwizard import SellableItemStep
from stoqlib.lib.message import warning, yesno
from stoqlib.lib.translation import locale_sorted, stoqlib_gettext
from stoqlib.reporting.transferreceipt import TransferOrderReceipt

_ = stoqlib_gettext


#
# Wizard steps
#

class TemporaryTransferOrder(object):

    def __init__(self):
        self.items = []
        self.open_date = datetime.date.today()
        self.receival_date = datetime.date.today()
        self.source_branch = None
        self.destination_branch = None
        self.source_responsible = None
        self.destination_responsible = None

    @property
    def branch(self):
        # This method is here because SellableItemStep requires a branch
        # property
        return self.source_branch

    def add_item(self, item):
        self.items.append(item)

    def get_items(self):
        return self.items

    def remove_item(self, item):
        self.items.remove(item)


class TemporaryTransferOrderItem(Settable):
    pass


class StockTransferItemStep(SellableItemStep):
    model_type = TemporaryTransferOrder
    item_table = TemporaryTransferOrderItem
    sellable_view = ProductWithStockView

    def __init__(self, wizard, previous, store, model):
        self.branch = api.get_current_branch(store)
        SellableItemStep.__init__(self, wizard, previous, store, model)

    #
    # SellableItemStep hooks
    #

    def get_sellable_view_query(self):
        branch = api.get_current_branch(self.store)
        branch_query = ProductStockItem.branch_id == branch.id
        sellable_query = Sellable.get_unblocked_sellables_query(self.store,
                                                                storable=True)
        query = And(branch_query, sellable_query)
        return self.sellable_view, query

    def get_saved_items(self):
        return list(self.model.get_items())

    def get_order_item(self, sellable, cost, quantity):
        item = self.get_model_item_by_sellable(sellable)
        if item is not None:
            item.quantity += quantity
        else:
            item = TemporaryTransferOrderItem(quantity=quantity,
                                              sellable=sellable)
            self.model.add_item(item)
        return item

    def get_columns(self):
        return [
            Column('sellable.description', title=_(u'Description'),
                   data_type=str, expand=True, searchable=True),
            AccessorColumn('stock', title=_(u'Stock'), data_type=Decimal,
                           accessor=self._get_stock_quantity, width=80),
            Column('quantity', title=_(u'Transfer'), data_type=Decimal,
                   width=100),
            AccessorColumn('total', title=_(u'Total'), data_type=Decimal,
                            accessor=self._get_total_quantity, width=80),
            ]

    def _get_stock_quantity(self, item):
        storable = item.sellable.product_storable
        stock_item = storable.get_stock_item(self.branch)
        return stock_item.quantity or 0

    def _get_total_quantity(self, item):
        qty = self._get_stock_quantity(item)
        qty -= item.quantity
        if qty > 0:
            return qty
        return 0

    def _setup_summary(self):
        self.summary = None

    def _get_stock_balance(self, sellable):
        storable = sellable.product_storable
        quantity = storable.get_balance_for_branch(self.branch) or Decimal(0)
        # do not count the added quantity
        for item in self.slave.klist:
            if item.sellable == sellable:
                quantity -= item.quantity
                break

        return quantity

    def sellable_selected(self, sellable):
        SellableItemStep.sellable_selected(self, sellable)

        if sellable is None:
            return

        storable = sellable.product_storable
        stock_item = storable.get_stock_item(self.branch)
        self.stock_quantity.set_label("%s" % stock_item.quantity or 0)

        quantity = self._get_stock_balance(sellable)
        has_quantity = quantity > 0
        self.quantity.set_sensitive(has_quantity)
        self.add_sellable_button.set_sensitive(has_quantity)
        if has_quantity:
            self.quantity.set_range(1, quantity)

    def setup_slaves(self):
        SellableItemStep.setup_slaves(self)

    #
    # WizardStep hooks
    #

    def post_init(self):
        self.hide_add_button()
        self.hide_edit_button()
        self.cost.hide()
        self.cost_label.hide()

    def next_step(self):
        return StockTransferFinishStep(self.store, self.wizard,
                                       self.model, self)

    def _on_quantity__validate(self, widget, value):
        sellable = self.proxy.model.sellable
        if not sellable:
            return

        balance = self._get_stock_balance(sellable)
        if value > balance:
            return ValidationError(
                _(u'Quantity is greater than the quantity in stock.'))

        return super(StockTransferItemStep,
                     self).on_quantity__validate(widget, value)


class StockTransferFinishStep(BaseWizardStep):
    gladefile = 'StockTransferFinishStep'
    proxy_widgets = ('open_date',
                     'receival_date',
                     'destination_responsible',
                     'destination_branch',
                     'source_responsible')

    def __init__(self, store, wizard, transfer_order, previous):
        self.store = store
        self.transfer_order = transfer_order
        self.branch = api.get_current_branch(self.store)
        BaseWizardStep.__init__(self, self.store, wizard, previous)
        self.setup_proxies()

    def setup_proxies(self):
        self._setup_widgets()
        self.proxy = self.add_proxy(self.transfer_order,
                                    StockTransferFinishStep.proxy_widgets)

    def _setup_widgets(self):
        items = [(b.person.name, b)
                    for b in self.store.find(Branch)
                        if b is not self.branch]
        self.destination_branch.prefill(locale_sorted(
            items, key=operator.itemgetter(0)))
        self.source_branch.set_text(self.branch.person.name)

        employees = self.store.find(Employee)
        self.source_responsible.prefill(api.for_combo(employees))
        self.destination_responsible.prefill(api.for_combo(employees))

        self.transfer_order.source_branch = self.branch
        self.transfer_order.destination_branch = items[0][1]

    def _validate_destination_branch(self):
        other_branch = self.destination_branch.read()

        if not self.branch.is_from_same_company(other_branch):
            warning(_(u"Branches are not from the same CNPJ"))
            return False

        return True

    #
    # WizardStep hooks
    #

    def post_init(self):
        self.register_validate_function(self.wizard.refresh_next)
        self.force_validation()

    def has_previous_step(self):
        return True

    def has_next_step(self):
        return False

    def validate_step(self):
        if not self._validate_destination_branch():
            return False

        return True

    #
    # Kiwi callbacks
    #

    def on_open_date__validate(self, widget, date):
        if date < datetime.date.today():
            return ValidationError(_(u"The date must be set to today "
                                      "or a future date"))
        receival_date = self.receival_date.get_date()
        if receival_date is not None and date > receival_date:
            return ValidationError(_(u"The open date must be set to "
                                      "before the receival date"))

    def on_receival_date__validate(self, widget, date):
        open_date = self.open_date.get_date()
        if open_date > date:
            return ValidationError(_(u"The receival date must be set "
                                      "to after the open date"))


#
# Main wizard
#


class StockTransferWizard(BaseWizard):
    title = _(u'Stock Transfer')
    size = (750, 350)

    def __init__(self, store):
        self.model = TemporaryTransferOrder()
        first_step = StockTransferItemStep(self, None, store, self.model)
        BaseWizard.__init__(self, store, first_step, self.model)
        self.next_button.set_sensitive(False)

    def _receipt_dialog(self, order):
        msg = _('Would you like to print a receipt for this transfer?')
        if yesno(msg, gtk.RESPONSE_YES, _("Print receipt"), _("Don't print")):
            print_report(TransferOrderReceipt, order)
        return

    def finish(self):
        order = TransferOrder(
            open_date=self.model.open_date,
            receival_date=self.model.receival_date,
            source_branch=self.model.source_branch,
            destination_branch=self.model.destination_branch,
            source_responsible=self.model.source_responsible,
            destination_responsible=self.model.destination_responsible,
            store=self.store)
        for item in self.model.get_items():
            transfer_item = TransferOrderItem(store=self.store,
                                              transfer_order=order,
                                              sellable=item.sellable,
                                              quantity=item.quantity)
            order.send_item(transfer_item)
        #XXX Waiting for transfer order receiving wizard implementation
        order.receive()

        self.retval = self.model
        self.close()
        StockTransferWizardFinishEvent.emit(order)
        self._receipt_dialog(order)

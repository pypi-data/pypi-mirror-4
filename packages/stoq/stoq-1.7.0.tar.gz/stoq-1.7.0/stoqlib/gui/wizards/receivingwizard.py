# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2006-2009 Async Open Source <http://www.async.com.br>
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
##
""" Receiving wizard definition """

import datetime
from decimal import Decimal
import gtk

from kiwi.currency import currency
from kiwi.ui.objectlist import Column, SearchColumn

from stoqlib.api import api
from stoqlib.database.queryexecuter import StoqlibQueryExecuter
from stoqlib.lib.translation import stoqlib_gettext
from stoqlib.gui.base.wizards import (WizardEditorStep, BaseWizard,
                                      BaseWizardStep)
from stoqlib.gui.base.dialogs import run_dialog
from stoqlib.gui.base.search import StoqlibSearchSlaveDelegate
from stoqlib.gui.slaves.receivingslave import ReceivingInvoiceSlave
from stoqlib.gui.wizards.abstractwizard import SellableItemStep
from stoqlib.gui.dialogs.purchasedetails import PurchaseDetailsDialog
from stoqlib.gui.dialogs.sellableimage import SellableImageViewer
from stoqlib.gui.dialogs.labeldialog import SkipLabelsEditor
from stoqlib.gui.editors.receivingeditor import ReceivingItemEditor
from stoqlib.gui.events import ReceivingOrderWizardFinishEvent
from stoqlib.gui.printing import print_labels
from stoqlib.lib.formatters import format_quantity, get_formatted_cost
from stoqlib.lib.message import yesno
from stoqlib.domain.purchase import PurchaseOrder, PurchaseOrderView
from stoqlib.domain.receiving import (ReceivingOrder, ReceivingOrderItem,
                                      get_receiving_items_by_purchase_order)

_ = stoqlib_gettext


#
# Wizard Steps
#


class PurchaseSelectionStep(BaseWizardStep):
    gladefile = 'PurchaseSelectionStep'

    def __init__(self, wizard, store):
        self._next_step = None
        BaseWizardStep.__init__(self, store, wizard)
        self.setup_slaves()

    def _refresh_next(self, validation_value):
        has_selection = self.search.results.get_selected() is not None
        self.wizard.refresh_next(has_selection)

    def _create_search(self):
        self.search = StoqlibSearchSlaveDelegate(self._get_columns(),
                                         restore_name=self.__class__.__name__)
        self.search.enable_advanced_search()
        self.attach_slave('searchbar_holder', self.search)
        self.executer = StoqlibQueryExecuter(self.store)
        self.search.set_query_executer(self.executer)
        self.executer.set_table(PurchaseOrderView)
        self.executer.add_query_callback(self.get_extra_query)
        self._create_filters()
        self.search.results.connect('selection-changed',
                                    self._on_results__selection_changed)
        self.search.results.connect('row-activated',
                                    self._on_results__row_activated)
        self.search.focus_search_entry()

    def _create_filters(self):
        self.search.set_text_field_columns(['supplier_name'])

    def get_extra_query(self, states):
        return PurchaseOrderView.status == PurchaseOrder.ORDER_CONFIRMED

    def _get_columns(self):
        return [SearchColumn('identifier', title=_('Number'), sorted=True,
                             data_type=int, width=80),
                SearchColumn('open_date', title=_('Date Started'),
                             data_type=datetime.date, width=100),
                SearchColumn('expected_receival_date', data_type=datetime.date,
                             title=_('Expected Receival'), visible=False),
                SearchColumn('supplier_name', title=_('Supplier'),
                             data_type=str, searchable=True, width=130,
                             expand=True),
                SearchColumn('ordered_quantity', title=_('Qty Ordered'),
                             data_type=Decimal, width=110,
                             format_func=format_quantity),
                SearchColumn('received_quantity', title=_('Qty Received'),
                             data_type=Decimal, width=145,
                             format_func=format_quantity),
                SearchColumn('total', title=_('Order Total'),
                             data_type=currency, width=120)]

    def _update_view(self):
        has_selection = self.search.results.get_selected() is not None
        self.details_button.set_sensitive(has_selection)

    #
    # WizardStep hooks
    #

    def post_init(self):
        self._update_view()
        self.register_validate_function(self._refresh_next)
        self.force_validation()

    def next_step(self):
        self.search.save_columns()
        selected = self.search.results.get_selected()
        purchase = selected.purchase

        # We cannot create the model in the wizard since we haven't
        # selected a PurchaseOrder yet which ReceivingOrder depends on
        # Create the order here since this is the first place where we
        # actually have a purchase selected
        if not self.wizard.model:
            self.wizard.model = self.model = ReceivingOrder(
                responsible=api.get_current_user(self.store),
                supplier=purchase.supplier, invoice_number=None,
                branch=purchase.branch, purchase=purchase,
                store=self.store)

        # Remove all the items added previously, used if we hit back
        # at any point in the wizard.
        if self.model.purchase != purchase:
            self.model.remove_items()
            # This forces ReceivingOrderProductStep to create a new model
            self._next_step = None

        if selected:
            self.model.purchase = purchase
            self.model.branch = purchase.branch
            self.model.supplier = purchase.supplier
            self.model.transporter = purchase.transporter
        else:
            self.model.purchase = None

        # FIXME: Improve the infrastructure to avoid this local caching of
        #        Wizard steps.
        if not self._next_step:
            # Remove all the items added previously, used if we hit back
            # at any point in the wizard.
            self._next_step = ReceivingOrderItemStep(self.wizard,
                                                     self, self.store,
                                                     self.model)
        return self._next_step

    def has_previous_step(self):
        return False

    def setup_slaves(self):
        self._create_search()

    #
    # Kiwi callbacks
    #

#     def on_searchbar_activate(self, slave, objs):
#         """Use this callback with SearchBar search-activate signal"""
#         self.results.add_list(objs, clear=True)
#         has_selection = self.results.get_selected() is not None
#         self.wizard.refresh_next(has_selection)

    def _on_results__selection_changed(self, results, purchase_order_view):
        self.force_validation()
        self._update_view()

    def _on_results__row_activated(self, results, purchase_order_view):
        run_dialog(PurchaseDetailsDialog, self.wizard, self.store,
                   model=purchase_order_view.purchase)

    def on_details_button__clicked(self, *args):
        selected = self.search.results.get_selected()
        if not selected:
            raise ValueError('You should have one order selected '
                             'at this point, got nothing')
        run_dialog(PurchaseDetailsDialog, self.wizard, self.store,
                   model=selected.purchase)


class ReceivingOrderItemStep(SellableItemStep):
    model_type = ReceivingOrder
    item_table = ReceivingOrderItem
    summary_label_text = "<b>%s</b>" % api.escape(_('Total Received:'))
    item_editor = ReceivingItemEditor

    def _on_purchase_item_selection_changed(self, klist, items):
        if items and self._image_viewer:
            sellable = items[0].purchase_item.sellable
            self._image_viewer.set_sellable(sellable)

    def _open_image_viewer(self):
        self._image_viewer = SellableImageViewer()
        self._image_viewer.toplevel.set_property("visible", True)
        selected = self.slave.klist.get_selected_rows()
        if selected:
            self._image_viewer.set_sellable(selected[0].purchase_item.sellable)

    def _close_image_viewer(self):
        self._image_viewer.destroy()
        self._image_viewer = None

    def _on_show_image_toggled(self, *args):
        if self._image_viewer:
            self._close_image_viewer()
        else:
            self._open_image_viewer()

    #
    # SellableItemStep overrides
    #

    def validate(self, value):
        super(ReceivingOrderItemStep, self).validate(value)
        has_receivings = self.model.get_total() > 0
        self.wizard.refresh_next(value and has_receivings)

    def get_sellable_view_query(self):
        # We do not use the sellable entry in this step, so no action needs to
        # be performed here.
        pass

    #
    # WizardStep hooks
    #

    def on_step_changed(self):
        if self._image_viewer:
            self._show_image_button.set_active(False)

    def setup_slaves(self):
        SellableItemStep.setup_slaves(self)
        self.slave.klist.connect('selection-changed',
                                 self._on_purchase_item_selection_changed)
        self._image_viewer = None
        # FIXME: Enable before release
        #self._show_image_button = gtk.CheckButton(_("Show product image"))
        #self.slave.extra_holder.add(self._show_image_button)
        #self._show_image_button.show()
        #self._show_image_button.connect(
        #    "toggled", self._on_show_image_toggled)

    def post_init(self):
        # Hide the search bar, since it does not make sense to add new
        # items to a receivable order.
        self.hide_item_addition_toolbar()
        self.hide_add_button()
        self.hide_del_button()
        super(ReceivingOrderItemStep, self).post_init()

    def next_step(self):
        return ReceivingInvoiceStep(self.store, self.wizard, self.model, self)

    def get_columns(self):
        return [
            Column('sellable.description', title=_('Description'),
                   data_type=str, expand=True, searchable=True),
            Column('sellable.category_description', title=_('Category'),
                   data_type=str, width=120),
            Column('remaining_quantity', title=_('Qty'), data_type=int,
                   width=90, format_func=format_quantity, expand=True),
            Column('quantity', title=_('Qty to receive'), data_type=int,
                   width=110, format_func=format_quantity),
            Column('unit_description', title=_('Unit'), data_type=str,
                   width=50),
            Column('cost', title=_('Cost'), data_type=currency,
                   format_func=get_formatted_cost, width=90),
            Column('total', title=_('Total'), data_type=currency, width=100)
            ]

    def get_order_item(self, sellable, cost, quantity):
        # Never called in this wizard.
        return

    def get_saved_items(self):
        if not self.model.purchase:
            return []
        return get_receiving_items_by_purchase_order(self.model.purchase,
                                                     self.model)


class ReceivingInvoiceStep(WizardEditorStep):
    gladefile = 'HolderTemplate'
    model_type = ReceivingOrder

    #
    # WizardStep hooks
    #

    def has_next_step(self):
        return False

    def post_init(self):
        self._is_valid = False
        self.invoice_slave = ReceivingInvoiceSlave(self.store, self.model)
        self.invoice_slave.connect('activate', self._on_invoice_slave__activate)
        self.attach_slave("place_holder", self.invoice_slave)
        # Slaves must be focused after being attached
        self.invoice_slave.invoice_number.grab_focus()
        self.register_validate_function(self._validate_func)
        self.force_validation()
        if not self.has_next_step():
            self.wizard.enable_finish()

    def validate_step(self):
        create_freight_payment = self.invoice_slave.create_freight_payment()
        self.model.update_payments(create_freight_payment)
        return self.model

    # Callbacks

    def _validate_func(self, is_valid):
        self._is_valid = is_valid
        self.wizard.refresh_next(is_valid)

    def _on_invoice_slave__activate(self, slave):
        if self._is_valid:
            self.wizard.finish()

#
# Main wizard
#


class ReceivingOrderWizard(BaseWizard):
    title = _("Receive Purchase Order")
    size = (750, 350)
    #help_section = 'purchase-new-receival'

    def __init__(self, store):
        self.model = None
        first_step = PurchaseSelectionStep(self, store)
        BaseWizard.__init__(self, store, first_step, self.model)
        self.next_button.set_sensitive(False)

    #
    # WizardStep hooks
    #

    def finish(self):
        assert self.model
        assert self.model.branch

        # Remove the items that will not be received now.
        for item in self.model.get_items():
            if item.quantity > 0:
                continue
            ReceivingOrderItem.delete(item.id, store=self.store)

        if yesno(_(u'Do you want to print the labels for the received products?'),
                     gtk.RESPONSE_YES, _(u'Print labels'), _(u"Don't print")):
            label_data = run_dialog(SkipLabelsEditor, self, self.store)
            if label_data:
                print_labels(label_data, self.store, self.model.purchase)

        ReceivingOrderWizardFinishEvent.emit(self.model)

        self.retval = self.model
        self.model.confirm()
        self.close()

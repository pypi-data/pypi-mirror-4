# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2010 Async Open Source <http://www.async.com.br>
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
""" Loan wizard"""

from decimal import Decimal
import datetime
import sys

import gtk
from kiwi.currency import currency
from kiwi.datatypes import ValidationError
from kiwi.python import Settable
from kiwi.ui.widgets.entry import ProxyEntry
from kiwi.ui.objectlist import Column, SearchColumn

from stoqlib.api import api
from stoqlib.database.queryexecuter import StoqlibQueryExecuter
from stoqlib.domain.person import (Client, LoginUser,
                                   ClientCategory)
from stoqlib.domain.loan import Loan, LoanItem
from stoqlib.domain.payment.group import PaymentGroup
from stoqlib.domain.sale import Sale
from stoqlib.domain.views import LoanView, ProductFullStockItemView
from stoqlib.lib.formatters import format_quantity
from stoqlib.lib.message import info, yesno
from stoqlib.lib.translation import stoqlib_gettext
from stoqlib.gui.base.dialogs import run_dialog
from stoqlib.gui.base.search import StoqlibSearchSlaveDelegate
from stoqlib.gui.base.wizards import (WizardEditorStep, BaseWizard,
                                      BaseWizardStep)
from stoqlib.gui.dialogs.clientdetails import ClientDetailsDialog
from stoqlib.gui.events import (NewLoanWizardFinishEvent,
                                CloseLoanWizardFinishEvent,
                                LoanItemSelectionStepEvent)
from stoqlib.gui.editors.noteeditor import NoteEditor
from stoqlib.gui.editors.personeditor import ClientEditor
from stoqlib.gui.editors.loaneditor import LoanItemEditor
from stoqlib.gui.printing import print_report
from stoqlib.gui.wizards.abstractwizard import SellableItemStep
from stoqlib.gui.wizards.personwizard import run_person_role_dialog
from stoqlib.gui.wizards.salequotewizard import SaleQuoteItemStep
from stoqlib.reporting.loanreceipt import LoanReceipt

_ = stoqlib_gettext


#
# Wizard Steps
#


class StartNewLoanStep(WizardEditorStep):
    gladefile = 'SalesPersonStep'
    model_type = Loan
    proxy_widgets = ['client', 'salesperson', 'expire_date',
                     'client_category']

    def _setup_widgets(self):
        # Hide total and subtotal
        self.table1.hide()
        self.hbox4.hide()

        # Hide invoice number details
        self.invoice_number_label.hide()
        self.invoice_number.hide()

        # Hide cost center combobox
        self.cost_center_lbl.hide()
        self.cost_center.hide()

        # Responsible combo
        self.salesperson_lbl.set_text(_(u'Responsible:'))
        self.salesperson.model_attribute = 'responsible'
        users = self.store.find(LoginUser, is_active=True)
        self.salesperson.prefill(api.for_person_combo(users))
        self.salesperson.set_sensitive(False)

        self._fill_clients_combo()
        self._fill_clients_category_combo()

        self.expire_date.mandatory = True

        # CFOP combo
        self.cfop_lbl.hide()
        self.cfop.hide()
        self.create_cfop.hide()

        # Transporter/RemovedBy Combo
        self.transporter_lbl.set_text(_(u'Removed By:'))
        self.create_transporter.hide()

        # removed_by widget
        self.removed_by = ProxyEntry(unicode)
        self.removed_by.model_attribute = 'removed_by'
        if 'removed_by' not in self.proxy_widgets:
            self.proxy_widgets.append('removed_by')
        self.removed_by.show()
        self._replace_widget(self.transporter, self.removed_by)

        # Operation Nature widget
        self.operation_nature.hide()
        self.nature_lbl.hide()

    def _fill_clients_combo(self):
        # FIXME: This should not be using a normal ProxyComboEntry,
        #        we need a specialized widget that does the searching
        #        on demand.
        clients = Client.get_active_clients(self.store)
        self.client.prefill(api.for_person_combo(clients))
        self.client.mandatory = True

    def _fill_clients_category_combo(self):
        categories = self.store.find(ClientCategory)
        self.client_category.prefill(api.for_combo(categories, empty=''))

    def _replace_widget(self, old_widget, new_widget):
        # retrieve the position, since we will replace two widgets later.
        parent = old_widget.get_parent()
        top = parent.child_get_property(old_widget, 'top-attach')
        bottom = parent.child_get_property(old_widget, 'bottom-attach')
        left = parent.child_get_property(old_widget, 'left-attach')
        right = parent.child_get_property(old_widget, 'right-attach')
        parent.remove(old_widget)
        parent.attach(new_widget, left, right, top, bottom)
        parent.child_set_property(new_widget, 'y-padding', 3)
        parent.child_set_property(new_widget, 'x-padding', 3)

    #
    # WizardStep hooks
    #

    def post_init(self):
        self.toogle_client_details()
        self.register_validate_function(self.wizard.refresh_next)
        self.force_validation()

    def next_step(self):
        return LoanItemStep(self.wizard, self, self.store, self.model)

    def has_previous_step(self):
        return False

    def setup_proxies(self):
        self._setup_widgets()
        self.proxy = self.add_proxy(self.model,
                                    StartNewLoanStep.proxy_widgets)

    def toogle_client_details(self):
        client = self.client.read()
        self.client_details.set_sensitive(bool(client))

    #
    #   Callbacks
    #

    def on_create_client__clicked(self, button):
        store = api.new_store()
        client = run_person_role_dialog(ClientEditor, self.wizard, store, None)
        retval = store.confirm(client)
        client = self.store.fetch(client)
        store.close()
        if not retval:
            return
        self._fill_clients_combo()
        self.client.select(client)

    def on_client__changed(self, widget):
        self.toogle_client_details()
        client = self.client.get_selected()
        if not client:
            return
        self.client_category.select(client.category)

    def on_expire_date__validate(self, widget, value):
        if value < datetime.date.today():
            msg = _(u"The expire date must be set to today or a future date.")
            return ValidationError(msg)

    def on_notes_button__clicked(self, *args):
        run_dialog(NoteEditor, self.wizard, self.store, self.model, 'notes',
                   title=_("Additional Information"))

    def on_client_details__clicked(self, button):
        client = self.model.client
        run_dialog(ClientDetailsDialog, self.wizard, self.store, client)


class LoanItemStep(SaleQuoteItemStep):
    """ Wizard step for loan items selection """
    model_type = Loan
    item_table = LoanItem
    sellable_view = ProductFullStockItemView
    item_editor = LoanItemEditor

    def _has_stock(self, sellable, quantity):
        storable = sellable.product_storable
        if storable is not None:
            balance = storable.get_balance_for_branch(self.model.branch)
        else:
            balance = Decimal(0)
        return balance >= quantity

    def on_quantity__validate(self, widget, value):
        if value <= 0:
            return ValidationError(_(u'Quantity should be positive.'))

        sellable = self.proxy.model.sellable
        if not self._has_stock(sellable, value):
            return ValidationError(
                _(u'The quantity is greater than the quantity in stock.'))


class LoanSelectionStep(BaseWizardStep):
    gladefile = 'HolderTemplate'

    def __init__(self, wizard, store):
        BaseWizardStep.__init__(self, store, wizard)
        self.setup_slaves()

    def _create_filters(self):
        self.search.set_text_field_columns(['client_name'])

    def _get_columns(self):
        return [SearchColumn('identifier', title=_('#'), sorted=True,
                             data_type=int),
                SearchColumn('responsible_name', title=_(u'Responsible'),
                             data_type=str, expand=True),
                SearchColumn('client_name', title=_(u'Client'),
                             data_type=str, expand=True),
                SearchColumn('open_date', title=_(u'Opened'),
                             data_type=datetime.date),
                SearchColumn('expire_date', title=_(u'Expire'),
                             data_type=datetime.date),
                Column('loaned', title=_(u'Loaned'),
                             data_type=Decimal),
        ]

    def _refresh_next(self, value=None):
        has_selected = self.search.results.get_selected() is not None
        self.wizard.refresh_next(has_selected)

    def get_extra_query(self, states):
        return LoanView.status == Loan.STATUS_OPEN

    def setup_slaves(self):
        self.search = StoqlibSearchSlaveDelegate(self._get_columns(),
                                        restore_name=self.__class__.__name__)
        self.search.enable_advanced_search()
        self.attach_slave('place_holder', self.search)
        self.executer = StoqlibQueryExecuter(self.store)
        self.search.set_query_executer(self.executer)
        self.executer.set_table(LoanView)
        self.executer.add_query_callback(self.get_extra_query)
        self._create_filters()
        self.search.results.connect('selection-changed',
                                    self._on_results_selection_changed)
        self.search.focus_search_entry()

    #
    # WizardStep
    #

    def has_previous_step(self):
        return False

    def post_init(self):
        self.register_validate_function(self._refresh_next)
        self.force_validation()

    def next_step(self):
        loan = self.search.results.get_selected().loan
        # FIXME: For some reason, the loan isn't in self.store
        self.wizard.model = self.store.fetch(loan)
        return LoanItemSelectionStep(self.wizard, self, self.store,
                                     self.wizard.model)

    #
    # Callbacks
    #

    def _on_results_selection_changed(self, widget, selection):
        self._refresh_next()


class LoanItemSelectionStep(SellableItemStep):
    model_type = Loan
    item_table = LoanItem
    cost_editable = False
    summary_label_column = None

    def __init__(self, wizard, previous, store, model):
        super(LoanItemSelectionStep, self).__init__(wizard, previous,
                                                    store, model)
        for item in self.model.loaned_items:
            self.wizard.original_items[item] = Settable(
                quantity=item.quantity,
                sale_quantity=item.sale_quantity,
                return_quantity=item.return_quantity,
                remaining_quantity=item.get_remaining_quantity(),
                )

        LoanItemSelectionStepEvent.emit(self)

    #
    #  SellableItemStep
    #

    def has_next_step(self):
        return False

    def post_init(self):
        super(LoanItemSelectionStep, self).post_init()

        self.hide_add_button()
        self.hide_edit_button()
        self.hide_del_button()
        self.hide_item_addition_toolbar()
        for widget in [self.minimum_quantity_lbl, self.minimum_quantity,
                       self.stock_quantity, self.stock_quantity_lbl]:
            widget.hide()

        self.slave.klist.connect('cell-edited', self._on_klist__cell_edited)
        self.slave.klist.connect('cell-editing-started',
                                 self._on_klist__cell_editing_started)
        self.force_validation()

    def get_columns(self):
        adjustment = gtk.Adjustment(lower=0, upper=sys.maxint, step_incr=1)
        return [
            Column('sellable.code', title=_('Code'),
                   data_type=str, visible=False),
            Column('sellable.barcode', title=_('Barcode'),
                   data_type=str, visible=False),
            Column('sellable.description', title=_('Description'),
                   data_type=str, expand=True),
            Column('quantity', title=_('Loaned'),
                   data_type=Decimal, format_func=format_quantity),
            Column('sale_quantity', title=_('Sold'),
                   data_type=Decimal, format_func=format_quantity,
                   editable=True, spin_adjustment=adjustment),
            Column('return_quantity', title=_('Returned'),
                   data_type=Decimal, format_func=format_quantity,
                   editable=True, spin_adjustment=adjustment),
            Column('remaining_quantity', title=_('Remaining'),
                   data_type=Decimal, format_func=format_quantity),
            Column('price', title=_('Price'), data_type=currency),
            ]

    def get_saved_items(self):
        return self.model.loaned_items

    def validate_step(self):
        any_changed = False
        has_sale_items = False

        for item in self.model.loaned_items:
            original = self.wizard.original_items[item]
            sale_quantity = item.sale_quantity - original.sale_quantity
            if sale_quantity > 0:
                has_sale_items = True

            if item.get_remaining_quantity() < original.remaining_quantity:
                any_changed = True

            # Should not happen!
            assert (item.sale_quantity >= original.sale_quantity or
                    item.return_quantity >= original.return_quantity)
            assert item.quantity >= item.sale_quantity + item.return_quantity

        if self.wizard.require_sale_items and not has_sale_items:
            return False

        # Don't let user finish if he didn't mark anything to return/sale
        return any_changed

    def validate(self, value):
        super(LoanItemSelectionStep, self).validate(value)
        self.wizard.refresh_next(value and self.validate_step())

    #
    #  Callbacks
    #

    def _on_klist__cell_edited(self, klist, obj, attr):
        # FIXME: Even with the adjustment, the user still can type
        # values out of range with the keyboard. Maybe it's kiwi's fault
        if attr in ['sale_quantity', 'return_quantity']:
            value = getattr(obj, attr)
            lower_value = getattr(self.wizard.original_items[obj], attr)
            if value < lower_value:
                setattr(obj, attr, lower_value)

            diff = obj.quantity - obj.return_quantity - obj.sale_quantity
            if diff < 0:
                setattr(obj, attr, value + diff)

        self.force_validation()

    def _on_klist__cell_editing_started(self, klist, obj, attr,
                                        renderer, editable):
        original_item = self.wizard.original_items[obj]

        if attr == 'sale_quantity':
            adjustment = editable.get_adjustment()
            adjustment.set_lower(original_item.sale_quantity)
            adjustment.set_upper(obj.quantity - obj.return_quantity)
        if attr == 'return_quantity':
            adjustment = editable.get_adjustment()
            adjustment.set_lower(original_item.return_quantity)
            adjustment.set_upper(obj.quantity - obj.sale_quantity)


#
# Main wizard
#


class NewLoanWizard(BaseWizard):
    size = (775, 400)
    help_section = 'loan'

    def __init__(self, store, model=None):
        title = self._get_title(model)
        model = model or self._create_model(store)
        if model.status != Loan.STATUS_OPEN:
            raise ValueError('Invalid loan status. It should '
                             'be STATUS_OPEN')

        first_step = StartNewLoanStep(store, self, model)
        BaseWizard.__init__(self, store, first_step, model, title=title,
                            edit_mode=False)

    def _get_title(self, model=None):
        if not model:
            return _('New Loan Wizard')

    def _create_model(self, store):
        loan = Loan(responsible=api.get_current_user(store),
                    branch=api.get_current_branch(store),
                    store=store)
        # Temporarily save the client_category, so it works fine with
        # SaleQuoteItemStep
        loan.client_category = None
        return loan

    def _print_receipt(self, order):
        # we can only print the receipt if the loan was confirmed.
        if yesno(_('Would you like to print the receipt now?'),
                 gtk.RESPONSE_YES, _("Print receipt"), _("Don't print")):
            print_report(LoanReceipt, order)

    #
    # WizardStep hooks
    #

    def finish(self):
        self.model.sync_stock()
        self.retval = self.model
        self.close()
        NewLoanWizardFinishEvent.emit(self.model)
        self._print_receipt(self.model)


class CloseLoanWizard(BaseWizard):
    size = (775, 400)
    title = _(u'Close Loan Wizard')
    help_section = 'loan'

    def __init__(self, store, create_sale=True, require_sale_items=False):
        """
        :param store: A database store
        :param create_sale: If a sale should be created for all the items that
          will be sold from this loan.
        :param require_sale_items: If there should be at least one item sold in
          the Loan. If ``False``, a loan with only returned items will be allowed
          to be confirmed. When ``True``, there should be at least one item in
          the loan that will be sold before confirming this wizard.
        """
        self._create_sale = create_sale
        self._sold_items = []
        self.original_items = {}
        self.require_sale_items = require_sale_items
        first_step = LoanSelectionStep(self, store)
        BaseWizard.__init__(self, store, first_step, model=None,
                            title=self.title, edit_mode=False)

    #
    #  Public API
    #

    def get_sold_items(self):
        """Get items set to be sold on this wizard

        Returns a list of sold |sellables|, the quantity sold of those
        |sellables| and the price it was sold at.

        :returns: a list of tuples (|sellable|, quantity, price)
        """
        return self._sold_items

    #
    # WizardStep hooks
    #

    def finish(self):
        for item in self.model.loaned_items:
            original = self.original_items[item]
            sale_quantity = item.sale_quantity - original.sale_quantity
            if sale_quantity > 0:
                self._sold_items.append(
                    (item.sellable, sale_quantity, item.price))

        if self._create_sale and self._sold_items:
            user = api.get_current_user(self.store)
            sale = Sale(
                store=self.store,
                branch=self.model.branch,
                client=self.model.client,
                salesperson=user.person.salesperson,
                group=PaymentGroup(store=self.store),
                coupon_id=None)

            for sellable, quantity, price in self._sold_items:
                sale.add_sellable(sellable, quantity, price,
                                  # Quantity was already decreased on loan
                                  quantity_decreased=quantity)

            sale.order()
            info(_("Close loan details..."),
                 _("A sale was created from loan items. You can confirm "
                   "that sale in the Till application later."))
        else:
            sale = None

        self.model.sync_stock()
        if self.model.can_close():
            self.model.close()

        self.retval = self.model
        self.close()
        CloseLoanWizardFinishEvent.emit(self.model, sale, self)

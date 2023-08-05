# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005-2009 Async Open Source <http://www.async.com.br>
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
""" Stock Decrease wizard definition """

from decimal import Decimal

import gtk
from kiwi.datatypes import ValidationError
from kiwi.ui.widgets.list import Column

from stoqlib.api import api
from stoqlib.database.orm import AND
from stoqlib.domain.fiscal import CfopData
from stoqlib.domain.person import Branch, Employee
from stoqlib.domain.product import Product, ProductStockItem
from stoqlib.domain.sellable import Sellable
from stoqlib.domain.stockdecrease import StockDecrease, StockDecreaseItem
from stoqlib.lib.message import yesno
from stoqlib.lib.parameters import sysparam
from stoqlib.lib.translation import stoqlib_gettext
from stoqlib.lib.formatters import format_quantity
from stoqlib.gui.base.wizards import WizardEditorStep, BaseWizard
from stoqlib.gui.editors.decreaseeditor import DecreaseItemEditor
from stoqlib.gui.events import StockDecreaseWizardFinishEvent
from stoqlib.gui.printing import print_report
from stoqlib.gui.wizards.abstractwizard import SellableItemStep
from stoqlib.reporting.stockdecreasereceipt import StockDecreaseReceipt

_ = stoqlib_gettext


#
# Wizard Steps
#


class StartStockDecreaseStep(WizardEditorStep):
    gladefile = 'StartStockDecreaseStep'
    model_type = StockDecrease
    proxy_widgets = ('confirm_date',
                     'branch',
                     'reason',
                     'removed_by',
                     'cfop',
                     )

    def _fill_employee_combo(self):
        self.removed_by.prefill(api.for_person_combo(
            Employee.select(connection=self.conn)))

    def _fill_branch_combo(self):
        branches = Branch.get_active_branches(self.conn)
        self.branch.prefill(api.for_person_combo(branches))

    def _fill_cfop_combo(self):
        cfops = CfopData.select(connection=self.conn)
        self.cfop.prefill(api.for_combo(cfops))

    def _setup_widgets(self):
        self.confirm_date.set_sensitive(False)
        self._fill_employee_combo()
        self._fill_branch_combo()
        self._fill_cfop_combo()

    #
    # WizardStep hooks
    #

    def post_init(self):
        self.confirm_date.grab_focus()
        self.table1.set_focus_chain([self.confirm_date, self.branch,
                                     self.removed_by, self.reason, self.cfop])
        self.register_validate_function(self.wizard.refresh_next)
        self.force_validation()

    def next_step(self):
        return DecreaseItemStep(self.wizard, self, self.conn, self.model)

    def has_previous_step(self):
        return False

    def setup_proxies(self):
        self._setup_widgets()
        self.proxy = self.add_proxy(self.model,
                                    self.proxy_widgets)


class DecreaseItemStep(SellableItemStep):
    """ Wizard step for purchase order's items selection """
    model_type = StockDecrease
    item_table = StockDecreaseItem
    summary_label_text = "<b>%s</b>" % api.escape(_('Total Ordered:'))
    summary_label_column = None
    sellable_editable = False

    #
    # Helper methods
    #

    def get_sellable_view_query(self):
        branch = api.get_current_branch(self.conn)
        branch_query = ProductStockItem.q.branch_id == branch.id
        # The stock quantity of consigned products can not be
        # decreased manually. See bug 5212.
        return AND(branch_query,
                   Product.q.consignment == False,
                   Sellable.get_available_sellables_query(self.conn))

    def setup_slaves(self):
        SellableItemStep.setup_slaves(self)
        self.hide_add_button()

        self.cost_label.hide()
        self.cost.hide()
        self.quantity.connect('validate', self._on_quantity__validate)

    #
    # SellableItemStep virtual methods
    #

    def validate(self, value):
        SellableItemStep.validate(self, value)
        can_decrease = self.model.get_items().count()
        self.wizard.refresh_next(can_decrease)

    def get_order_item(self, sellable, cost, quantity):
        item = self.model.add_sellable(sellable, quantity)
        return item

    def get_saved_items(self):
        return list(self.model.get_items())

    def get_columns(self):
        return [
            Column('sellable.code', title=_('Code'), width=100, data_type=str),
            Column('sellable.description', title=_('Description'),
                   data_type=str, expand=True, searchable=True),
            Column('sellable.category_description', title=_('Category'),
                   data_type=str, expand=True, searchable=True),
            Column('quantity', title=_('Quantity'), data_type=float, width=90,
                   format_func=format_quantity),
            Column('sellable.unit_description', title=_('Unit'), data_type=str,
                   width=70),
            ]

    #
    # WizardStep hooks
    #

    def post_init(self):
        SellableItemStep.post_init(self)
        self.slave.set_editor(DecreaseItemEditor)
        self.slave.register_editor_kwargs(all_items=self.slave.klist)
        self._refresh_next()

    def has_next_step(self):
        return False

    def next_step(self):
        return None

    #
    # Callbacks
    #

    def _on_quantity__validate(self, widget, value):
        sellable = self.proxy.model.sellable
        if not sellable:
            return

        if not value or value <= Decimal(0):
            return ValidationError(_(u'Quantity must be greater than zero'))

        storable = sellable.product_storable
        assert storable
        balance = storable.get_balance_for_branch(branch=self.model.branch)
        for i in self.slave.klist:
            if i.sellable == sellable:
                balance -= i.quantity

        if value > balance:
            return ValidationError(
                _(u'Quantity is greater than the quantity in stock.'))


class StockDecreaseWizard(BaseWizard):
    size = (775, 400)
    title = _('Manual Stock Decrease')

    def __init__(self, conn):
        model = self._create_model(conn)

        first_step = StartStockDecreaseStep(conn, self, model)
        BaseWizard.__init__(self, conn, first_step, model)

    def _create_model(self, conn):
        branch = api.get_current_branch(conn)
        user = api.get_current_user(conn)
        employee = user.person.employee
        cfop = sysparam(conn).DEFAULT_STOCK_DECREASE_CFOP
        return StockDecrease(responsible=user,
                             removed_by=employee,
                             branch=branch,
                             status=StockDecrease.STATUS_INITIAL,
                             cfop=cfop,
                             connection=conn)

    def _receipt_dialog(self):
        msg = _('Would you like to print a receipt?')
        if yesno(msg, gtk.RESPONSE_YES,
                 _("Print receipt"), _("Don't print")):
            print_report(StockDecreaseReceipt, self.model)
        return

    #
    # WizardStep hooks
    #

    def finish(self):
        self.retval = self.model
        self.model.confirm()
        self.close()
        StockDecreaseWizardFinishEvent.emit(self.model)
        self._receipt_dialog()

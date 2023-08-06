# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2012 Async Open Source <http://www.async.com.br>
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

import datetime

import mock
from stoqlib.domain.account import Account
from stoqlib.domain.payment.method import CheckData, PaymentMethod
from stoqlib.domain.payment.payment import Payment
from stoqlib.gui.dialogs.paymentchangedialog import PaymentDueDateChangeDialog
from stoqlib.gui.dialogs.paymentcommentsdialog import PaymentCommentsDialog
from stoqlib.gui.editors.paymenteditor import InPaymentEditor
from stoqlib.gui.editors.paymentseditor import SalePaymentsEditor
from stoqlib.gui.search.paymentsearch import CardPaymentSearch
from stoqlib.gui.search.paymentsearch import InPaymentBillCheckSearch
from stoqlib.gui.wizards.renegotiationwizard import PaymentRenegotiationWizard
from stoqlib.reporting.boleto import BillReport
from stoqlib.reporting.paymentsreceipt import InPaymentReceipt

from stoq.gui.receivable import ReceivableApp
from stoq.gui.test.baseguitest import BaseGUITest


class TestReceivable(BaseGUITest):
    @mock.patch('stoq.gui.receivable.run_dialog')
    @mock.patch('stoq.gui.receivable.api.new_store')
    def _check_run_dialog(self, app, action, dialog, new_store,
                          run_dialog):
        new_store.return_value = self.store

        with mock.patch.object(self.store, 'commit'):
            with mock.patch.object(self.store, 'close'):
                self.activate(action)
                self.assertEquals(run_dialog.call_count, 1)
                args, kwargs = run_dialog.call_args
                self.assertEquals(args[0], dialog)
                self.assertEquals(args[1], app)
                self.assertEquals(args[2], self.store)

    def setUp(self):
        BaseGUITest.setUp(self)

    def testInitial(self):
        app = self.create_app(ReceivableApp, u'receivable')
        self.check_app(app, u'receivable')

    def testInitialWithoutPayments(self):
        from stoqlib.domain.till import TillEntry
        from stoqlib.domain.commission import Commission
        from stoqlib.domain.account import AccountTransaction
        from stoqlib.domain.payment.category import PaymentCategory
        # Delete all objects so we have no payments in the database.
        self.clean_domain([CheckData, TillEntry, Commission,
                           AccountTransaction, Payment])

        category = self.create_payment_category(u'Sample category',
                                                PaymentCategory.TYPE_RECEIVABLE)

        app = self.create_app(ReceivableApp, u'receivable')

        # Note that set_message is always called twice (once from
        # stoqlib.gui.base.search and later by stoq.gui.application), so we
        # cannot use assert_called_once_with
        set_message = mock.MagicMock()
        app.main_window.search.set_message = set_message

        app.main_window.main_filter.set_state(None)
        app.main_window.search.refresh()
        set_message.assert_called_with('No payments found.\n\nWould you '
                'like to <a href="new_payment">create a new payment</a>?')

        set_message.reset_mock()
        app.main_window.main_filter.set_state(None, 'Received payments')
        set_message.assert_called_with('No paid payments found.')

        set_message.reset_mock()
        app.main_window.main_filter.set_state(None, 'To receive')
        set_message.assert_called_with('No payments to receive found.')

        set_message.reset_mock()
        app.main_window.main_filter.set_state(None, 'Late payments')
        set_message.assert_called_with('No late payments found.')

        set_message.reset_mock()
        app.main_window.main_filter.set_state(None, category.id)
        set_message.assert_called_with('No payments in the <b>Sample '
         'category</b> category were found.\n\nWould you like to <a '
         'href="new_payment?Sample%20category">create a new payment</a>?')

        # Reset the state to None, since thats the expected by the other tests
        app.main_window.main_filter.set_state(None)

    def create_receivable_sale(self):
        sale = self.create_sale()
        sale.identifier = 12345
        self.add_product(sale)
        sale.order()
        payment = self.add_payments(sale, method_type=u'bill')[0]
        payment.identifier = 67890
        sale.confirm()
        payment.due_date = datetime.datetime(2012, 1, 1)
        #payment.paid_date = datetime.datetime(2012, 2, 2)
        return sale, payment

    def testSelect(self):
        sale, payment = self.create_receivable_sale()
        app = self.create_app(ReceivableApp, u'receivable')
        olist = app.main_window.results
        olist.select(olist[1])
        self.check_app(app, u'receivable-selected')

    @mock.patch('stoq.gui.receivable.run_dialog')
    def testReceive(self, run_dialog):
        sale, payment = self.create_receivable_sale()

        app = self.create_app(ReceivableApp, u'receivable')
        olist = app.main_window.results
        olist.select(olist[3])
        assert olist[3].payment == payment

        with mock.patch('stoq.gui.receivable.api', new=self.fake.api):
            self.activate(app.main_window.Receive)

    @mock.patch('stoq.gui.receivable.run_dialog')
    def testEdit(self, run_dialog):
        sale, payment = self.create_receivable_sale()

        app = self.create_app(ReceivableApp, u'receivable')
        olist = app.main_window.results
        olist.select(olist[3])

        with mock.patch('stoq.gui.receivable.api', new=self.fake.api):
            self.activate(app.main_window.Edit)

        run_dialog.assert_called_once_with(
            SalePaymentsEditor, app.main_window,
            self.store.readonly, sale)

    @mock.patch('stoq.gui.accounts.run_dialog')
    def testChangeDueDate(self, run_dialog):
        sale, payment = self.create_receivable_sale()

        app = self.create_app(ReceivableApp, u'receivable')
        olist = app.main_window.results
        olist.select(olist[3])

        with mock.patch('stoq.gui.accounts.api', new=self.fake.api):
            self.activate(app.main_window.ChangeDueDate)

        run_dialog.assert_called_once_with(
            PaymentDueDateChangeDialog, app.main_window,
            self.store.readonly, payment, sale)

    @mock.patch('stoq.gui.accounts.run_dialog')
    def testDetails(self, run_dialog):
        sale, payment = self.create_receivable_sale()

        app = self.create_app(ReceivableApp, u'receivable')
        olist = app.main_window.results
        olist.select(olist[3])

        with mock.patch('stoq.gui.accounts.api', new=self.fake.api):
            self.activate(app.main_window.Details)

        run_dialog.assert_called_once_with(
            InPaymentEditor, app.main_window,
            self.store.readonly, payment)

    @mock.patch('stoq.gui.accounts.run_dialog')
    def testComments(self, run_dialog):
        sale, payment = self.create_receivable_sale()

        app = self.create_app(ReceivableApp, u'receivable')
        olist = app.main_window.results
        olist.select(olist[3])

        with mock.patch('stoq.gui.accounts.api', new=self.fake.api):
            self.activate(app.main_window.Comments)
        run_dialog.assert_called_once_with(
            PaymentCommentsDialog, app.main_window,
            self.store.readonly, payment)

    @mock.patch('stoq.gui.receivable.run_dialog')
    def testRenegotiate(self, run_dialog):
        sale, payment = self.create_receivable_sale()
        sale.client = self.create_client()

        app = self.create_app(ReceivableApp, u'receivable')
        olist = app.main_window.results
        olist.select(olist[3])

        with mock.patch('stoq.gui.receivable.api', new=self.fake.api):
            self.activate(app.main_window.Renegotiate)

        run_dialog.assert_called_once_with(
            PaymentRenegotiationWizard, app.main_window,
            self.store.readonly, [payment.group])

    @mock.patch('stoq.gui.receivable.print_report')
    def testPrintDocument(self, print_report):
        sale, payment = self.create_receivable_sale()
        sale.client = self.create_client()

        app = self.create_app(ReceivableApp, u'receivable')
        olist = app.main_window.results
        olist.select(olist[3])

        method = PaymentMethod.get_by_name(self.store, u'bill')
        account = self.store.find(Account, description=u'Banco do Brasil').one()
        method.destination_account = account

        with mock.patch('stoq.gui.receivable.api', new=self.fake.api):
            self.activate(app.main_window.PrintDocument)

        print_report.assert_called_once_with(BillReport, [payment])

    def test_can_receive(self):
        sale, payment1 = self.create_receivable_sale()
        payment2 = self.add_payments(sale, method_type=u'bill')[0]
        payment2.identifier = 67891

        app = self.create_app(ReceivableApp, u'receivable')

        olist = app.main_window.results
        payments = list(olist)[-2:]

        for payment in payments:
            payment.status = Payment.STATUS_PENDING
        self.assertTrue(app.main_window._can_receive(payments))

    def test_can_renegotiate(self):
        app = self.create_app(ReceivableApp, u'receivable')
        self.assertFalse(app.main_window._can_renegotiate([]))

    def test_run_dialogs(self):
        app = self.create_app(ReceivableApp, u'receivable')
        self._check_run_dialog(app.main_window,
                               app.main_window.CardPaymentSearch,
                               CardPaymentSearch)
        self._check_run_dialog(app.main_window,
                               app.main_window.BillCheckSearch,
                               InPaymentBillCheckSearch)

    @mock.patch('stoq.gui.receivable.print_report')
    def test_print_receipt(self, print_report):
        sale, payment = self.create_receivable_sale()
        payment.pay()

        app = self.create_app(ReceivableApp, u'receivable')
        olist = app.main_window.results
        olist.select(olist[-1])

        self.activate(app.main_window.PrintReceipt)
        print_report.assert_called_once_with(InPaymentReceipt, payment=payment,
                                             order=sale, date=datetime.date.today())

    @mock.patch('stoq.gui.receivable.ReceivableApp.change_status')
    def test_cancel_payment(self, change_status):
        payment = self.create_payment()
        payment.status = Payment.STATUS_PENDING
        payment.payment_type = Payment.TYPE_IN

        app = self.create_app(ReceivableApp, u'receivable')
        olist = app.main_window.results
        olist.select(olist[-1])

        self.activate(app.main_window.CancelPayment)
        change_status.assert_called_once_with(olist[-1], None,
                                              Payment.STATUS_CANCELLED)

    @mock.patch('stoq.gui.receivable.ReceivableApp.change_status')
    def test_set_not_paid(self, change_status):
        sale, payment = self.create_receivable_sale()
        payment.pay()

        app = self.create_app(ReceivableApp, u'receivable')
        olist = app.main_window.results
        olist.select(olist[-1])

        self.activate(app.main_window.SetNotPaid)
        change_status.assert_called_once_with(olist[-1], sale,
                                              Payment.STATUS_PENDING)

    @mock.patch('stoq.gui.receivable.ReceivableApp.change_due_date')
    def test_change_due_date(self, change_due_date):
        sale, payment = self.create_receivable_sale()

        app = self.create_app(ReceivableApp, u'receivable')
        olist = app.main_window.results
        olist.select(olist[-1])

        self.activate(app.main_window.ChangeDueDate)
        change_due_date.assert_called_once_with(olist[-1], sale)

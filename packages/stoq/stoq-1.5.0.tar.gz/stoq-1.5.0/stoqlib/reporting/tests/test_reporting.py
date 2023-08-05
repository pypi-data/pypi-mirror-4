# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2007-2008 Async Open Source <http://www.async.com.br>
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
## GNU General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
## Author(s): Stoq Team <stoq-devel@async.com.br>
##
""" This module test reporties """

import datetime
from decimal import Decimal
import os
import tempfile
import sys

from nose.exc import SkipTest

from stoqlib.database.runtime import get_current_station
from stoqlib.database.runtime import get_current_branch
from stoqlib.domain.commission import CommissionSource, CommissionView
from stoqlib.domain.payment.method import PaymentMethod
from stoqlib.domain.payment.views import (InPaymentView, OutPaymentView,
                                          InCheckPaymentView,
                                          OutCheckPaymentView)
from stoqlib.domain.person import CallsView
from stoqlib.domain.product import Storable
from stoqlib.domain.purchase import PurchaseOrder
from stoqlib.domain.service import ServiceView
from stoqlib.domain.test.domaintest import DomainTest
from stoqlib.domain.till import Till, TillEntry
from stoqlib.domain.views import ProductFullStockView
from stoqlib.lib.parameters import sysparam
from stoqlib.reporting import tests
from stoqlib.reporting.payments_receipt import (InPaymentReceipt,
                                               OutPaymentReceipt)
from stoqlib.reporting.calls_report import CallsReport
from stoqlib.reporting.payment import (ReceivablePaymentReport,
                                       PayablePaymentReport,
                                       BillCheckPaymentReport)
from stoqlib.reporting.product import ProductReport, ProductPriceReport
from stoqlib.reporting.production import ProductionOrderReport
from stoqlib.reporting.purchase import PurchaseQuoteReport
from stoqlib.reporting.service import ServicePriceReport
from stoqlib.reporting.sale import SaleOrderReport, SalesPersonReport
from stoqlib.reporting.till import TillHistoryReport
from stoqlib.lib.diffutils import diff_pdf_htmls
from stoqlib.lib.pdf import pdftohtml


class TestReport(DomainTest):
    def checkPDF(self, report_class, *args, **kwargs):
        frame = sys._getframe(1)
        basename = frame.f_code.co_name[4:]
        basedir = os.path.join(tests.__path__[0], 'data')
        expected = os.path.join(basedir, '%s.pdf.html' % basename)
        output = os.path.join(basedir, '%s-tmp.pdf.html' % basename)

        if not os.path.isfile(expected):
            with tempfile.NamedTemporaryFile(prefix='stoq-report') as fp_tmp:
                report = report_class(fp_tmp.name, *args, **kwargs)
                report.save()
                with open(expected, 'w') as fp:
                    pdftohtml(fp_tmp.name, fp.name)
            return
        with tempfile.NamedTemporaryFile(prefix='stoq-report') as fp_tmp:
            report = report_class(fp_tmp.name, *args, **kwargs)
            report.save()
            with open(output, 'w') as fp:
                pdftohtml(fp_tmp.name, fp.name)

        # Diff and compare
        diff = diff_pdf_htmls(expected, output)
        os.unlink(output)

        self.failIf(diff, '%s\n%s' % ("Files differ, output:", diff))

    def testPayablePaymentReport(self):
        raise SkipTest('We need a SearchDialog to test this report.')

        out_payments = list(OutPaymentView.select(connection=self.trans))
        for item in out_payments:
            item.payment.due_date = datetime.date(2007, 1, 1)
        self.checkPDF(PayablePaymentReport, out_payments, date=datetime.date(2007, 1, 1))

    def testReceivablePaymentReport(self):
        raise SkipTest('We need a SearchDialog to test this report.')

        payments = InPaymentView.select(connection=self.trans).orderBy('id')
        in_payments = list(payments)
        for item in in_payments:
            item.due_date = datetime.date(2007, 1, 1)
        self.checkPDF(ReceivablePaymentReport, in_payments, date=datetime.date(2007, 1, 1))

    def testPayableBillCheckPaymentReport(self):
        from stoqlib.gui.search.paymentsearch import OutPaymentBillCheckSearch
        search = OutPaymentBillCheckSearch(self.trans)

        out_payments = list(OutCheckPaymentView.select(connection=self.trans))
        for item in out_payments:
            item.due_date = datetime.date(2007, 1, 1)
            search.results.append(item)

        # Resize the columns in order to generate the correct report.
        for column in search.results.get_columns():
            column.width = 90

        self.checkPDF(BillCheckPaymentReport, search.results, list(search.results),
                      date=datetime.date(2007, 1, 1))

    def testReceivableBillCheckPaymentReport(self):
        from stoqlib.gui.search.paymentsearch import InPaymentBillCheckSearch
        search = InPaymentBillCheckSearch(self.trans)

        in_payments = list(InCheckPaymentView.select(connection=self.trans))
        for item in in_payments:
            item.due_date = datetime.date(2007, 1, 1)
            search.results.append(item)

        # Resize the columns in order to generate the correct report.
        for column in search.results.get_columns():
            column.width = 90

        self.checkPDF(BillCheckPaymentReport, search.results, list(search.results),
                      date=datetime.date(2007, 1, 1))

    def testInPaymentReceipt(self):
        payer = self.create_client()
        address = self.create_address()
        address.person = payer.person

        method = PaymentMethod.get_by_name(self.trans, 'money')
        group = self.create_payment_group()
        branch = self.create_branch()
        payment = method.create_inpayment(group, branch, Decimal(100))
        payment.description = "Test receivable account"
        payment.group.payer = payer.person
        payment.set_pending()
        payment.pay()
        payment.get_payment_number_str = lambda: '00036'
        date = datetime.date(2012, 1, 1)

        self.checkPDF(InPaymentReceipt, payment, order=None, date=date)

    def testOutPaymentReceipt(self):
        drawee = self.create_supplier()
        address = self.create_address()
        address.person = drawee.person

        method = PaymentMethod.get_by_name(self.trans, 'money')
        group = self.create_payment_group()
        branch = self.create_branch()
        payment = method.create_outpayment(group, branch, Decimal(100))
        payment.description = "Test payable account"
        payment.group.recipient = drawee.person
        payment.set_pending()
        payment.pay()
        payment.get_payment_number_str = lambda: '00035'
        date = datetime.date(2012, 1, 1)

        self.checkPDF(OutPaymentReceipt, payment, order=None, date=date)

    def testProductReport(self):
        from stoqlib.gui.search.productsearch import ProductSearch
        search = ProductSearch(self.trans)
        search.width = 1000
        # the orderBy clause is only needed by the test
        products = ProductFullStockView.select(connection=self.trans)\
                                       .orderBy('id')
        search.results.add_list(products, clear=True)
        branch_name = self.create_branch('Any').person.name
        self.checkPDF(ProductReport, search.results, list(search.results),
                      branch_name=branch_name,
                      date=datetime.date(2007, 1, 1))

    def testTillHistoryReport(self):
        from stoqlib.gui.dialogs.tillhistory import TillHistoryDialog
        dialog = TillHistoryDialog(self.trans)

        till = Till(station=get_current_station(self.trans),
                    connection=self.trans)
        till.open_till()

        sale = self.create_sale()
        sellable = self.create_sellable()
        sale.add_sellable(sellable, price=100)
        method = PaymentMethod.get_by_name(self.trans, 'bill')
        payment = method.create_inpayment(sale.group, sale.branch, Decimal(100))
        TillEntry(value=25,
                  identifier=20,
                  description="Cash In",
                  payment=None,
                  till=till,
                  branch=till.station.branch,
                  date=datetime.date(2007, 1, 1),
                  connection=self.trans)
        TillEntry(value=-5,
                  identifier=21,
                  description="Cash Out",
                  payment=None,
                  till=till,
                  branch=till.station.branch,
                  date=datetime.date(2007, 1, 1),
                  connection=self.trans)

        TillEntry(value=100,
                  identifier=22,
                  description=sellable.get_description(),
                  payment=payment,
                  till=till,
                  branch=till.station.branch,
                  date=datetime.date(2007, 1, 1),
                  connection=self.trans)
        till_entry = list(TillEntry.selectBy(connection=self.trans, till=till))
        today = datetime.date.today().strftime('%x')
        for item in till_entry:
            if today in item.description:
                date = datetime.date(2007, 1, 1).strftime('%x')
                item.description = item.description.replace(today, date)

            item.date = datetime.date(2007, 1, 1)
            dialog.results.append(item)

        self.checkPDF(TillHistoryReport, dialog.results, list(dialog.results),
                      date=datetime.date(2007, 1, 1))

    def testSalesPersonReport(self):
        sysparam(self.trans).SALE_PAY_COMMISSION_WHEN_CONFIRMED = 1
        salesperson = self.create_sales_person()
        product = self.create_product(price=100)
        sellable = product.sellable

        sale = self.create_sale()
        sale.salesperson = salesperson
        sale.add_sellable(sellable, quantity=1)

        storable = Storable(product=product, connection=self.trans)
        storable.increase_stock(100, get_current_branch(self.trans))

        CommissionSource(sellable=sellable,
                         direct_value=Decimal(10),
                         installments_value=1,
                         connection=self.trans)

        sale.order()

        method = PaymentMethod.get_by_name(self.trans, 'money')
        till = Till.get_last_opened(self.trans)
        method.create_inpayment(sale.group, sale.branch,
                                sale.get_sale_subtotal(),
                                till=till)
        sale.confirm()
        sale.set_paid()

        salesperson_name = salesperson.person.name
        commissions = list(CommissionView.select(connection=self.trans))
        commissions[0].identifier = 1
        commissions[1].identifier = 139

        self.checkPDF(SalesPersonReport, commissions, salesperson_name,
                      date=datetime.date(2007, 1, 1))

    def testSaleOrderReport(self):
        product = self.create_product(price=100)
        sellable = product.sellable
        default_date = datetime.date(2007, 1, 1)
        sale = self.create_sale()
        sale.open_date = default_date
        # workaround to make the sale order number constant.
        sale.get_order_number_str = lambda: '9090'

        sale.add_sellable(sellable, quantity=1)
        storable = Storable(product=product, connection=self.trans)
        storable.increase_stock(100, get_current_branch(self.trans))
        sale.order()
        self.checkPDF(SaleOrderReport, sale, date=default_date)

    def testProductPriceReport(self):
        # the orderBy clause is only needed by the test
        products = ProductFullStockView.select(connection=self.trans)\
                                       .orderBy('id')
        branch_name = self.create_branch('Any').person.name
        self.checkPDF(ProductPriceReport, list(products),
                      branch_name=branch_name, date=datetime.date(2007, 1, 1))

    def testServicePriceReport(self):
        services = ServiceView.select(connection=self.trans).orderBy('id')
        self.checkPDF(ServicePriceReport, list(services),
                      date=datetime.date(2007, 1, 1))

    def testPurchaseQuoteReport(self):
        quoted_item = self.create_purchase_order_item()
        quote = quoted_item.order
        quote.open_date = datetime.date(2007, 1, 1)
        quote.get_order_number_str = lambda: '0028'
        quote.status = PurchaseOrder.ORDER_QUOTING
        self.checkPDF(PurchaseQuoteReport, quote, date=quote.open_date)

    def testProductionOrderReport(self):
        order_item = self.create_production_item()
        order = order_item.order
        order.get_order_number = lambda: '0028'
        service = self.create_production_service()
        service.order = order
        order.open_date = datetime.date(2007, 1, 1)
        self.checkPDF(ProductionOrderReport, order, date=order.open_date)

    def testCallsReport(self):
        from stoqlib.gui.search.callsearch import CallsSearch
        person = self.create_person()
        self.create_call()
        search = CallsSearch(self.trans, person)
        search.width = 1000
        # the orderBy clause is only needed by the test
        calls = CallsView.select(connection=self.trans).orderBy('id')
        search.results.add_list(calls, clear=True)
        self.checkPDF(CallsReport, search.results, list(search.results),
                      date=datetime.date(2011, 1, 1), person=person)

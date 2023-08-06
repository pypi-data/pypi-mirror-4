# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2006-2008 Async Open Source <http://www.async.com.br>
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

from decimal import Decimal

from nose.exc import SkipTest
from stoqdrivers.enum import PaymentMethodType
from stoqdrivers.exceptions import DriverError
from stoqlib.domain.payment.method import PaymentMethod

from ecf.test.ecftest import ECFTest


class TestCouponPrinter(ECFTest):
    def testCloseTill(self):
        self.printer.close_till(Decimal(0))
        self.assertRaises(DriverError, self.printer.close_till, 0)

    def testAddCash(self):
        self.printer.add_cash(Decimal(100))

    def testRemoveCash(self):
        self.printer.remove_cash(Decimal(100))

    def testCancel(self):
        self.printer.cancel()

    def testSummarize(self):
        self.printer.summarize()


class TestFiscalCoupon(ECFTest):
    def setUp(self):
        super(TestFiscalCoupon, self).setUp()

        self.sale = self.create_sale()
        self.coupon = self.printer.create_coupon(self.sale)

    def testAddItemProduct(self):
        raise SkipTest(
            "Producing 'Connection closed error', traceback starting at kiwi. "
            "Just happen when running all tests, not alone")
        product = self.create_product()
        sellable = product.sellable
        item = self.sale.add_sellable(sellable)

        self.assertEqual(self.coupon.add_item(item), -1)

        self.coupon.open()
        self.coupon.add_item(item)

    def testAddItemService(self):
        service = self.create_service()
        sellable = service.sellable
        item = self.sale.add_sellable(sellable)

        self.coupon.open()
        self.coupon.add_item(item)


class _TestFiscalCouponPayments(object):
    def setUp(self):
        super(_TestFiscalCouponPayments, self).setUp()

        self.sale = self.create_sale()
        self.coupon = self.printer.create_coupon(self.sale)

    def _open_and_add(self, product):
        sellable = product.sellable
        item = self.sale.add_sellable(sellable)

        self.coupon.open()
        self.coupon.add_item(item)
        self.coupon.totalize(self.sale)

    def _add_sale_payments(self, sale, constant, method_type):
        method = PaymentMethod.get_by_name(self.store, method_type)
        method.create_inpayment(sale.group, sale.branch,
                                sale.get_total_sale_amount())
        self.sale.order()

    def testSetupPayment(self):
        raise SkipTest(
            "Need to configure %s payment method on fiscal printer" % self.method)
        product = self.create_product()
        self._open_and_add(product)
        self._add_sale_payments(self.sale, self.constant, self.method)
        self.coupon.add_payments(self.sale)


class TestFiscalCouponPaymentsBill(_TestFiscalCouponPayments, ECFTest):
    setUp = _TestFiscalCouponPayments.setUp
    method = u'bill'
    constant = PaymentMethodType.BILL


class TestFiscalCouponPaymentsCheck(_TestFiscalCouponPayments, ECFTest):
    setUp = _TestFiscalCouponPayments.setUp
    method = u'check'
    constant = PaymentMethodType.CHECK


class TestFiscalCouponPaymentsMoney(_TestFiscalCouponPayments, ECFTest):
    setUp = _TestFiscalCouponPayments.setUp
    method = u'money'
    constant = PaymentMethodType.MONEY

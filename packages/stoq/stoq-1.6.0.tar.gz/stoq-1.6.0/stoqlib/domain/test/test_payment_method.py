# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2007-2008 Async Open Source <http://www.async.com.br>
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
from decimal import Decimal

from kiwi import ValueUnset

from stoqlib.database.runtime import get_current_station
from stoqlib.domain.payment.method import PaymentMethod
from stoqlib.domain.payment.payment import Payment
from stoqlib.domain.test.domaintest import DomainTest
from stoqlib.domain.till import Till
from stoqlib.exceptions import TillError
from stoqlib.lib.defaults import quantize


class _TestPaymentMethod:
    def createInPayment(self, till=ValueUnset):
        sale = self.create_sale()
        method = PaymentMethod.get_by_name(self.store, self.method_type)
        return method.create_inpayment(sale.group, sale.branch, Decimal(100),
                                       till=till)

    def createOutPayment(self, till=ValueUnset):
        purchase = self.create_purchase_order()
        method = PaymentMethod.get_by_name(self.store, self.method_type)
        return method.create_outpayment(purchase.group, purchase.branch, Decimal(100),
                                        till=till)

    def createInPayments(self, no=3):
        sale = self.create_sale()
        d = datetime.datetime.today()
        method = PaymentMethod.get_by_name(self.store, self.method_type)
        payments = method.create_inpayments(sale.group, sale.branch, Decimal(100),
                                            [d] * no)
        return payments

    def createOutPayments(self, no=3):
        purchase = self.create_purchase_order()
        d = datetime.datetime.today()
        method = PaymentMethod.get_by_name(self.store, self.method_type)
        payments = method.create_outpayments(purchase.group, purchase.branch, Decimal(100),
                                             [d] * no)
        return payments

    def createPayment(self, payment_type):
        if payment_type == Payment.TYPE_OUT:
            order = self.create_purchase_order()
        elif payment_type == Payment.TYPE_IN:
            order = self.create_sale()
        else:
            order = None

        value = Decimal(100)
        method = PaymentMethod.get_by_name(self.store, self.method_type)
        return method.create_payment(payment_type, order.group, order.branch, value)

    def createPayments(self, payment_type, no=3):
        if payment_type == Payment.TYPE_OUT:
            order = self.create_purchase_order()
        elif payment_type == Payment.TYPE_IN:
            order = self.create_sale()
        else:
            order = None

        value = Decimal(100)
        due_dates = [datetime.datetime.today()] * no
        method = PaymentMethod.get_by_name(self.store, self.method_type)
        return method.create_payments(payment_type, order.group, order.branch, value, due_dates)


class _TestPaymentMethodsBase(_TestPaymentMethod):
    def testCreateInPayment(self):
        payment = self.createInPayment()
        self.failUnless(isinstance(payment, Payment))
        self.assertEqual(payment.value, Decimal(100))
        self.assertEqual(payment.till, Till.get_current(self.store))

        payment_without_till = self.createInPayment(till=None)
        self.failUnless(isinstance(payment, Payment))
        self.assertEqual(payment_without_till.value, Decimal(100))
        self.assertEqual(payment_without_till.till, None)

    def testCreateOutPayment(self):
        payment = self.createOutPayment()
        self.failUnless(isinstance(payment, Payment))
        self.assertEqual(payment.value, Decimal(100))
        self.assertEqual(payment.till, None)

        payment_without_till = self.createOutPayment(till=None)
        self.failUnless(isinstance(payment, Payment))
        self.assertEqual(payment_without_till.value, Decimal(100))
        self.assertEqual(payment_without_till.till, None)

    def testCreateInPayments(self):
        payments = self.createInPayments()
        athird = quantize(Decimal(100) / Decimal(3))
        rest = quantize(Decimal(100) - (athird * 2))
        self.assertEqual(len(payments), 3)
        self.assertEqual(payments[0].value, athird)
        self.assertEqual(payments[1].value, athird)
        self.assertEqual(payments[2].value, rest)

    def testCreateOutPayments(self):
        payments = self.createOutPayments()
        athird = quantize(Decimal(100) / Decimal(3))
        rest = quantize(Decimal(100) - (athird * 2))
        self.assertEqual(len(payments), 3)
        self.assertEqual(payments[0].value, athird)
        self.assertEqual(payments[1].value, athird)
        self.assertEqual(payments[2].value, rest)

    def testCreatePayment(self):
        payment = self.createPayment(Payment.TYPE_IN)
        self.failUnless(isinstance(payment, Payment))
        self.assertEqual(payment.value, Decimal(100))

        payment = self.createPayment(Payment.TYPE_OUT)
        self.failUnless(isinstance(payment, Payment))
        self.assertEqual(payment.value, Decimal(100))

    def testCreatePayments(self):
        payments = self.createPayments(Payment.TYPE_IN)
        self.assertEqual(len(payments), 3)
        athird = quantize(Decimal(100) / Decimal(3))
        rest = quantize(Decimal(100) - (athird * 2))
        self.assertEqual(payments[0].value, athird)
        self.assertEqual(payments[1].value, athird)
        self.assertEqual(payments[2].value, rest)

        payments = self.createPayments(Payment.TYPE_OUT)
        self.assertEqual(len(payments), 3)
        athird = quantize(Decimal(100) / Decimal(3))
        rest = quantize(Decimal(100) - (athird * 2))
        self.assertEqual(payments[0].value, athird)
        self.assertEqual(payments[1].value, athird)
        self.assertEqual(payments[2].value, rest)

    def testDescribePayment(self):
        sale = self.create_sale()
        method = PaymentMethod.get_by_name(self.store, self.method_type)
        desc = method.describe_payment(sale.group)
        self.failUnless(isinstance(desc, unicode))
        self.failUnless(method.description in desc)

        self.assertRaises(AssertionError, method.describe_payment, sale.group, 0)
        self.assertRaises(AssertionError, method.describe_payment, sale.group, 1, 0)
        self.assertRaises(AssertionError, method.describe_payment, sale.group, 2, 1)
        desc = method.describe_payment(sale.group, 123, 456)
        self.failUnless(u'123' in desc, desc)
        self.failUnless(u'456' in desc, desc)
        self.failUnless(u'123/456' in desc, desc)

    def testMaxInPaymnets(self):
        method = PaymentMethod.get_by_name(self.store, self.method_type)
        max = method.max_installments
        self.assertRaises(ValueError, self.createInPayments, max + 1)

    def testMaxOutPaymnets(self):
        method = PaymentMethod.get_by_name(self.store, self.method_type)
        self.createOutPayments(method.max_installments + 1)

    def testSelectable(self):
        method = PaymentMethod.get_by_name(self.store, self.method_type)
        method.selectable()


class TestPaymentMethod(DomainTest, _TestPaymentMethod):
    method_type = u'check'

    def _createUnclosedTill(self):
        till = Till(station=get_current_station(self.store),
                    store=self.store)
        till.open_till()
        yesterday = datetime.date.today() - datetime.timedelta(1)
        till.opening_date = yesterday

    def testCreateOutPaymentUnClosedTill(self):
        self._createUnclosedTill()
        payment = self.createOutPayment()
        self.failUnless(isinstance(payment, Payment))

    def testCreateOutPaymentsUnClosedTill(self):
        # Test for bug 3270
        self._createUnclosedTill()
        self.createOutPayments()

    def testCreateInPaymentUnClosedTill(self):
        self._createUnclosedTill()
        self.assertRaises(TillError, self.createInPayment)

    def testCreateInPaymentsUnClosedTill(self):
        self._createUnclosedTill()
        self.assertRaises(TillError, self.createInPayments)

    def testCreatePaymentUnClosedTill(self):
        self._createUnclosedTill()
        self.assertRaises(TillError, self.createPayment,
                          Payment.TYPE_IN)

        self.createPayment(Payment.TYPE_OUT)

    def testCreatePaymentsUnClosedTill(self):
        self._createUnclosedTill()
        self.assertRaises(TillError, self.createPayments,
                          Payment.TYPE_IN)

        self.createPayments(Payment.TYPE_OUT)

    def testGetActiveMethods(self):
        methods = PaymentMethod.get_active_methods(self.store)
        self.assertTrue(methods)
        self.assertEquals(len(methods), 9)
        self.assertEquals(methods[0].method_name, u'bill')
        self.assertEquals(methods[1].method_name, u'card')
        self.assertEquals(methods[2].method_name, u'check')
        self.assertEquals(methods[3].method_name, u'deposit')
        self.assertEquals(methods[4].method_name, u'money')
        self.assertEquals(methods[5].method_name, u'multiple')
        self.assertEquals(methods[6].method_name, u'online')
        self.assertEquals(methods[7].method_name, u'store_credit')
        self.assertEquals(methods[8].method_name, u'trade')

    def testGetCreditableMethods(self):
        # Incoming payments
        methods = PaymentMethod.get_creatable_methods(
            self.store, Payment.TYPE_IN, separate=False)
        self.assertTrue(methods)
        self.assertEquals(len(methods), 7)
        self.assertEquals(methods[0].method_name, u'bill')
        self.assertEquals(methods[1].method_name, u'card')
        self.assertEquals(methods[2].method_name, u'check')
        self.assertEquals(methods[3].method_name, u'deposit')
        self.assertEquals(methods[4].method_name, u'money')
        self.assertEquals(methods[5].method_name, u'multiple')
        self.assertEquals(methods[6].method_name, u'store_credit')

        methods = PaymentMethod.get_creatable_methods(
            self.store, Payment.TYPE_OUT, separate=False)
        self.assertTrue(methods)
        self.assertEquals(len(methods), 4)
        self.assertEquals(methods[0].method_name, u'bill')
        self.assertEquals(methods[1].method_name, u'check')
        self.assertEquals(methods[2].method_name, u'deposit')
        self.assertEquals(methods[3].method_name, u'money')

    def testGetCreditableMethodsSeparate(self):
        methods = PaymentMethod.get_creatable_methods(
            self.store, Payment.TYPE_IN, separate=True)
        self.assertTrue(methods)
        self.assertEquals(len(methods), 6)
        self.assertEquals(methods[0].method_name, u'bill')
        self.assertEquals(methods[1].method_name, u'card')
        self.assertEquals(methods[2].method_name, u'check')
        self.assertEquals(methods[3].method_name, u'deposit')
        self.assertEquals(methods[4].method_name, u'money')
        self.assertEquals(methods[5].method_name, u'store_credit')

        methods = PaymentMethod.get_creatable_methods(
            self.store, Payment.TYPE_OUT, separate=True)
        self.assertTrue(methods)
        self.assertEquals(len(methods), 4)
        self.assertEquals(methods[0].method_name, u'bill')
        self.assertEquals(methods[1].method_name, u'check')
        self.assertEquals(methods[2].method_name, u'deposit')
        self.assertEquals(methods[3].method_name, u'money')

    def testGetEditableMethods(self):
        methods = PaymentMethod.get_editable_methods(self.store)
        self.assertTrue(methods)
        self.assertEquals(len(methods), 7)
        self.assertEquals(methods[0].method_name, u'bill')
        self.assertEquals(methods[1].method_name, u'card')
        self.assertEquals(methods[2].method_name, u'check')
        self.assertEquals(methods[3].method_name, u'deposit')
        self.assertEquals(methods[4].method_name, u'money')
        self.assertEquals(methods[5].method_name, u'multiple')
        self.assertEquals(methods[6].method_name, u'store_credit')

        methods_names = [m.method_name for m in methods]
        self.assertFalse(u'online' in methods_names)
        self.assertFalse(u'trade' in methods_names)

    def testGetByAccount(self):
        account = self.create_account()
        methods = PaymentMethod.get_by_account(self.store, account)
        self.assertTrue(methods.is_empty())
        PaymentMethod(store=self.store,
                      method_name=u'test',
                      destination_account=account)
        methods = PaymentMethod.get_by_account(self.store, account)
        self.assertFalse(methods.is_empty())


class TestMoney(DomainTest, _TestPaymentMethodsBase):
    method_type = u'money'

    def testCreateInPayments(self):
        pass

    def testCreateOutPayments(self):
        pass

    def testCreatePayments(self):
        pass


class TestCheck(DomainTest, _TestPaymentMethodsBase):
    method_type = u'check'

    def testCheckDataCreated(self):
        payment = self.createInPayment()
        method = PaymentMethod.get_by_name(self.store, self.method_type)
        check_data = method.operation.get_check_data_by_payment(payment)
        self.failUnless(check_data)

    def testBank(self):
        sale = self.create_sale()
        method = PaymentMethod.get_by_name(self.store, self.method_type)
        payment = method.create_outpayment(sale.group, sale.branch, Decimal(10))
        check_data = method.operation.get_check_data_by_payment(payment)
        check_data.bank_account.bank_number = 123
        self.assertEquals(payment.bank_account_number, 123)


class TestBill(DomainTest, _TestPaymentMethodsBase):
    method_type = u'bill'


class TestCard(DomainTest, _TestPaymentMethodsBase):
    method_type = u'card'

    def testCardData(self):
        payment = self.createInPayment()
        method = PaymentMethod.get_by_name(self.store, self.method_type)
        card_data = method.operation.get_card_data_by_payment(payment)
        self.failUnless(card_data)


class TestDeposit(DomainTest, _TestPaymentMethodsBase):
    method_type = u'deposit'

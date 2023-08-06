# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2010 Async Open Source <http://www.async.com.br>
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

from stoqlib.domain.test.domaintest import DomainTest
from stoqlib.database.runtime import get_current_branch
from stoqlib.domain.loan import Loan


class TestLoan(DomainTest):

    def testAddSellable(self):
        loan = self.create_loan()
        sellable = self.create_sellable()
        self.create_storable(product=sellable.product,
                             branch=loan.branch, stock=2)
        loan.add_sellable(sellable, quantity=1, price=10)
        items = list(loan.get_items())
        self.assertEquals(len(items), 1)
        self.failIf(items[0].sellable is not sellable)

    def testCanClose(self):
        loan_item = self.create_loan_item()
        loan = loan_item.loan
        self.assertEquals(loan.status, Loan.STATUS_OPEN)
        self.failIf(loan.can_close())

        loan_item.return_quantity = loan_item.quantity
        self.failUnless(loan.can_close())

    def testClose(self):
        loan_item = self.create_loan_item()
        loan = loan_item.loan
        self.assertEquals(loan.status, Loan.STATUS_OPEN)
        self.failIf(loan.can_close())

        loan_item.return_quantity = loan_item.quantity
        self.failUnless(loan.can_close())
        loan.close()
        self.assertEquals(loan.status, Loan.STATUS_CLOSED)


class TestLoanItem(DomainTest):

    def test_sync_stock(self):
        loan = self.create_loan()
        product = self.create_product()
        branch = get_current_branch(self.store)
        storable = self.create_storable(product, branch, 4)
        loan.branch = branch
        initial = storable.get_balance_for_branch(branch)
        sellable = product.sellable

        # creates a loan with 4 items of the same product
        quantity = 4
        loan_item = loan.add_sellable(sellable, quantity=quantity, price=10)
        loan_item.sync_stock()
        self.assertEquals(loan_item.quantity, quantity)
        self.assertEquals(loan_item.return_quantity, 0)
        self.assertEquals(loan_item.sale_quantity, 0)
        # The quantity loaned items should be removed from stock
        self.assertEquals(
            storable.get_balance_for_branch(branch),
            initial - quantity)

        # Sell one of the loaned items and return one item (leaving 2 in the
        # loan)
        loan_item.return_quantity = 1
        loan_item.sale_quantity = 1
        loan_item.sync_stock()
        self.assertEquals(loan_item.quantity, quantity)
        self.assertEquals(loan_item.return_quantity, 1)
        self.assertEquals(loan_item.sale_quantity, 1)
        # The return_quantity should be returned to the stock
        self.assertEquals(
            storable.get_balance_for_branch(branch),
            initial - quantity + loan_item.return_quantity)

        # Return the 2 remaining products in this loan.
        loan_item.return_quantity += 2
        loan_item.sync_stock()
        self.assertEquals(loan_item.quantity, quantity)
        self.assertEquals(loan_item.return_quantity, 3)
        self.assertEquals(loan_item.sale_quantity, 1)
        # The return_quantity should be returned to the stock
        self.assertEquals(
            storable.get_balance_for_branch(branch),
            initial - quantity + loan_item.return_quantity)

    def test_remaining_quantity(self):
        loan = self.create_loan()
        product = self.create_product()
        branch = get_current_branch(self.store)
        self.create_storable(product, branch, 4)
        loan.branch = branch

        # creates a loan with 4 items of the same product
        loan_item = loan.add_sellable(product.sellable, quantity=4, price=10)
        self.assertEqual(loan_item.get_remaining_quantity(), 4)
        loan_item.sale_quantity = 1
        self.assertEqual(loan_item.get_remaining_quantity(), 3)
        loan_item.return_quantity = 2
        self.assertEqual(loan_item.get_remaining_quantity(), 1)

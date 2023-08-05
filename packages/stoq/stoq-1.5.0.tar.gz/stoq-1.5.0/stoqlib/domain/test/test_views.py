# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2007-2011 Async Open Source <http://www.async.com.br>
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

from stoqlib.database.orm import Viewable
from stoqlib.database.runtime import get_current_branch
from stoqlib.domain.purchase import PurchaseOrder, QuoteGroup
from stoqlib.domain.test.domaintest import DomainTest
from stoqlib.domain.views import AccountView
from stoqlib.domain.views import ProductComponentView
from stoqlib.domain.views import ProductFullStockView
from stoqlib.domain.views import ProductFullStockItemView
from stoqlib.domain.views import QuotationView
from stoqlib.domain.views import SellableCategoryView
from stoqlib.domain.views import SellableFullStockView
from stoqlib.domain.views import SoldItemView
from stoqlib.lib.introspection import get_all_classes


def _get_all_views():
    for klass in get_all_classes('stoqlib/domain'):
        try:
            # Exclude Viewable, since we just want to test it's subclasses
            if not issubclass(klass, Viewable) or klass is Viewable:
                continue
        except TypeError:
            continue

        yield klass


class TestViewsGeneric(DomainTest):
    """Generic tests for views"""

    def _test_view(self, view):
        results_list = list(view.select(connection=self.trans))

        # See if there are no duplicates
        ids_set = set()
        for result in results_list:
            self.assertFalse(result.id in ids_set)
            ids_set.add(result.id)


for view in _get_all_views():
    name = 'test' + view.__name__
    func = lambda s, v=view: TestViewsGeneric._test_view(s, v)
    func.__name__ = name
    setattr(TestViewsGeneric, name, func)
    del func


class TestProductFullStockView(DomainTest):
    def testSelectByBranch(self):
        branch = self.create_branch()
        p1 = self.create_product(branch=branch, stock=1)

        results = ProductFullStockView.select_by_branch(
            None, branch, connection=self.trans)
        self.failUnless(list(results))
        # FIXME: Storm does not support count() with group_by
        #self.assertEquals(results.count(), 1)
        self.assertEquals(len(list(results)), 1)

        results = ProductFullStockView.select_by_branch(
            ProductFullStockView.q.product_id == p1.id,
            branch, connection=self.trans)
        self.failUnless(list(results))
        self.assertEquals(len(list(results)), 1)

    def testUnitDescription(self):
        p1 = self.create_product()
        p1.sellable.unit = self.create_sellable_unit()
        p1.sellable.unit.description = "kg"

        p2 = self.create_product()

        results = ProductFullStockView.select_by_branch(
            ProductFullStockView.q.product_id == p1.id,
            None, connection=self.trans)
        self.failUnless(list(results))
        product_view = results[0]
        self.assertEquals(product_view.get_unit_description(), "kg")

        results = ProductFullStockView.select_by_branch(
            ProductFullStockView.q.product_id == p2.id,
            None, connection=self.trans)
        self.failUnless(list(results))
        product_view = results[0]
        self.assertEquals(product_view.get_unit_description(), "un")

    def testGetProductAndCategoryDescription(self):
        p1 = self.create_product()
        p1.sellable.category = self.create_sellable_category()
        p1.sellable.category.description = "category"

        p2 = self.create_product()

        results = ProductFullStockView.select_by_branch(
            ProductFullStockView.q.product_id == p1.id,
            None, connection=self.trans)
        self.failUnless(list(results))
        pv = results[0]
        desc = pv.get_product_and_category_description()
        self.assertEquals(desc, "[category] Description")

        results = ProductFullStockView.select_by_branch(
            ProductFullStockView.q.product_id == p2.id,
            None, connection=self.trans)
        self.failUnless(list(results))
        pv = results[0]
        desc = pv.get_product_and_category_description()
        self.assertEquals(desc, "Description")

    def testStockCost(self):
        branch = self.create_branch()
        p1 = self.create_product(branch=branch, stock=1)

        p2 = self.create_product()

        results = ProductFullStockView.select_by_branch(
            ProductFullStockView.q.product_id == p1.id,
            None, connection=self.trans)
        self.failUnless(list(results))
        pv = results[0]
        self.assertEquals(pv.stock_cost, 10)

        branch = get_current_branch(self.trans)
        results = ProductFullStockView.select_by_branch(
            ProductFullStockView.q.product_id == p2.id,
            None, connection=self.trans)
        self.failUnless(list(results))
        pv = results[0]
        self.assertEquals(pv.stock_cost, 0)

    def testPrice(self):
        p1 = self.create_product()
        results = ProductFullStockView.select_by_branch(
            ProductFullStockView.q.product_id == p1.id,
            None, connection=self.trans)
        self.failUnless(list(results))
        pv = results[0]
        self.assertEquals(pv.price, 10)

        # Set a sale price
        sellable = p1.sellable
        sellable.on_sale_price = Decimal('5.55')

        # And a interval that includes today
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        sellable.on_sale_start_date = yesterday
        sellable.on_sale_end_date = tomorrow

        results = ProductFullStockView.select_by_branch(
            ProductFullStockView.q.product_id == p1.id,
            None, connection=self.trans)
        self.assertEquals(results[0].price, Decimal('5.55'))

        # Testing with a sale price set, but in the past
        date1 = datetime.date.today() - datetime.timedelta(days=10)
        date2 = datetime.date.today() - datetime.timedelta(days=5)
        sellable.on_sale_start_date = date1
        sellable.on_sale_end_date = date2

        results = ProductFullStockView.select_by_branch(
            ProductFullStockView.q.product_id == p1.id,
            None, connection=self.trans)
        self.assertEquals(results[0].price, 10)

    def test_with_unblocked_sellables_query(self):
        # This is used in the purchase wizard and breaks storm
        from stoqlib.domain.product import ProductSupplierInfo
        from stoqlib.domain.sellable import Sellable

        p1 = self.create_product()
        supplier = self.create_supplier()

        # Product should appear when querying without a supplier
        query = Sellable.get_unblocked_sellables_query(self.trans)
        results = ProductFullStockView.select(query, connection=self.trans)
        self.assertTrue(p1.id in [p.product_id for p in results])

        # But should not appear when querying with a supplier
        query = Sellable.get_unblocked_sellables_query(self.trans,
                                                       supplier=supplier)
        results = ProductFullStockView.select(query, connection=self.trans)
        self.assertFalse(p1.id in [p.id for p in results])

        # Now relate the two
        ProductSupplierInfo(connection=self.trans,
                            supplier=supplier,
                            product=p1,
                            is_main_supplier=True)

        # And it should appear now
        query = Sellable.get_unblocked_sellables_query(self.trans,
                                                       supplier=supplier)
        results = ProductFullStockView.select(query, connection=self.trans)
        self.assertTrue(p1.id in [s.product_id for s in results])

        # But should not appear for a different supplier
        other_supplier = self.create_supplier()
        query = Sellable.get_unblocked_sellables_query(self.trans,
                                                       supplier=other_supplier)
        results = ProductFullStockView.select(query, connection=self.trans)
        self.assertFalse(p1.id in [s.product_id for s in results])


class TestProductComponentView(DomainTest):
    def testSellable(self):
        pc1 = self.create_product_component()
        results = ProductComponentView.select(connection=self.trans)
        self.failUnless(list(results))
        pcv = results[0]
        self.assertEquals(pcv.sellable, pc1.product.sellable)


class TestSellableFullStockView(DomainTest):
    def testSelectByBranch(self):
        branch = self.create_branch()
        p1 = self.create_product(branch=branch, stock=1)
        p2 = self.create_product()

        results = SellableFullStockView.select_by_branch(
            SellableFullStockView.q.product_id == p1.id,
            branch, connection=self.trans)
        self.failUnless(list(results))

        results = SellableFullStockView.select_by_branch(
            ProductFullStockView.q.product_id == p2.id,
            branch, connection=self.trans)
        self.failUnless(list(results))
        # FIXME: Storm does not support count() with group_by
        #self.assertEquals(results.count(), 1)
        self.assertEquals(len(list(results)), 1)

    def testSellable(self):
        branch = self.create_branch()
        p1 = self.create_product(branch=branch, stock=1)

        results = SellableFullStockView.select_by_branch(
            SellableFullStockView.q.product_id == p1.id,
            branch, connection=self.trans)
        self.failUnless(list(results))

        self.assertEquals(results[0].sellable, p1.sellable)

    def testPrice(self):
        branch = self.create_branch()
        p1 = self.create_product(branch=branch, stock=1, price=Decimal('10.15'))
        results = SellableFullStockView.select_by_branch(
            SellableFullStockView.q.product_id == p1.id,
            branch, connection=self.trans)
        self.failUnless(list(results))

        self.assertEquals(results[0].price, Decimal('10.15'))

        # Set a sale price
        sellable = p1.sellable
        sellable.on_sale_price = Decimal('5.55')

        # And a interval that includes today
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        sellable.on_sale_start_date = yesterday
        sellable.on_sale_end_date = tomorrow

        results = SellableFullStockView.select_by_branch(
            SellableFullStockView.q.product_id == p1.id,
            branch, connection=self.trans)
        self.assertEquals(results[0].price, Decimal('5.55'))

        # Testing with a sale price set, but in the past
        date1 = datetime.date.today() - datetime.timedelta(days=10)
        date2 = datetime.date.today() - datetime.timedelta(days=5)
        sellable.on_sale_start_date = date1
        sellable.on_sale_end_date = date2

        results = SellableFullStockView.select_by_branch(
            SellableFullStockView.q.product_id == p1.id,
            branch, connection=self.trans)
        self.assertEquals(results[0].price, Decimal('10.15'))


class TestSellableCategoryView(DomainTest):
    def testCategory(self):
        category = self.create_sellable_category()
        results = SellableCategoryView.select(
            SellableCategoryView.q.id == category.id,
            connection=self.trans)
        self.failUnless(list(results))
        self.assertEquals(results[0].category, category)

    def testGetCommission(self):
        category = self.create_sellable_category()
        results = SellableCategoryView.select(
            SellableCategoryView.q.id == category.id,
            connection=self.trans)
        self.failUnless(list(results))
        self.assertEquals(results[0].get_commission(), None)

        base_category = self.create_sellable_category()
        self.create_commission_source(category=base_category)
        category.category = base_category
        results = SellableCategoryView.select(
            SellableCategoryView.q.id == category.id,
            connection=self.trans)
        self.assertEquals(results[0].get_commission(), 10)

        self.create_commission_source(category=category)
        results = SellableCategoryView.select(
            SellableCategoryView.q.id == category.id,
            connection=self.trans)
        self.assertEquals(results[0].get_commission(), 10)

    def testGetInstallmentsCommission(self):
        category = self.create_sellable_category()
        results = SellableCategoryView.select(
            SellableCategoryView.q.id == category.id,
            connection=self.trans)
        self.failUnless(list(results))
        self.assertEquals(results[0].get_installments_commission(), None)

        base_category = self.create_sellable_category()
        category.category = base_category
        self.create_commission_source(category=base_category)
        results = SellableCategoryView.select(
            SellableCategoryView.q.id == category.id,
            connection=self.trans)
        self.assertEquals(results[0].get_installments_commission(), 1)

        self.create_commission_source(category=category)
        results = SellableCategoryView.select(
            SellableCategoryView.q.id == category.id,
            connection=self.trans)
        self.assertEquals(results[0].get_installments_commission(), 1)


class TestQuotationView(DomainTest):
    def testGroupQuotationPurchase(self):
        order = self.create_purchase_order()
        quote = QuoteGroup(connection=self.trans, branch=order.branch)
        order.status = PurchaseOrder.ORDER_QUOTING
        quote.add_item(order)

        self.assertEqual(order.status, PurchaseOrder.ORDER_QUOTING)
        quotations = quote.get_items()
        self.assertEqual(quotations.count(), 1)

        self.assertFalse(quotations[0].is_closed())
        quotations[0].close()

        results = QuotationView.select(
                QuotationView.q.id == quotations[0].id, connection=self.trans)
        self.failUnless(list(results))
        self.assertEquals(results.count(), 1)
        self.assertEquals(results[0].group, quote)
        self.assertEquals(results[0].quotation, quotations[0])
        self.assertEquals(results[0].purchase, order)


class TestSoldItemView(DomainTest):
    def testSelectByBranchData(self):
        branch = get_current_branch(self.trans)
        sale = self.create_sale()
        sale.branch = branch
        sellable = self.add_product(sale)
        sale.order()
        self.add_payments(sale, method_type='money')
        sale.confirm()

        results = SoldItemView.select_by_branch_date(None, None, None,
                                                     connection=self.trans)
        self.failUnless(results)

        results = SoldItemView.select_by_branch_date(None, branch, None,
                                                     connection=self.trans)
        self.failUnless(results)

        results = SoldItemView.select_by_branch_date(
            SoldItemView.q.id == sellable.id, branch, None,
            connection=self.trans)
        # FIXME: Storm does not support count() with group_by
        #self.assertEquals(results.count(), 1)
        self.assertEquals(len(list(results)), 1)

        today = datetime.date.today()
        results = SoldItemView.select_by_branch_date(
            SoldItemView.q.id == sellable.id, None, today,
            connection=self.trans)
        self.assertEquals(len(list(results)), 1)

        yesterday = today - datetime.timedelta(days=1)
        results = SoldItemView.select_by_branch_date(
            SoldItemView.q.id == sellable.id, None, (yesterday, today),
            connection=self.trans)
        self.assertEquals(len(list(results)), 1)

        yesterday = today - datetime.timedelta(days=1)
        results = SoldItemView.select_by_branch_date(
            None, None, (yesterday, today),
            connection=self.trans)

        self.failUnless(results)

    def testAverageCost(self):
        sale = self.create_sale()
        sellable = self.add_product(sale)
        sale.order()
        self.add_payments(sale, method_type='money')
        sale.confirm()

        results = SoldItemView.select(
            SoldItemView.q.id == sellable.id,
            connection=self.trans)
        self.failUnless(results)
        self.assertEquals(results[0].average_cost, 0)


class TestAccountView(DomainTest):
    def testAccount(self):
        account = self.create_account()
        results = AccountView.select(AccountView.q.id == account.id,
                                     connection=self.trans)
        self.failUnless(list(results))
        self.assertEquals(results[0].account, account)

    def testParentAccount(self):
        account = self.create_account()
        account.parent = self.create_account()
        results = AccountView.select(AccountView.q.id == account.id,
                                     connection=self.trans)
        self.failUnless(list(results))
        self.assertEquals(results[0].parent_account, account.parent)

    def testMatches(self):
        account = self.create_account()
        account.parent = self.create_account()
        results = AccountView.select(AccountView.q.id == account.id,
                                     connection=self.trans)
        self.failUnless(list(results))
        self.failUnless(results[0].matches(account.id))
        self.failUnless(results[0].matches(account.parent.id))

    def testGetCombinedValue(self):
        a1 = self.create_account()
        a2 = self.create_account()
        results = AccountView.select(AccountView.q.id == a1.id,
                                     connection=self.trans)
        self.failUnless(list(results))
        self.assertEquals(results[0].get_combined_value(), 0)

        t1 = self.create_account_transaction(a1, 1)
        t1.source_account = a1
        t1.account = a2
        t1.sync()
        t2 = self.create_account_transaction(a1, 9)
        t2.source_account = a1
        t2.account = a2
        t2.sync()

        results = AccountView.select(AccountView.q.id == a1.id,
                                     connection=self.trans)
        self.failUnless(list(results))
        self.assertEquals(results.count(), 1)
        # The negative sum of t1 and t2
        self.assertEquals(results[0].get_combined_value(), -10)

        t3 = self.create_account_transaction(a2, 10)
        t3.source_account = a2
        t3.account = a1
        t3.sync()
        t4 = self.create_account_transaction(a2, 90)
        t4.source_account = a2
        t4.account = a1
        t4.sync()

        results = AccountView.select(AccountView.q.id == a1.id,
                                     connection=self.trans)
        self.failUnless(list(results))
        self.assertEquals(results.count(), 1)
        # The negative sum of t1 and t2 plus the sum of t3 and t4
        self.assertEquals(results[0].get_combined_value(), 90)

    def testRepr(self):
        a1 = self.create_account()
        results = AccountView.select(AccountView.q.id == a1.id,
                                     connection=self.trans)
        self.failUnless(list(results))
        self.assertEquals(repr(results[0]), '<AccountView Test Account>')


class TestProductFullStockItemView(DomainTest):

    def testSelect(self):
        from stoqlib.domain.product import Product
        product = Product.select(connection=self.trans)[0]

        order = self.create_purchase_order()
        order.add_item(product.sellable, 1)
        order.status = PurchaseOrder.ORDER_CONFIRMED

        order2 = self.create_purchase_order()
        order2.add_item(product.sellable, 4)
        order2.status = PurchaseOrder.ORDER_CONFIRMED

        # This viewable should return only one item for each existing product,
        # event if there is more than one purchase order for the product.
        results = ProductFullStockItemView.select(connection=self.trans)
        ids = [r.id for r in results]
        self.assertEquals(ids.count(product.sellable.id), 1)

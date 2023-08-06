# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2006-2012 Async Open Source <http://www.async.com.br>
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
""" This module test all class in stoqlib/domain/product.py """

from decimal import Decimal
import datetime

# Import domaintest first so that externals is setup properly
from stoqlib.domain.test.domaintest import DomainTest
from stoqlib.database.runtime import get_current_branch, new_store
from stoqlib.domain.events import (ProductCreateEvent, ProductEditEvent,
                                   ProductRemoveEvent)
from stoqlib.domain.payment.method import PaymentMethod
from stoqlib.domain.product import (ProductSupplierInfo, Product,
                                    ProductHistory, ProductComponent,
                                    ProductQualityTest, Storable,
                                    StockTransactionHistory)
from stoqlib.domain.production import (ProductionOrder, ProductionProducedItem,
                                       ProductionItemQualityResult)
from stoqlib.domain.purchase import PurchaseOrder
from stoqlib.domain.sellable import Sellable


class TestProductSupplierInfo(DomainTest):

    def testGetName(self):
        product = self.create_product()
        supplier = self.create_supplier()
        info = ProductSupplierInfo(store=self.store,
                                   product=product,
                                   supplier=supplier)
        self.assertEqual(info.get_name(), supplier.get_description())

    def testDefaultLeadTimeValue(self):
        product = self.create_product()
        supplier = self.create_supplier()
        info = ProductSupplierInfo(store=self.store,
                                   product=product,
                                   supplier=supplier)
        default_lead_time = 1
        self.assertEqual(info.lead_time, default_lead_time)


class _ProductEventData(object):

    def __init__(self):
        self.reset()

    def reset(self):
        self.product = None
        self.emmit_count = 0
        self.was_created = False
        self.was_edited = False
        self.was_deleted = False

    def on_create(self, product, **kwargs):
        self.product = product
        self.was_created = True
        self.emmit_count += 1

    def on_edit(self, product, **kwargs):
        self.product = product
        self.was_edited = True
        self.emmit_count += 1

    def on_delete(self, product, **kwargs):
        self.product = product
        self.was_deleted = True
        self.emmit_count += 1


class TestProduct(DomainTest):

    def setUp(self):
        DomainTest.setUp(self)
        sellable = self.create_sellable()
        self.product = Product(sellable=sellable,
                               store=self.store)

    def test_get_main_supplier_info(self):
        self.failIf(self.product.get_main_supplier_info())
        supplier = self.create_supplier()
        ProductSupplierInfo(store=self.store, supplier=supplier,
                            product=self.product, is_main_supplier=True)
        self.failUnless(self.product.get_main_supplier_info())

    def testGetComponents(self):
        self.assertEqual(list(self.product.get_components()), [])

        components = []
        for i in range(3):
            component = self.create_product()
            product_component = ProductComponent(product=self.product,
                                                 component=component,
                                                 store=self.store)
            components.append(product_component)
        self.assertEqual(list(self.product.get_components()),
                        components)

    def testHasComponents(self):
        self.assertFalse(self.product.has_components())

        component = self.create_product()
        ProductComponent(product=self.product,
                         component=component,
                         store=self.store)
        self.assertTrue(self.product.has_components())

    def testGetProductionCost(self):
        product = self.create_product()
        sellable = product.sellable
        sellable.cost = 50
        production_cost = sellable.cost
        self.assertEqual(product.get_production_cost(), production_cost)

    def testIsComposedBy(self):
        component = self.create_product()
        self.assertEqual(self.product.is_composed_by(component), False)

        ProductComponent(product=self.product, component=component,
                         store=self.store)
        self.assertEqual(self.product.is_composed_by(component), True)

        component2 = self.create_product()
        ProductComponent(product=component, component=component2,
                         store=self.store)
        self.assertEqual(self.product.is_composed_by(component2), True)
        self.assertEqual(component.is_composed_by(component2), True)

        component3 = self.create_product()
        ProductComponent(product=self.product, component=component3,
                         store=self.store)
        self.assertEqual(self.product.is_composed_by(component3), True)
        self.assertEqual(component.is_composed_by(component3), False)
        self.assertEqual(component2.is_composed_by(component3), False)

    def testSuppliers(self):
        product = self.create_product()
        supplier = self.create_supplier()

        info = ProductSupplierInfo(store=self.store,
                                   product=product,
                                   supplier=supplier)

        suppliers = list(product.get_suppliers_info())

        # self.create_product already adds a supplier. so here we must have 2
        self.assertEqual(len(suppliers), 2)
        self.assertEqual(info in suppliers, True)

        # product.suppliers should behave just like get_suppliers_info()
        self.assertEqual(len(list(product.suppliers)), 2)
        self.assertEqual(info in product.suppliers, True)

        self.assertEqual(product.is_supplied_by(supplier), True)

    def testCanRemove(self):
        product = self.create_product()
        storable = Storable(product=product, store=self.store)
        self.assertTrue(product.can_remove())

        storable.increase_stock(1, get_current_branch(self.store), 0, 0)
        self.assertFalse(product.can_remove())

        # Product was sold.
        sale = self.create_sale()
        sale.add_sellable(product.sellable, quantity=1, price=10)

        method = PaymentMethod.get_by_name(self.store, u'money')
        method.create_inpayment(sale.group, sale.branch, sale.get_sale_subtotal())

        sale.order()
        sale.confirm()

        self.assertFalse(product.can_remove())

        # Product is a component.
        from stoqlib.domain.product import ProductComponent
        product = self.create_product(10)
        component = self.create_product(5)
        Storable(product=component, store=self.store)
        self.assertTrue(component.can_remove())

        ProductComponent(product=product,
                         component=component,
                         store=self.store)

        self.assertFalse(component.can_remove())

        # Product is used in a production.
        from stoqlib.domain.production import ProductionItem
        product = self.create_product()
        Storable(product=product, store=self.store)
        self.assertTrue(product.can_remove())
        order = self.create_production_order()
        ProductionItem(product=product,
                       order=order,
                       quantity=1,
                       store=self.store)

        self.assertFalse(product.can_remove())

    def testRemove(self):
        product = self.create_product()
        Storable(product=product, store=self.store)

        total = self.store.find(Product, id=product.id).count()
        self.assertEquals(total, 1)

        product.remove()
        total = self.store.find(Product, id=product.id).count()
        self.assertEquals(total, 0)

    def testIncreaseDecreaseStock(self):
        branch = get_current_branch(self.store)
        product = self.create_product()
        storable = Storable(product=product, store=self.store)
        stock_item = storable.get_stock_item(branch)
        self.failIf(stock_item is not None)

        storable.increase_stock(1, branch, 0, 0)
        stock_item = storable.get_stock_item(branch)
        self.assertEquals(stock_item.stock_cost, 0)

        storable.increase_stock(1, branch, 0, 0, unit_cost=10)
        stock_item = storable.get_stock_item(branch)
        self.assertEquals(stock_item.stock_cost, 5)

        stock_item = storable.decrease_stock(1, branch, 0, 0)
        self.assertEquals(stock_item.stock_cost, 5)

        storable.increase_stock(1, branch, 0, 0)
        stock_item = storable.get_stock_item(branch)
        self.assertEquals(stock_item.stock_cost, 5)

        storable.increase_stock(2, branch, 0, 0, unit_cost=15)
        stock_item = storable.get_stock_item(branch)
        self.assertEquals(stock_item.stock_cost, 10)

    def test_lead_time(self):
        product = self.create_product()
        Storable(product=product, store=self.store)
        branch = get_current_branch(self.store)

        supplier1 = self.create_supplier()
        ProductSupplierInfo(store=self.store, product=product,
                            supplier=supplier1, lead_time=10)

        self.assertEqual(product.get_max_lead_time(1, branch), 10)

        supplier2 = self.create_supplier()
        ProductSupplierInfo(store=self.store, product=product,
                            supplier=supplier2, lead_time=20)
        self.assertEqual(product.get_max_lead_time(1, branch), 20)

        # Now for composed products
        product = self.create_product(create_supplier=False)
        product.is_composed = True
        product.production_time = 5
        Storable(product=product, store=self.store)

        component = self.create_product(create_supplier=False)
        Storable(product=component, store=self.store)
        ProductSupplierInfo(store=self.store, product=component,
                            supplier=supplier1, lead_time=7)
        self.assertEqual(component.get_max_lead_time(1, branch), 7)

        pc = ProductComponent(product=product, component=component, quantity=1,
                         store=self.store)

        self.assertEqual(product.get_max_lead_time(1, branch), 12)

        # Increase the component stock
        component.storable.increase_stock(1, branch, 0, 0)

        self.assertEqual(product.get_max_lead_time(1, branch), 5)

        # Increase the quantity required:
        pc.quantity = 2
        self.assertEqual(product.get_max_lead_time(1, branch), 12)


class TestProductSellableItem(DomainTest):

    def testSell(self):
        sale = self.create_sale()
        sellable = Sellable(store=self.store)
        sellable.barcode = u'xyz'
        product = Product(sellable=sellable, store=self.store)
        sale_item = sale.add_sellable(product.sellable)
        branch = get_current_branch(self.store)
        storable = self.create_storable(product, branch, 2)

        stock_item = storable.get_stock_item(branch)
        assert stock_item is not None
        current_stock = stock_item.quantity
        if current_stock:
            storable.decrease_stock(current_stock, branch, 0, 0)
        assert not storable.get_stock_item(branch).quantity
        sold_qty = 2
        storable.increase_stock(sold_qty, branch, 0, 0)
        assert storable.get_stock_item(branch) is not None
        assert storable.get_stock_item(branch).quantity == sold_qty
        # now setting the proper sold quantity in the sellable item
        sale_item.quantity = sold_qty
        sale_item.sell(branch)
        assert not storable.get_stock_item(branch).quantity


class TestProductHistory(DomainTest):

    def testAddReceivedQuantity(self):
        order_item = self.create_receiving_order_item()
        order_item.receiving_order.purchase.status = PurchaseOrder.ORDER_PENDING
        order_item.receiving_order.purchase.confirm()
        self.failIf(
            self.store.find(ProductHistory,
                            sellable=order_item.sellable).one())
        order_item.receiving_order.confirm()
        prod_hist = self.store.find(ProductHistory,
                                    sellable=order_item.sellable).one()
        self.failUnless(prod_hist)
        self.assertEqual(prod_hist.quantity_received,
                         order_item.quantity)

    def testAddSoldQuantity(self):
        sale = self.create_sale()
        sellable = self.create_sellable()
        sellable.status = Sellable.STATUS_AVAILABLE
        product = sellable.product
        branch = get_current_branch(self.store)
        self.create_storable(product, branch, 100)
        sale_item = sale.add_sellable(sellable, quantity=5)

        method = PaymentMethod.get_by_name(self.store, u'money')
        method.create_inpayment(sale.group, sale.branch, sale.get_sale_subtotal())

        self.failIf(self.store.find(ProductHistory,
                                    sellable=sellable).one())
        sale.order()
        sale.confirm()
        prod_hist = self.store.find(ProductHistory, sellable=sellable).one()
        self.failUnless(prod_hist)
        self.assertEqual(prod_hist.quantity_sold, 5)
        self.assertEqual(prod_hist.quantity_sold,
                         sale_item.quantity)

    def testAddTransferedQuantity(self):
        qty = 10
        order = self.create_transfer_order()
        transfer_item = self.create_transfer_order_item(order, quantity=qty)
        self.failIf(self.store.find(ProductHistory,
                                    sellable=transfer_item.sellable).one())

        order.send_item(transfer_item)
        order.receive()
        prod_hist = self.store.find(ProductHistory,
                                    sellable=transfer_item.sellable).one()
        self.failUnless(prod_hist)
        self.assertEqual(prod_hist.quantity_transfered, qty)


class TestProductQuality(DomainTest):

    def test_quality_tests(self):
        product = self.create_product()
        Storable(product=product, store=self.store)

        # There are still no tests for this product
        self.assertEqual(product.quality_tests.count(), 0)

        test1 = ProductQualityTest(store=self.store, product=product,
                                   test_type=ProductQualityTest.TYPE_BOOLEAN,
                                   success_value=u'True')
        # Now there sould be one
        self.assertEqual(product.quality_tests.count(), 1)
        # and it should be the one we created
        self.assertTrue(test1 in product.quality_tests)

        # Different product
        product2 = self.create_product()
        Storable(product=product2, store=self.store)

        # With different test
        test2 = ProductQualityTest(store=self.store, product=product2,
                                   test_type=ProductQualityTest.TYPE_BOOLEAN,
                                   success_value=u'True')

        # First product still should have only one
        self.assertEqual(product.quality_tests.count(), 1)
        # And it should not be the second test.
        self.assertTrue(test2 not in product.quality_tests)

    def test_boolean_value(self):
        product = self.create_product()
        bool_test = ProductQualityTest(store=self.store, product=product,
                                   test_type=ProductQualityTest.TYPE_BOOLEAN)
        bool_test.set_boolean_value(True)
        self.assertEqual(bool_test.get_boolean_value(), True)
        self.assertTrue(bool_test.result_value_passes(True))
        self.assertFalse(bool_test.result_value_passes(False))

        bool_test.set_boolean_value(False)
        self.assertEqual(bool_test.get_boolean_value(), False)
        self.assertTrue(bool_test.result_value_passes(False))
        self.assertFalse(bool_test.result_value_passes(True))

        self.assertRaises(AssertionError, bool_test.get_range_value)

    def test_decimal_value(self):
        product = self.create_product()
        test = ProductQualityTest(store=self.store, product=product,
                                   test_type=ProductQualityTest.TYPE_DECIMAL)
        test.set_range_value(Decimal(10), Decimal(20))
        self.assertEqual(test.get_range_value(), (Decimal(10), Decimal(20)))

        self.assertFalse(test.result_value_passes(Decimal('9.99')))
        self.assertTrue(test.result_value_passes(Decimal(10)))
        self.assertTrue(test.result_value_passes(Decimal(15)))
        self.assertTrue(test.result_value_passes(Decimal(20)))
        self.assertFalse(test.result_value_passes(Decimal('20.0001')))
        self.assertFalse(test.result_value_passes(Decimal(30)))

        test.set_range_value(Decimal(30), Decimal(40))
        self.assertEqual(test.get_range_value(), (Decimal(30), Decimal(40)))
        self.assertTrue(test.result_value_passes(Decimal(30)))

        # Negative values
        test.set_range_value(Decimal(-5), Decimal(5))
        self.assertEqual(test.get_range_value(), (Decimal(-5), Decimal(5)))

        self.assertRaises(AssertionError, test.get_boolean_value)

    def test_can_remove(self):
        product = self.create_product()
        test = ProductQualityTest(store=self.store, product=product)

        # Test has never been used
        self.assertTrue(test.can_remove())

        order = self.create_production_order()
        user = self.create_user()
        item = ProductionProducedItem(product=product,
                                      order=order,
                                      produced_by=user,
                                      produced_date=datetime.date.today(),
                                      serial_number=1,
                                      store=self.store)
        self.assertTrue(test.can_remove())

        # Test has been used in a production
        ProductionItemQualityResult(produced_item=item,
                                    quality_test=test,
                                    tested_by=user,
                                    result_value=u'True',
                                    test_passed=True,
                                    store=self.store)
        self.assertFalse(test.can_remove())


class TestProductEvent(DomainTest):
    def testCreateEvent(self):
        store_list = []
        p_data = _ProductEventData()
        ProductCreateEvent.connect(p_data.on_create)
        ProductEditEvent.connect(p_data.on_edit)
        ProductRemoveEvent.connect(p_data.on_delete)

        try:
            # Test product being created
            store = new_store()
            store_list.append(store)
            sellable = Sellable(
                store=store,
                description=u'Test 1234',
                price=Decimal(2),
                )
            product = Product(
                store=store,
                sellable=sellable,
                )
            store.commit()
            self.assertTrue(p_data.was_created)
            self.assertFalse(p_data.was_edited)
            self.assertFalse(p_data.was_deleted)
            self.assertEqual(p_data.product, product)
            p_data.reset()

            # Test product being edited and emmiting the event just once
            store = new_store()
            store_list.append(store)
            sellable = store.fetch(sellable)
            product = store.fetch(product)
            sellable.notes = u'Notes'
            sellable.description = u'Test 666'
            product.weight = Decimal(10)
            store.commit()
            self.assertTrue(p_data.was_edited)
            self.assertFalse(p_data.was_created)
            self.assertFalse(p_data.was_deleted)
            self.assertEqual(p_data.product, product)
            self.assertEqual(p_data.emmit_count, 1)
            p_data.reset()

            # Test product being edited, editing Sellable
            store = new_store()
            store_list.append(store)
            sellable = store.fetch(sellable)
            product = store.fetch(product)
            sellable.notes = u'Notes for test'
            store.commit()
            self.assertTrue(p_data.was_edited)
            self.assertFalse(p_data.was_created)
            self.assertFalse(p_data.was_deleted)
            self.assertEqual(p_data.product, product)
            self.assertEqual(p_data.emmit_count, 1)
            p_data.reset()

            # Test product being edited, editing Product itself
            store = new_store()
            store_list.append(store)
            sellable = store.fetch(sellable)
            product = store.fetch(product)
            product.weight = Decimal(1)
            store.commit()
            self.assertTrue(p_data.was_edited)
            self.assertFalse(p_data.was_created)
            self.assertFalse(p_data.was_deleted)
            self.assertEqual(p_data.product, product)
            self.assertEqual(p_data.emmit_count, 1)
            p_data.reset()

            # Test product being edited, editing Product itself
            store = new_store()
            store_list.append(store)
            sellable = store.fetch(sellable)
            product = store.fetch(product)
            product.weight = Decimal(1)
            store.commit()
            #self.assertTrue(p_data.was_edited)
            self.assertFalse(p_data.was_created)
            self.assertFalse(p_data.was_deleted)
            #self.assertEqual(p_data.product, product)
            #self.assertEqual(p_data.emmit_count, 1)
            p_data.reset()

        finally:
            # Test product being removed
            store = new_store()
            store_list.append(store)
            sellable = store.fetch(sellable)
            product = store.fetch(product)
            sellable.remove()
            store.commit()
            self.assertTrue(p_data.was_deleted)
            self.assertFalse(p_data.was_created)
            self.assertFalse(p_data.was_edited)
            self.assertEqual(p_data.product, product)
            self.assertEqual(p_data.emmit_count, 1)
            p_data.reset()

            for store in store_list:
                store.close()


class TestStockTransactionHistory(DomainTest):
    def setUp(self):
        DomainTest.setUp(self)
        self.branch = get_current_branch(self.store)

    def _check_stock(self, product):
        storable = product.storable or self.create_storable(product)
        if not storable.get_stock_item(self.branch):
            storable.increase_stock(100, self.branch, 0, 0)

    def test_initial_stock(self):
        storable = self.create_storable()

        history_before = self.store.find(StockTransactionHistory).count()
        storable.register_initial_stock(10, self.branch)
        history_after = self.store.find(StockTransactionHistory).count()
        self.assertEquals(history_after, history_before + 1)

        history = self.store.find(StockTransactionHistory,
                                  type=StockTransactionHistory.TYPE_INITIAL).one()
        self.assertEquals(history.product_stock_item.storable, storable)
        self.assertEquals(history.get_description(), u'Registred initial stock')

    def test_imported(self):
        storable = self.create_storable()
        stock_item = self.create_product_stock_item(quantity=15,
                                                    storable=storable)

        # patch-04-09 creates this for us
        history = StockTransactionHistory(product_stock_item=stock_item,
                                        stock_cost=stock_item.stock_cost,
                                        quantity=stock_item.quantity,
                                        type=StockTransactionHistory.TYPE_IMPORTED,
                                        store=self.store)

        self.assertEquals(history.get_description(),
                          u'Imported from previous version')

    def _check_stock_history(self, product, quantity, item, parent, type):
        stock_item = product.storable.get_stock_item(self.branch)
        transaction = self.store.find(StockTransactionHistory,
                        product_stock_item=stock_item).order_by(
                            StockTransactionHistory.date).last()
        self.assertEquals(transaction.quantity, quantity)
        self.assertEquals(transaction.type, type)
        self.assertEquals(item, transaction.get_object())
        self.assertEquals(parent, transaction.get_object_parent())

    def test_stock_decrease(self):
        decrease_item = self.create_stock_decrease_item()
        product = decrease_item.sellable.product

        self._check_stock(product)
        decrease_item.decrease(self.branch)
        self._check_stock_history(product, -1, decrease_item,
                    decrease_item.stock_decrease,
                    StockTransactionHistory.TYPE_STOCK_DECREASE)

    def test_sale_cancel(self):
        sale_item = self.create_sale_item()
        # Mimic this sale_item like it was sold or else cancell
        # won't increase the stock bellow
        sale_item.quantity_decreased = sale_item.quantity
        product = sale_item.sellable.product

        self._check_stock(product)
        sale_item.cancel(self.branch)
        self._check_stock_history(product, 1, sale_item, sale_item.sale,
                    StockTransactionHistory.TYPE_CANCELED_SALE)

    def test_sell(self):
        sale_item = self.create_sale_item()
        product = sale_item.sellable.product
        sale_item.sellable.status = Sellable.STATUS_AVAILABLE

        self._check_stock(product)
        sale_item.sell(self.branch)
        self._check_stock_history(product, -1, sale_item, sale_item.sale,
                    StockTransactionHistory.TYPE_SELL)

    def test_retrun_sale(self):
        sale_item = self.create_sale_item()
        # Mimic this sale_item like it was sold or else we won't have
        # anything to return bellow
        sale_item.quantity_decreased = sale_item.quantity
        returned_sale = sale_item.sale.create_sale_return_adapter()
        returned_sale_item = returned_sale.get_items().any()
        product = returned_sale_item.sellable.product

        self._check_stock(product)
        returned_sale_item.return_(self.branch)
        self._check_stock_history(product, 1, returned_sale_item, returned_sale,
                    StockTransactionHistory.TYPE_RETURNED_SALE)

    def test_produce(self):
        material = self.create_production_material()
        production_item = material.order.get_items().any()
        product = production_item.product

        production_item.order.status = ProductionOrder.ORDER_PRODUCING
        material.allocated = 10
        material.consumed = 1

        self._check_stock(product)
        production_item.produce(1)
        self._check_stock_history(product, 1, production_item,
                    production_item.order,
                    StockTransactionHistory.TYPE_PRODUCTION_PRODUCED)

    def test_receiving_order(self):
        receiving_item = self.create_receiving_order_item()
        product = receiving_item.sellable.product

        receiving_item.quantity = 5

        self._check_stock(product)
        receiving_item.add_stock_items()
        self._check_stock_history(product, 5, receiving_item,
                    receiving_item.receiving_order,
                    StockTransactionHistory.TYPE_RECEIVED_PURCHASE)

    def test_loan_decrease(self):
        loan_item = self.create_loan_item()
        product = loan_item.sellable.product

        loan_item.quantity = 10
        loan_item.returned = 0
        loan_item.sold = 0

        self._check_stock(product)
        loan_item.sync_stock()
        self._check_stock_history(product, -10, loan_item, loan_item.loan,
                    StockTransactionHistory.TYPE_LOANED)

    def test_inventory_adjust(self):
        item = self.create_inventory_item()
        product = item.product

        item.inventory.branch = self.branch
        item.actual_quantity = 10
        item.recorded_quantity = 0
        increase_quantity = item.actual_quantity - item.recorded_quantity

        self._check_stock(product)
        item.adjust(123)
        self._check_stock_history(product, increase_quantity, item,
                    item.inventory,
                    StockTransactionHistory.TYPE_INVENTORY_ADJUST)

    def test_production_produced(self):
        production_item = self.create_production_item()
        production = production_item.order
        material = production.get_material_items().any()

        self._check_stock(production_item.product)
        self._check_stock(material.product)

        production.start_production()
        production_item.produce(1)
        self._check_stock_history(production_item.product, 1, production_item,
                    production,
                    StockTransactionHistory.TYPE_PRODUCTION_PRODUCED)

    def test_production_allocated(self):
        production_item = self.create_production_item()
        production = production_item.order
        material = production.get_material_items().any()
        production.branch = self.branch

        self._check_stock(production_item.product)
        self._check_stock(material.product)

        material.allocate(5)
        self._check_stock_history(material.product, -5, material, production,
                    StockTransactionHistory.TYPE_PRODUCTION_ALLOCATED)

    def test_production_returned(self):
        production_item = self.create_production_item()
        production = production_item.order
        material = production.get_material_items().any()
        production.branch = self.branch

        production.status = ProductionOrder.ORDER_CLOSED

        self._check_stock(production_item.product)
        self._check_stock(material.product)

        material.allocated = 10
        material.lost = 0
        material.consumed = 5

        material.return_remaining()
        self._check_stock_history(material.product, 5, material, production,
                    StockTransactionHistory.TYPE_PRODUCTION_RETURNED)

    def test_transfer_to(self):
        transfer_item = self.create_transfer_order_item()
        transfer = transfer_item.transfer_order
        product = transfer_item.sellable.product

        self._check_stock(product)

        transfer.source_branch = self.branch
        transfer.send_item(transfer_item)

        self._check_stock_history(product, -5, transfer_item, transfer,
                    StockTransactionHistory.TYPE_TRANSFER_TO)

    def test_transfer_from(self):
        transfer_item = self.create_transfer_order_item()
        transfer = transfer_item.transfer_order
        product = transfer_item.sellable.product

        self._check_stock(product)

        transfer_item.quantity = 2
        transfer.destination_branch = self.branch
        transfer.receive(datetime.date.today())

        self._check_stock_history(product, 2, transfer_item, transfer,
                    StockTransactionHistory.TYPE_TRANSFER_FROM)

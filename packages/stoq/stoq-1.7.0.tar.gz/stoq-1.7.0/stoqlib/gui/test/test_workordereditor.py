# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2013 Async Open Source <http://www.async.com.br>
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

from stoqlib.domain.workorder import WorkOrder, WorkOrderCategory
from stoqlib.gui.uitestutils import GUITest
from stoqlib.gui.editors.workordereditor import WorkOrderEditor
from stoqlib.lib.parameters import sysparam


class TestWorkOrderEditor(GUITest):
    def testCreate(self):
        # Create those before initializating the editor so they get prefilled
        category = WorkOrderCategory(store=self.store,
                                     name=u'Categoty XXX')
        client = self.create_client()

        editor = WorkOrderEditor(self.store)
        editor.model.identifier = 654
        editor.proxy.update('order_number_str')
        opening_slave = editor.opening_slave
        execution_slave = editor.execution_slave
        item_slave = execution_slave.sellable_item_slave
        quote_slave = editor.quote_slave
        # Check creation state
        self.assertEqual(editor.model.status, WorkOrder.STATUS_OPENED)
        self.check_editor(editor, 'editor-workorder-create')

        editor.equipment.update(u"Test equipment")
        editor.category.update(category)
        editor.client.update(client)
        opening_slave.defect_reported.update(u"Defect reported")
        # Check initial state
        self.assertEqual(editor.model.status, WorkOrder.STATUS_OPENED)
        self.check_editor(editor, 'editor-workorder-create-initial')

        quote_slave.defect_detected.update(u"Defect detected")
        quote_slave.estimated_hours.update(10)
        quote_slave.estimated_hours.update(100)
        quote_slave.estimated_start.update(datetime.datetime(2013, 1, 1))
        quote_slave.estimated_finish.update(datetime.datetime(2013, 1, 2))
        self.assertInvalid(quote_slave, ['estimated_start'])
        sysparam(self.store).update_parameter(u"ALLOW_OUTDATED_OPERATIONS", u"1")
        quote_slave.estimated_start.validate(force=True)
        self.assertValid(quote_slave, ['estimated_start'])
        editor.has_client_approval.set_active(True)
        # Check approved state
        self.assertEqual(editor.model.status, WorkOrder.STATUS_APPROVED)
        self.check_editor(editor, 'editor-workorder-create-approved')

        product_sellable = self.create_product(stock=100).sellable
        product_sellable.barcode = u'9988776655'
        service_sellable = self.create_service().sellable
        service_sellable.barcode = u'5566778899'
        service_sellable.can_sell()
        item_slave.barcode.set_text(product_sellable.barcode)
        item_slave.barcode.activate()
        item_slave.cost.update(50)
        item_slave.quantity.update(101)
        self.assertNotSensitive(item_slave, ['add_sellable_button'])
        item_slave.quantity.update(99)
        self.assertSensitive(item_slave, ['add_sellable_button'])
        self.click(item_slave.add_sellable_button)
        item_slave.barcode.set_text(service_sellable.barcode)
        item_slave.barcode.activate()
        item_slave.cost.update(100)
        item_slave.quantity.update(2)
        self.click(item_slave.add_sellable_button)
        # Check work in progress state
        self.assertEqual(editor.model.status, WorkOrder.STATUS_WORK_IN_PROGRESS)
        self.check_editor(editor, 'editor-workorder-create-in-progress')

        self.click(editor.main_dialog.ok_button)
        storable = product_sellable.product_storable
        # This should be 1 since we created it with 100 and used 99 in the order
        self.assertEqual(
            storable.get_balance_for_branch(editor.model.branch), 1)

    def testShow(self):
        workorder = self.create_workorder(equipment=u'Test equipment')
        workorder.identifier = 666
        workorder.client = self.create_client()
        workorder.category = WorkOrderCategory(store=self.store,
                                               name=u'Categoty XXX')
        workorder.defect_reported = u"Defect reported"
        # Create the editor and check initial state
        editor = WorkOrderEditor(self.store, model=workorder)
        self.check_editor(editor, 'editor-workorder-show-initial')

        workorder.defect_detected = u"Defect detected"
        workorder.estimated_hours = 10
        workorder.estimated_hours = 100
        workorder.estimated_start = datetime.datetime(2013, 1, 1)
        workorder.estimated_finish = datetime.datetime(2013, 1, 2)
        workorder.approve()
        # Create another editor to check approved state
        editor = WorkOrderEditor(self.store, model=workorder)
        self.check_editor(editor, 'editor-workorder-show-approved')

        workorder.add_sellable(self.create_sellable(description=u"Product A"),
                               price=99, quantity=2)
        workorder.add_sellable(self.create_sellable(description=u"Product B"),
                               price=5, quantity=100)
        workorder.start()
        # Create another editor to check work in progress state
        editor = WorkOrderEditor(self.store, model=workorder)
        self.check_editor(editor, 'editor-workorder-show-in-progress')

        workorder.finish()
        # Create another editor to check finished state
        editor = WorkOrderEditor(self.store, model=workorder)
        self.check_editor(editor, 'editor-workorder-show-finished')

        workorder.close()
        # Create another editor to check closed state
        editor = WorkOrderEditor(self.store, model=workorder)
        self.check_editor(editor, 'editor-workorder-show-closed')

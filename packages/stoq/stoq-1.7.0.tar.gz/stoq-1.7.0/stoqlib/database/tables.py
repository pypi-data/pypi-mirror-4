# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005-2013 Async Open Source <http://www.async.com.br>
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
"""A list of all tables in database and a way to get them.

 Add new tables here:
 ('domain.modulo') : ['classA', 'classB', ...],

 module is the domain module which lives the classes in the list
 (classA, classB, ...).
"""


from kiwi.log import Logger
from kiwi.python import namedAny

from stoqlib.lib.translation import stoqlib_gettext

_ = stoqlib_gettext

log = Logger(__name__)


_tables = [
     ('system', ["SystemTable", "TransactionEntry"]),
     ('parameter', ["ParameterData"]),
     ('account', ['Account',
                  'AccountTransaction',
                  'BankAccount',
                  'BillOption']),
     ('profile', ["UserProfile", "ProfileSettings"]),
     ('person', ["Person"]),
     ('address', ["CityLocation", "Address"]),
     ('person', ["EmployeeRole",
                 "WorkPermitData",
                 "MilitaryData",
                 "VoterData",
                 "ContactInfo",
                 "LoginUser",
                 "Calls",
                 "Individual",
                 "Company",
                 "Client",
                 "Supplier",
                 "Employee",
                 "Branch",
                 "SalesPerson",
                 "Transporter",
                 "EmployeeRoleHistory",
                 "ClientCategory",
                 "ClientSalaryHistory",
                 "CreditCheckHistory",
                 "UserBranchAccess"]),
     ('synchronization', ["BranchSynchronization"]),
     ('station', ["BranchStation"]),
     ('till', ["Till", "TillEntry"]),
     ('payment.card', ["CreditProvider", "CreditCardData", 'CardPaymentDevice',
                       'CardOperationCost']),
     ('payment.category', ["PaymentCategory"]),
     ('payment.comment', ["PaymentComment"]),
     ('payment.group', ["PaymentGroup"]),
     ('payment.method', ["PaymentMethod", "CheckData"]),
     ('payment.payment', ["Payment", "PaymentChangeHistory"]),
     ('payment.renegotiation', ["PaymentRenegotiation"]),
     ('fiscal', ["CfopData", "FiscalBookEntry"]),
     ('sale', ["SaleItem",
               "Delivery",
               "Sale"]),
     ('returnedsale', ["ReturnedSale",
                       "ReturnedSaleItem"]),
     ('sellable', ["SellableUnit",
                   "SellableTaxConstant",
                   "SellableCategory",
                   'ClientCategoryPrice',
                   "Sellable"]),
     ('service', ["Service"]),
     ('product', ["Product",
                  "ProductComponent",
                  "ProductHistory",
                  'ProductManufacturer',
                  'ProductQualityTest',
                  "ProductSupplierInfo",
                  'StockTransactionHistory',
                  "ProductStockItem",
                  "Storable"]),
     ('purchase', ["PurchaseOrder",
                   "Quotation",
                   "PurchaseItem",
                   "QuoteGroup"]),
     ('receiving', ["ReceivingOrder", "ReceivingOrderItem"]),
     ('devices', ["DeviceSettings",
                  "FiscalDayHistory",
                  "FiscalDayTax"]),
     ('commission', ["CommissionSource", "Commission"]),
     ('transfer', ["TransferOrder", "TransferOrderItem"]),
     ('inventory', ["Inventory", "InventoryItem"]),
     ('image', ["Image"]),
     ('attachment', ["Attachment"]),
     ('stockdecrease', ["StockDecrease", "StockDecreaseItem"]),
     ('production', ["ProductionOrder",
                     "ProductionItem",
                     "ProductionItemQualityResult",
                     "ProductionMaterial",
                     "ProductionService",
                     "ProductionProducedItem"]),
     ('loan', ['Loan', 'LoanItem']),
     ('invoice', ['InvoiceField', 'InvoiceLayout',
                  'InvoicePrinter']),
     ('taxes', ['ProductIcmsTemplate',
                'ProductIpiTemplate',
                'ProductTaxTemplate',
                'SaleItemIcms',
                'SaleItemIpi']),
     ('uiform', ['UIForm', 'UIField']),
     ('plugin', ['InstalledPlugin']),
     ('costcenter', ['CostCenter', 'CostCenterEntry']),
     ('stockdecrease', ['StockDecrease',
                        'StockDecreaseItem']),
     ('workorder', ['WorkOrder',
                    'WorkOrderItem',
                    'WorkOrderCategory']),
     ('event', ['Event']),
]

# fullname (eg "stoqlib.domain.person.Person") -> class
_table_cache = {}
# list of classes, used by get_table_types where order is important
_table_list = []


def _import():
    for path, table_names in _tables:
        for table_name in table_names:
            klass = namedAny('stoqlib.domain.%s.%s' % (path, table_name))
            _table_cache[table_name] = klass
            _table_list.append(klass)


def get_table_type_by_name(table_name):
    """Gets a table by name.

    :param table_name: name of the table
    """

    if not _table_cache:
        _import()

    return _table_cache[table_name]


def get_table_types():
    if not _table_list:
        _import()

    return _table_list

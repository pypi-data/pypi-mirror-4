# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2006 Async Open Source <http://www.async.com.br>
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
""" Test case for stoq/domain/person.py module.  """

import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from storm.exceptions import NotOneError
from storm.expr import And
from storm.store import AutoReload

from kiwi.currency import currency

from stoqlib.database.expr import Age, Case, Date, DateTrunc, Interval
from stoqlib.domain.person import Calls, ContactInfo
from stoqlib.domain.address import Address, CityLocation
from stoqlib.domain.exampledata import ExampleCreator
from stoqlib.domain.fiscal import CfopData
from stoqlib.domain.payment.method import PaymentMethod
from stoqlib.domain.payment.payment import Payment
from stoqlib.domain.person import (Branch, Client, ClientCategory,
                                   ClientSalaryHistory, Company,
                                   Employee, EmployeeRole,
                                   EmployeeRoleHistory, Individual,
                                   LoginUser, Person, SalesPerson, Supplier,
                                   Transporter)
from stoqlib.domain.product import Product
from stoqlib.domain.purchase import PurchaseOrder
from stoqlib.domain.sellable import ClientCategoryPrice
from stoqlib.domain.test.domaintest import DomainTest
from stoqlib.enums import LatePaymentPolicy
from stoqlib.exceptions import SellError
from stoqlib.lib.parameters import sysparam
from stoqlib.lib.translation import stoqlib_gettext


_ = stoqlib_gettext


class TestEmployeeRoleHistory(DomainTest):
    def testCreate(self):
        EmployeeRole(store=self.store, name=u'ajudante')

    def testHasRole(self):
        role = EmployeeRole(store=self.store, name=u'role')
        self.failIf(role.has_other_role(u'Role'))
        role = EmployeeRole(store=self.store, name=u'Role')
        self.failUnless(role.has_other_role(u'role'))


class TestEmployeeRole(DomainTest):
    def testGetdescription(self):
        role = self.create_employee_role()
        role.name = u'manager'
        self.assertEquals(role.name, role.get_description())


class TestPerson(DomainTest):

    def testAddresses(self):
        person = self.create_person()
        assert not person.get_main_address()
        ctlocs = self.store.find(CityLocation)
        assert not ctlocs.is_empty()
        ctloc = ctlocs[0]
        address = Address(store=self.store, person=person,
                          city_location=ctloc, is_main_address=True)
        self.assertEquals(person.get_main_address(), address)

        self.assertEquals(len(list(person.addresses)), 1)
        self.assertEquals(list(person.addresses)[0], address)

    def testCalls(self):
        person = self.create_person()
        user = self.create_user()
        self.assertEquals(len(list(person.calls)), 0)

        call = Calls(store=self.store, date=datetime.datetime.today(),
                     description=u'', message=u'', person=person, attendant=user)
        self.assertEquals(len(list(person.calls)), 1)
        self.assertEquals(list(person.calls)[0], call)

    def testContactInfo(self):
        person = self.create_person()
        self.assertEquals(len(list(person.contact_infos)), 0)

        contact_info = ContactInfo(store=self.store, person=person)
        self.assertEquals(len(list(person.contact_infos)), 1)
        self.assertEquals(list(person.contact_infos)[0], contact_info)

    def testGetaddressString(self):
        person = self.create_person()
        ctloc = CityLocation(store=self.store)
        address = Address(store=self.store, person=person,
                          city_location=ctloc, street=u'bla', streetnumber=2,
                          district=u'fed', is_main_address=True)
        self.assertEquals(person.get_address_string(), _(u'%s %s, %s') % (
            address.street, address.streetnumber, address.district))

    def testGetMobileNumberNumber(self):
        person = self.create_person()
        person.mobile_number = u'0321-12345'
        self.assertEquals(person.mobile_number, u'032112345')

    def testGetPhoneNumberNumber(self):
        person = self.create_person()
        person.phone_number = u'0321-12345'
        self.assertEquals(person.get_phone_number_number(), 32112345)
        self.assertEquals(person.phone_number, u'032112345')

        person.phone_number = None
        self.assertEquals(person.get_phone_number_number(), 0)

    def testGetFaxNumberNumber(self):
        person = self.create_person()
        person.fax_number = u'0321-12345'
        self.assertEquals(person.fax_number, u'032112345')
        self.assertEquals(person.get_fax_number_number(), 32112345)

        person.fax_number = None
        self.assertEquals(person.get_fax_number_number(), 0)

    def testGetFormattedPhoneNumber(self):
        person = self.create_person()
        self.assertEquals(person.get_formatted_phone_number(), u"")
        phone = u'0321-1234'
        person.phone_number = phone
        self.assertEquals(person.get_formatted_phone_number(),
                          phone)

    def testGetFormattedFaxNumber(self):
        person = self.create_person()
        self.assertEquals(person.get_formatted_fax_number(), u"")
        fax = u'0321-1234'
        person.fax_number = fax
        self.assertEquals(person.get_formatted_fax_number(),
                          fax)

    def testGetByPhoneNumber(self):
        person = self.create_person()

        self.assertTrue(Person.get_by_phone_number(
            self.store, u'1138').is_empty())
        person.phone_number = u'1138'
        self.assertFalse(Person.get_by_phone_number(
            self.store, u'1138').is_empty())
        person.phone_number = u'0'
        self.assertTrue(Person.get_by_phone_number(
            self.store, u'1138').is_empty())
        person.mobile_number = u'1138'
        self.assertFalse(Person.get_by_phone_number(
            self.store, u'1138').is_empty())


class _PersonFacetTest(object):
    facet = None

    def _create_person_facet(self):
        return ExampleCreator.create(self.store, self.facet.__name__)

    def testInactivate(self):
        facet = self._create_person_facet()
        if not facet.is_active:
            facet.is_active = True
        facet.inactivate()
        self.failIf(facet.is_active)
        self.assertRaises(AssertionError, facet.inactivate)

    def testActivate(self):
        facet = self._create_person_facet()
        facet.is_active = False
        facet.activate()
        self.failUnless(facet.is_active)
        self.assertRaises(AssertionError, facet.activate)

    def testGetDescription(self):
        facet = self._create_person_facet()
        self.failUnless(facet.get_description(), facet.person.name)


class TestIndividual(_PersonFacetTest, DomainTest):
    facet = Individual

    def testIndividual(self):
        person = self.create_person()
        individual = Individual(person=person, store=self.store)

        statuses = individual.get_marital_statuses()
        self.assertEqual(type(statuses), list)
        self.failUnless(len(statuses) > 0)
        self.assertEqual(type(statuses[0]), tuple)
        self.assertEqual(type(statuses[0][0]), unicode)
        self.assertEqual(type(statuses[0][1]), int)

    def testGetCPFNumber(self):
        individual = self.create_individual()
        individual.cpf = u''
        self.assertEquals(individual.get_cpf_number(), 0)
        individual.cpf = u'123.456.789-203'
        self.assertEquals(individual.get_cpf_number(), 123456789203)

    def testGetBirthdayDateQuery(self):
        start = datetime.datetime(2000, 3, 4)

        query = Individual.get_birthday_query(start)

        start_year = DateTrunc(u'year', Date(start))
        age_in_year = Age(Individual.birth_date,
                          DateTrunc(u'year', Individual.birth_date))
        test_query = (
            start_year + age_in_year +
            Case(condition=age_in_year < Age(Date(start), start_year),
                 result=Interval(u'1 year'),
                 else_=Interval(u'0 year'))
        )
        test_query = (test_query == Date(start))

        self.assertEquals(query, test_query)

        individuals = list(self.store.find(Individual, test_query))
        self.assertEquals(len(individuals), 0)

        client1 = self.create_client(u'Junio C. Hamano')
        client1.person.individual.birth_date = datetime.date(1972, 10, 15)
        client2 = self.create_client(u'Richard Stallman')
        client2.person.individual.birth_date = datetime.date(1989, 3, 4)
        client3 = self.create_client(u'Linus Torvalds')
        client3.person.individual.birth_date = datetime.date(2000, 3, 4)
        client4 = self.create_client(u'Guido van Rossum')
        client4.person.individual.birth_date = datetime.date(2005, 3, 4)

        individuals = list(self.store.find(Individual, test_query))
        self.assertEquals(len(individuals), 3)
        self.assertTrue(client2.person.individual in individuals)
        self.assertTrue(client3.person.individual in individuals)
        self.assertTrue(client4.person.individual in individuals)

    def testGetBirthdayIntervalQuery(self):
        start = datetime.datetime(2000, 3, 1)
        end = datetime.datetime(2000, 3, 25)

        query = Individual.get_birthday_query(start, end)

        start_year = DateTrunc(u'year', Date(start))
        age_in_year = Age(Individual.birth_date,
                          DateTrunc(u'year', Individual.birth_date))
        test_query = (
            start_year + age_in_year +
            Case(condition=age_in_year < Age(Date(start), start_year),
                 result=Interval(u'1 year'),
                 else_=Interval(u'0 year'))
        )
        test_query = And(test_query >= Date(start),
                         test_query <= Date(end))

        self.assertEquals(query, test_query)

        individuals = list(self.store.find(Individual, test_query))
        self.assertEquals(len(individuals), 0)

        client1 = self.create_client(u'Junio C. Hamano')
        client1.person.individual.birth_date = datetime.date(1972, 10, 15)
        client2 = self.create_client(u'Richard Stallman')
        client2.person.individual.birth_date = datetime.date(1989, 3, 7)
        client3 = self.create_client(u'Linus Torvalds')
        client3.person.individual.birth_date = datetime.date(2000, 3, 4)
        client4 = self.create_client(u'Guido van Rossum')
        client4.person.individual.birth_date = datetime.date(2005, 3, 20)

        individuals = list(self.store.find(Individual, test_query))
        self.assertEquals(len(individuals), 3)
        self.assertTrue(client2.person.individual in individuals)
        self.assertTrue(client3.person.individual in individuals)
        self.assertTrue(client4.person.individual in individuals)


class TestCompany(_PersonFacetTest, DomainTest):
    facet = Company

    def testGetCnpjNumberNumber(self):
        company = self.create_company()
        company.cnpj = u'111.222.333.444'
        self.assertEquals(company.get_cnpj_number(), 111222333444)


class TestClient(_PersonFacetTest, DomainTest):
    facet = Client

    def testGetname(self):
        client = self.create_client()
        client.person.name = u'Laun'
        self.assertEquals(client.get_name(), u'Laun')

    def testGetStatusString(self):
        client = self.create_client()
        status = client.status
        status = client.statuses[status]
        self.assertEquals(client.get_status_string(), status)

    def testGetactiveClients(self):
        table = Client
        active_clients = table.get_active_clients(self.store).count()
        client = self.create_client()
        client.status = table.STATUS_SOLVENT
        one_more_active_client = table.get_active_clients(self.store).count()
        self.assertEquals(active_clients + 1, one_more_active_client)

    def testGetclient_sales(self):
        client = self.store.find(Client)
        assert not client.is_empty()
        client = client[0]
        CfopData(code=u'123', description=u'bla', store=self.store)
        branches = self.store.find(Branch)
        assert not branches.is_empty()
        people = self.store.find(SalesPerson)
        assert not people.is_empty()
        count_sales = client.get_client_sales().count()
        sale = self.create_sale()
        sale.client = client
        products = self.store.find(Product)
        assert not products.is_empty()
        product = products[0]
        sale.add_sellable(product.sellable)
        one_more_sale = client.get_client_sales().count()
        self.assertEquals(count_sales + 1, one_more_sale)

    def testClientCategory(self):
        categories = self.store.find(ClientCategory, name=u'Category')
        self.assertEquals(categories.count(), 0)

        category = self.create_client_category(u'Category')
        categories = self.store.find(ClientCategory, name=u'Category')
        self.assertEquals(categories.count(), 1)

        self.assertTrue(category.can_remove())
        category.remove()
        categories = self.store.find(ClientCategory, name=u'Category')
        self.assertEquals(categories.count(), 0)

        sellable = self.create_sellable(price=50)
        category = self.create_client_category(u'Category')
        ClientCategoryPrice(sellable=sellable,
                            category=category,
                            price=75,
                            store=self.store)
        self.assertFalse(category.can_remove())

    def test_can_purchase_allow_all(self):
        #: This parameter always allows the client to purchase, no matter if he
        #: has late payments
        sysparam(self.store).update_parameter(u'LATE_PAYMENTS_POLICY',
                                unicode(int(LatePaymentPolicy.ALLOW_SALES)))

        client = self.create_client()
        bill_method = PaymentMethod.get_by_name(self.store, u'bill')
        check_method = PaymentMethod.get_by_name(self.store, u'check')
        money_method = PaymentMethod.get_by_name(self.store, u'money')
        store_credit_method = PaymentMethod.get_by_name(self.store,
                                                        u'store_credit')
        today = datetime.date.today()

        # client can pay if he doesn't have any payments
        client.credit_limit = Decimal("1000")
        self.assertTrue(client.can_purchase(money_method, currency("200")))

        # client can pay if he has payments that are not overdue
        payment = self.create_payment(Payment.TYPE_IN, today, method=bill_method)
        payment.group = self.create_payment_group()
        payment.group.payer = client.person
        self.assertTrue(client.can_purchase(check_method, currency("200")))

        # client can pay even if he does have overdue payments
        payment = self.create_payment(Payment.TYPE_IN,
                            today - relativedelta(days=1), method=check_method)
        payment.group = self.create_payment_group()
        payment.group.payer = client.person
        self.assertTrue(client.can_purchase(store_credit_method, currency("200")))

        # But he cannot pay if its above the credit limit
        self.assertRaises(SellError, client.can_purchase, store_credit_method, currency("1001"))

    def test_can_purchase_disallow_store_credit(self):
        #: This parameter disallows the client to purchase with store credit
        #: when he has late payments
        sysparam(self.store).update_parameter(u'LATE_PAYMENTS_POLICY',
                                unicode(int(LatePaymentPolicy.DISALLOW_STORE_CREDIT)))

        client = self.create_client()
        bill_method = PaymentMethod.get_by_name(self.store, u'bill')
        check_method = PaymentMethod.get_by_name(self.store, u'check')
        money_method = PaymentMethod.get_by_name(self.store, u'money')
        store_credit_method = PaymentMethod.get_by_name(self.store,
                                                        u'store_credit')
        today = datetime.date.today()

        # client can pay if he doesn't have any payments
        self.assertTrue(client.can_purchase(money_method, currency("0")))

        # client can pay if he has payments that are not overdue
        payment = self.create_payment(Payment.TYPE_IN, today, method=bill_method)
        payment.group = self.create_payment_group()
        payment.group.payer = client.person
        self.assertTrue(client.can_purchase(money_method, currency("0")))

        # for a client with overdue payments
        payment = self.create_payment(Payment.TYPE_IN,
                                      today - relativedelta(days=1),
                                      method=money_method)
        payment.status = Payment.STATUS_PENDING
        payment.group = self.create_payment_group()
        payment.group.payer = client.person
        # client can pay if payment method is not store credit
        self.assertTrue(client.can_purchase(check_method, currency("0")))
        self.assertTrue(client.can_purchase(money_method, currency("0")))
        # client can not pay if payment method is store credit
        self.assertRaises(SellError, client.can_purchase, store_credit_method, currency("0"))

    def test_can_purchase_disallow_all(self):
        #: This parameter disallows the client to purchase with store credit
        #: when he has late payments
        sysparam(self.store).update_parameter(u'LATE_PAYMENTS_POLICY',
                                unicode(int(LatePaymentPolicy.DISALLOW_SALES)))

        client = self.create_client()
        bill_method = PaymentMethod.get_by_name(self.store, u'bill')
        check_method = PaymentMethod.get_by_name(self.store, u'check')
        money_method = PaymentMethod.get_by_name(self.store, u'money')
        store_credit_method = PaymentMethod.get_by_name(self.store,
                                                        u'store_credit')
        today = datetime.date.today()

        # client can pay if he doesn't have any payments
        self.assertTrue(client.can_purchase(money_method, currency("0")))

        # client can pay if he has overdue payments
        payment = self.create_payment(Payment.TYPE_IN, today, method=bill_method)
        payment.group = self.create_payment_group()
        payment.group.payer = client.person
        self.assertTrue(client.can_purchase(check_method, currency("0")))

        # client can not pay if he has overdue payments
        payment = self.create_payment(Payment.TYPE_IN,
                                      today - relativedelta(days=1),
                                      method=bill_method)
        payment.group = self.create_payment_group()
        payment.group.payer = client.person
        payment.status = Payment.STATUS_PENDING
        self.assertRaises(SellError, client.can_purchase, store_credit_method,
                                     currency("0"))
        self.assertRaises(SellError, client.can_purchase, check_method,
                                     currency("0"))
        self.assertRaises(SellError, client.can_purchase, money_method,
                                     currency("0"))

    def test_can_purchase_total_amount(self):
        method = PaymentMethod.get_by_name(self.store, u'store_credit')

        # client can not buy if he does not have enough store credit
        client = self.create_client()
        client.credit_limit = currency('0')
        self.assertRaises(SellError, client.can_purchase, method, currency('1'))

        # client can buy if he has enough store credit
        client.credit_limit = currency('1000')
        self.assertTrue(client.can_purchase(method, currency('200')))
        self.assertRaises(SellError, client.can_purchase, method, currency('1001'))

    def test_update_credit_limit(self):
        client = self.create_client()
        client.salary = 100

        # just setting paramater to a value that won't interfere in
        # the tests
        sysparam(self.store).update_parameter(
            u"CREDIT_LIMIT_SALARY_PERCENT",
            u"5")

        # testing if updates
        Client.update_credit_limit(10, self.store)
        client.credit_limit = AutoReload
        self.assertEquals(client.credit_limit, 10)

        # testing if it does not update
        client.credit_limit = 200
        Client.update_credit_limit(0, self.store)
        self.assertEquals(client.credit_limit, 200)

    def test_set_salary(self):
        sysparam(self.store).update_parameter(
            u"CREDIT_LIMIT_SALARY_PERCENT",
            u"10")

        client = self.create_client()

        self.assertEquals(client.salary, 0)
        self.assertEquals(client.credit_limit, 0)

        client.salary = 100

        self.assertEquals(client.salary, 100)
        self.assertEquals(client.credit_limit, 10)

        sysparam(self.store).update_parameter(
            u"CREDIT_LIMIT_SALARY_PERCENT",
            u"0")
        client.credit_limit = 100
        client.salary = 200

        self.assertEquals(client.salary, 200)
        self.assertEquals(client.credit_limit, 100)


class TestSupplier(_PersonFacetTest, DomainTest):
    facet = Supplier

    def testGetActiveSuppliers(self):
        for supplier in Supplier.get_active_suppliers(self.store):
            self.assertEquals(supplier.status,
                              Supplier.STATUS_ACTIVE)

    def testGetAllSuppliers(self):
        query = And(Person.name == u"test",
                    Supplier.person_id == Person.id)

        suppliers = self.store.find(Person, query)
        self.assertEqual(suppliers.count(), 0)

        supplier = self.create_supplier()
        supplier.person.name = u"test"

        suppliers = self.store.find(Person, query)
        self.assertEqual(suppliers.count(), 1)

    def testGetSupplierPurchase(self):
        supplier = self.create_supplier()

        self.failIf(supplier.get_supplier_purchases().count())

        order = self.create_receiving_order()
        order.purchase.supplier = supplier
        self.create_receiving_order_item(order)
        order.purchase.status = PurchaseOrder.ORDER_PENDING
        order.purchase.confirm()
        order.confirm()

        self.failUnless(supplier.get_supplier_purchases().count())

        last_date = supplier.get_last_purchase_date()
        self.assertEquals(last_date, order.purchase.open_date.date())


class TestEmployee(_PersonFacetTest, DomainTest):
    facet = Employee

    def testRoleHistory(self):
        #this test depends bug 2457
        employee = self.create_employee()
        EmployeeRoleHistory(role=employee.role,
                            employee=employee,
                            store=self.store,
                            salary=currency(500),
                            is_active=False)
        old_count = employee.get_role_history().count()
        EmployeeRoleHistory(role=employee.role,
                            employee=employee,
                            store=self.store,
                            salary=currency(900))
        new_count = employee.get_role_history().count()
        self.assertEquals(old_count + 1, new_count)

    def testGetActiveRoleHistory(self):
        employee = self.create_employee()

        #creating 2 active role history, asserting it fails
        EmployeeRoleHistory(role=employee.role,
                            employee=employee,
                            store=self.store,
                            salary=currency(230))
        EmployeeRoleHistory(role=employee.role,
                            employee=employee,
                            store=self.store,
                            salary=currency(320))
        self.assertRaises(NotOneError, employee.get_active_role_history)

        #now with one employeerolehistory
        #FIXME: this breaks in buildbot, figure out why.
        #history2.is_active = False
        #assert employee.get_role_history()


class TestUser(_PersonFacetTest, DomainTest):
    facet = LoginUser

    def testGetstatusStr(self):
        users = self.store.find(LoginUser)
        assert not users.is_empty()
        user = users[0]
        user.is_active = False
        string = user.get_status_string()
        self.assertEquals(string, _(u'Inactive'))

    def testGetActiveUsers(self):
        active_users_count = LoginUser.get_active_users(self.store).count()

        user = self.create_user()
        active_users = LoginUser.get_active_users(self.store)
        self.assertTrue(user in active_users)
        self.assertEqual(active_users.count(), active_users_count + 1)

        user.inactivate()
        active_users = LoginUser.get_active_users(self.store)
        self.assertFalse(user in active_users)
        self.assertEqual(active_users.count(), active_users_count)


class TestBranch(_PersonFacetTest, DomainTest):
    facet = Branch

    def testGetstatusStr(self):
        branches = self.store.find(Branch)
        assert not branches.is_empty()
        branch = branches[0]
        branch.is_active = False
        string = branch.get_status_string()
        self.assertEquals(string, _(u'Inactive'))

    def testGetactiveBranches(self):
        person = self.create_person()
        Company(person=person, store=self.store)
        count = Branch.get_active_branches(self.store).count()
        manager = self.create_employee()
        branch = Branch(person=person, store=self.store,
                        manager=manager, is_active=True)
        assert branch.get_active_branches(self.store).count() == count + 1

    def test_is_from_same_company(self):
        branch1 = self.create_branch()
        branch1.person.company.cnpj = u'111.222.333/0001-11'

        branch2 = self.create_branch()
        branch2.person.company.cnpj = u'555.666.777/0001-11'
        self.assertFalse(branch1.is_from_same_company(branch2))

        branch2.person.company.cnpj = u'111.222.333/0002-22'
        self.assertTrue(branch1.is_from_same_company(branch2))


class SalesPersonTest(_PersonFacetTest, DomainTest):

    facet = SalesPerson

    def testGetactiveSalespersons(self):
        count = SalesPerson.get_active_salespersons(self.store).count()
        salesperson = self.create_sales_person()
        one_more = salesperson.get_active_salespersons(self.store).count()
        assert count + 1 == one_more

    def testGetStatusString(self):
        salesperson = self.create_sales_person()
        string = salesperson.get_status_string()
        self.assertEquals(string, _(u'Active'))


class TransporterTest(_PersonFacetTest, DomainTest):

    facet = Transporter

    def testGetStatusString(self):
        transporter = self.create_transporter()
        string = transporter.get_status_string()
        self.assertEquals(string, _(u'Active'))

    def testGetActiveTransporters(self):
        count = Transporter.get_active_transporters(self.store).count()
        transporter = self.create_transporter()
        one_more = transporter.get_active_transporters(self.store).count()
        self.assertEqual(count + 1, one_more)


class TestClientSalaryHistory(DomainTest):
    def testAdd(self):
        client = self.create_client()
        user = self.create_user()

        client.salary = 20
        ClientSalaryHistory.add(self.store, 10, client, user)
        salary_histories = self.store.find(ClientSalaryHistory)
        last_salary_history = salary_histories.order_by(ClientSalaryHistory.id).last()

        self.assertEquals(last_salary_history.client, client)
        self.assertEquals(last_salary_history.new_salary, 20)

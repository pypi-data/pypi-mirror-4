# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005-2012 Async Open Source <http://www.async.com.br>
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
""" Person editors definition """

import datetime

from kiwi.datatypes import ValidationError
from kiwi.ui.forms import TextField

from stoqlib.api import api
from stoqlib.domain.person import (Client, Branch, Employee, EmployeeRole,
                                   CreditProvider, Individual, LoginUser,
                                   Supplier, Transporter)
from stoqlib.lib.translation import stoqlib_gettext
from stoqlib.gui.base.dialogs import run_dialog
from stoqlib.gui.editors.baseeditor import BaseEditor
from stoqlib.gui.slaves.clientslave import ClientStatusSlave
from stoqlib.gui.slaves.credproviderslave import CreditProviderDetailsSlave
from stoqlib.gui.slaves.employeeslave import (EmployeeDetailsSlave,
                                      EmployeeStatusSlave,
                                      EmployeeRoleSlave,
                                      EmployeeRoleHistorySlave)
from stoqlib.gui.slaves.userslave import UserDetailsSlave, UserStatusSlave
from stoqlib.gui.slaves.userbranchaccessslave import UserBranchAccessSlave
from stoqlib.gui.slaves.supplierslave import SupplierDetailsSlave
from stoqlib.gui.slaves.transporterslave import TransporterDataSlave
from stoqlib.gui.slaves.branchslave import BranchDetailsSlave
from stoqlib.gui.templates.persontemplate import BasePersonRoleEditor

_ = stoqlib_gettext


class ClientEditor(BasePersonRoleEditor):
    model_name = _('Client')
    title = _('New Client')
    model_type = Client
    gladefile = 'BaseTemplate'

    help_section = 'client'
    ui_form_name = 'client'

    #
    # BaseEditor hooks
    #

    def create_model(self, conn):
        person = BasePersonRoleEditor.create_model(self, conn)
        client = person.client
        if client is None:
            client = Client(person=person, connection=conn)
        return client

    def setup_slaves(self):
        BasePersonRoleEditor.setup_slaves(self)
        self.status_slave = ClientStatusSlave(self.conn, self.model,
                                              visual_mode=self.visual_mode)
        self.main_slave.attach_person_slave(self.status_slave)


class UserEditor(BasePersonRoleEditor):
    model_name = _('User')
    title = _('New User')
    model_type = LoginUser
    gladefile = 'BaseTemplate'
    USER_TAB_POSITION = 0

    help_section = 'user'
    ui_form_name = 'user'

    def create_model(self, conn):
        person = BasePersonRoleEditor.create_model(self, conn)
        return person.login_user or LoginUser(person=person,
                                              connection=conn, username="",
                                              password="", profile=None)

    def setup_slaves(self):
        BasePersonRoleEditor.setup_slaves(self)

        user_status = UserStatusSlave(self.conn, self.model,
                                      visual_mode=self.visual_mode)
        self.main_slave.attach_person_slave(user_status)

        passwd_fields = not self.edit_mode
        self.user_details = UserDetailsSlave(self.conn, self.model,
                                             show_password_fields=passwd_fields,
                                             visual_mode=self.visual_mode)
        tab_text = _('User Details')
        self.main_slave._person_slave.attach_custom_slave(self.user_details,
                                                          tab_text)

        tab_child = self.main_slave._person_slave.custom_tab
        notebook = self.main_slave._person_slave.person_notebook
        notebook.reorder_child(tab_child, position=self.USER_TAB_POSITION)
        notebook.set_current_page(self.USER_TAB_POSITION)

        tab_text = _('Branch Access')
        self.user_branches = UserBranchAccessSlave(self.conn, self.model)
        # XXX: workaround border being to large
        self.user_branches.vbox1.set_border_width(0)
        self.main_slave._person_slave.attach_extra_slave(self.user_branches,
                                                         tab_text)

    def validate_confirm(self):
        return (self.user_details.validate_confirm() and
                self.user_branches.validate_confirm())


class CardProviderEditor(BasePersonRoleEditor):
    model_name = _('Card Provider')
    title = _('New Card Provider')
    model_type = CreditProvider
    gladefile = 'BaseTemplate'

    #
    # BaseEditor hooks
    #

    def create_model(self, conn):
        person = BasePersonRoleEditor.create_model(self, conn)
        if person.credit_provider:
            return person.credi_provider

        return CreditProvider(person=person,
                              short_name='',
                              provider_type=CreditProvider.PROVIDER_CARD,
                              open_contract_date=datetime.datetime.today(),
                              connection=conn)

    def setup_slaves(self):
        BasePersonRoleEditor.setup_slaves(self)
        klass = CreditProviderDetailsSlave
        self.details_slave = klass(self.conn, self.model,
                                   visual_mode=self.visual_mode)
        slave = self.main_slave.get_person_slave()
        slave.attach_slave('person_status_holder', self.details_slave)


class EmployeeEditor(BasePersonRoleEditor):
    model_name = _('Employee')
    title = _('New Employee')
    model_type = Employee
    gladefile = 'BaseTemplate'

    ui_form_name = 'employee'

    def __init__(self, conn, model=None, person=None, role_type=None,
                 visual_mode=False, parent=None):
        self.visual_mode = visual_mode

        # Do not allow users of one branch edit employee from a different
        # branch
        if (model and model.branch and
            not model.branch == api.get_current_branch(conn)):
            self.visual_mode = True

        BasePersonRoleEditor.__init__(self, conn, model, role_type=role_type,
                                      visual_mode=self.visual_mode,
                                      parent=parent)
    #
    # BaseEditor hooks
    #

    def create_model(self, conn):
        person = BasePersonRoleEditor.create_model(self, conn)
        if not person.individual:
            Individual(person=person, connection=self.conn)
        employee = person.employee
        if not employee:
            employee = Employee(person=person, connection=conn, role=None)
        return employee

    def setup_slaves(self):
        BasePersonRoleEditor.setup_slaves(self)
        if not self.individual_slave:
            raise ValueError('This editor must have an individual slave')
        self.details_slave = EmployeeDetailsSlave(self.conn, self.model,
                                                  visual_mode=self.visual_mode)
        custom_tab_label = _('Employee Data')
        slave = self.individual_slave
        slave._person_slave.attach_custom_slave(self.details_slave,
                                                custom_tab_label)
        self.status_slave = EmployeeStatusSlave(self.conn, self.model,
                                                visual_mode=self.visual_mode)
        slave.attach_person_slave(self.status_slave)
        self.role_slave = EmployeeRoleSlave(self.conn, self.model,
                                            edit_mode=self.edit_mode,
                                            visual_mode=self.visual_mode)
        db_form = self._person_slave.db_form
        slave._person_slave.attach_role_slave(self.role_slave)

        if db_form:
            db_form.update_widget(self.role_slave.role,
                                  other=self.role_slave.role_lbl)
            db_form.update_widget(self.role_slave.salary,
                                  other=self.role_slave.salary_lbl)

        history_tab_label = _("Role History")
        history_slave = EmployeeRoleHistorySlave(self.model)
        slave._person_slave.attach_extra_slave(history_slave,
                                               history_tab_label)


class EmployeeRoleEditor(BaseEditor):
    model_type = EmployeeRole
    model_name = _('Employee Role')
    confirm_widgets = ['name']

    fields = dict(
        name=TextField(_('Name'), proxy=True, mandatory=True),
        )

    def __init__(self, conn, model=None, visual_mode=False):
        BaseEditor.__init__(self, conn, model, visual_mode=visual_mode)
        self.set_description(self.model.name)

    #
    # BaseEditorSlave Hooks
    #

    def create_model(self, conn):
        return EmployeeRole(connection=conn, name='')

    def on_cancel(self):
        # XXX This will prevent problems in case that you can't
        # update the connection.
        if not self.edit_mode:
            self.model_type.delete(self.model.id, connection=self.conn)

    #
    # Kiwi handlers
    #

    def on_name__validate(self, widget, value):
        if self.model.has_other_role(value):
            return ValidationError('This role already exists!')


class SupplierEditor(BasePersonRoleEditor):
    model_name = _('Supplier')
    title = _('New Supplier')
    model_type = Supplier
    gladefile = 'BaseTemplate'

    help_section = 'supplier'
    ui_form_name = 'supplier'

    #
    # BaseEditor hooks
    #

    def create_model(self, conn):
        person = BasePersonRoleEditor.create_model(self, conn)
        supplier = person.supplier
        if supplier is None:
            supplier = Supplier(person=person, connection=conn)
        return supplier

    def setup_slaves(self):
        BasePersonRoleEditor.setup_slaves(self)
        self.details_slave = SupplierDetailsSlave(self.conn, self.model,
                                                  visual_mode=self.visual_mode)
        slave = self.main_slave.get_person_slave()
        slave.attach_slave('person_status_holder', self.details_slave)


class TransporterEditor(BasePersonRoleEditor):
    model_name = _('Transporter')
    title = _('New Transporter')
    model_type = Transporter
    gladefile = 'BaseTemplate'

    help_section = 'transporter'
    ui_form_name = 'transporter'

    #
    # BaseEditor hooks
    #

    def create_model(self, conn):
        person = BasePersonRoleEditor.create_model(self, conn)
        transporter = person.transporter
        if transporter is None:
            transporter = Transporter(person=person,
                                      connection=conn)
        return transporter

    def setup_slaves(self):
        BasePersonRoleEditor.setup_slaves(self)
        self.details_slave = TransporterDataSlave(self.conn,
                                                  self.model,
                                                  visual_mode=self.visual_mode)
        slave = self.main_slave.get_person_slave()
        slave.attach_slave('person_status_holder', self.details_slave)


class BranchEditor(BasePersonRoleEditor):
    model_name = _('Branch')
    title = _('New Branch')
    model_type = Branch
    gladefile = 'BaseTemplate'

    help_section = 'branch'
    ui_form_name = 'branch'

    #
    # BaseEditor hooks
    #

    def create_model(self, conn):
        person = BasePersonRoleEditor.create_model(self, conn)
        branch = person.branch
        if branch is None:
            branch = Branch(person=person, connection=conn)

        return branch

    def setup_slaves(self):
        BasePersonRoleEditor.setup_slaves(self)
        self.status_slave = BranchDetailsSlave(self.conn, self.model,
                                               visual_mode=self.visual_mode)
        self.main_slave.attach_person_slave(self.status_slave)


def test_client():  # pragma nocover
    from stoqlib.gui.wizards.personwizard import run_person_role_dialog
    creator = api.prepare_test()
    retval = run_person_role_dialog(ClientEditor, None, creator.trans, None)
    api.finish_transaction(creator.trans, retval)


def test_employee_role():  # pragma nocover
    creator = api.prepare_test()
    role = creator.create_employee_role()
    run_dialog(EmployeeRoleEditor, parent=None, conn=creator.trans,
               model=role)


if __name__ == '__main__':  # pragma nocover
    test_employee_role()

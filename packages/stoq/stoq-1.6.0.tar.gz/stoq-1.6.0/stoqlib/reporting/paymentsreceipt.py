# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2011 Async Open Source <http://www.async.com.br>
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
##
##  Author(s): Stoq Team <stoq-devel@async.com.br>
##
##


from stoqlib.api import api
from stoqlib.lib.formatters import get_formatted_price, get_price_as_cardinal
from stoqlib.lib.translation import stoqlib_gettext
from stoqlib.reporting.base.defaultstyle import TABLE_LINE_BLANK
from stoqlib.reporting.base.tables import (TableColumn as TC, HIGHLIGHT_NEVER)
from stoqlib.reporting.template import BaseStoqReport

_ = stoqlib_gettext


class BasePaymentReceipt(BaseStoqReport):
    """ Base account receipt
    """
    report_name = _("Payment receipt")

    def __init__(self, filename, payment, order, date, *args, **kwargs):
        self.payment = payment
        self.order = order
        self.receipt_date = date
        BaseStoqReport.__init__(self, filename, self.report_name,
                                do_footer=False, landscape=False, *args,
                                **kwargs)
        self.identify_drawee()
        self.add_blank_space()
        self.identify_recipient()
        self.add_signature()

        # Create separator to cut the receipt copy.
        self.add_line(dash_pattern=1)

        # Duplicate data to generate a copy of receipt in same page.
        self.add_title(self.get_title())
        self.identify_drawee()
        self.add_blank_space()
        self.identify_recipient()
        self.add_signature()

    def get_recipient(self):
        """This should be implemented in subclasses"""
        raise NotImplementedError

    def get_drawee(self):
        """This should be implemented in subclasses"""
        raise NotImplementedError

    def identify_drawee(self):
        payer = self.get_drawee()
        data = []
        if payer:
            data.extend([
                [_("I/We Received from:"), payer.name],
                [_("Address:"), payer.get_address_string()],
            ])
        value = self.payment.value
        cols = [TC('', style='Normal-Bold', width=150),
                TC('', expand=True, truncate=True)]

        data.extend([
            [_("The importance of:"), get_price_as_cardinal(value).upper()],
            [_("Referring to:"), self.payment.description],
        ])

        self.add_paragraph(_('Drawee'), style='Normal-Bold')
        self.add_column_table(data, cols, do_header=False,
                              highlight=HIGHLIGHT_NEVER,
                              table_line=TABLE_LINE_BLANK)

    def identify_recipient(self):
        recipient = self.get_recipient()
        if recipient:
            name = recipient.name
            address = recipient.get_address_string()
            if recipient.individual:
                individual = recipient.individual
                doc = individual.cpf or individual.rg_number or ''
            elif recipient.company:
                doc = recipient.company.cnpj or ''
            else:
                raise AssertionError('Person should be individual or company')
        else:
            name = ''
            doc = ''
            address = ''

        cols = [TC('', style='Normal-Bold', width=150),
                TC('', expand=True, truncate=True)]

        self.add_paragraph(_('Recipient'), style='Normal-Bold')
        data = [
            [_("Recipient:"), name],
            [_("RG/CPF/CNPJ:"), doc],
            [_("Address:"), address],
        ]

        self.add_column_table(data, cols, do_header=False,
                              highlight=HIGHLIGHT_NEVER,
                              table_line=TABLE_LINE_BLANK)

    def add_signature(self):
        self.add_signatures([_("Recipient")])

    #
    # BaseReportTemplate hooks
    #

    def get_title(self):
        total_value = get_formatted_price(self.payment.value)
        return _('Receipt: %s - Value: %s - Date: %s') % (
                 self.payment.get_payment_number_str(),
                 get_formatted_price(total_value),
                 self.receipt_date.strftime('%x'))


class InPaymentReceipt(BasePaymentReceipt):
    """ Accounts receivable receipt
    """

    def get_drawee(self):
        return self.payment.group.payer

    def get_recipient(self):
        if self.order:
            drawee = self.order.branch.person
        else:
            store = self.payment.store
            drawee = api.get_current_branch(store).person
        return drawee


class OutPaymentReceipt(BasePaymentReceipt):
    """ Accounts payable receipt
    """

    def get_drawee(self):
        if self.order:
            payer = self.order.branch.person
        else:
            store = self.payment.store
            payer = api.get_current_branch(store).person
        return payer

    def get_recipient(self):
        if self.order:
            drawee = self.order.supplier.person
        else:
            drawee = self.payment.group.recipient
        return drawee

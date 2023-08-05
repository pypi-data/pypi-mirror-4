# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005, 2006 Async Open Source <http://www.async.com.br>
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
"""Credit Provider editor
"""

from kiwi.datatypes import ValidationError

from stoqlib.gui.editors.baseeditor import BaseEditorSlave
from stoqlib.domain.person import CreditProvider
from stoqlib.lib.translation import stoqlib_gettext
from stoqlib.lib.validators import validate_percentage

_ = stoqlib_gettext


class CreditProviderDetailsSlave(BaseEditorSlave):
    model_type = CreditProvider
    gladefile = 'CredProviderDetailsSlave'
    proxy_widgets = ('provider_id',
                     'short_name',
                     'open_contract_date',
                     'max_installments',
                     'payment_day',
                     'credit_fee',
                     'credit_installments_store_fee',
                     'credit_installments_provider_fee',
                     'debit_fee',
                     'debit_pre_dated_fee',
                     'monthly_fee',
                     'closing_day')

    def setup_proxies(self):
        self.proxy = self.add_proxy(self.model,
                                    CreditProviderDetailsSlave.proxy_widgets)

    #
    # Kiwi Callbacks
    #

    def on_monthly_fee__validate(self, widget, value):
        if value < 0:
            return ValidationError(_(u'The monthly fee must be positive.'))

    def _validate_day(self, widget, value):
        # 28 is the maximum allowed number on schema
        # Also, do not allow day 0 and negative for obvious reasons
        if not 1 <= value <= 28:
            return ValidationError(_('%s is not a valid day') % value)

    # day validators
    on_payment_day__validate = _validate_day
    on_closing_day__validate = _validate_day

    def _validate_percentage(self, widget, value):
        if not validate_percentage(value):
            return ValidationError(_('%s is not a valid percentage') % value)

    # percentage validators
    on_credit_fee__validate = _validate_percentage
    on_credit_installments_store_fee__validate = _validate_percentage
    on_credit_installments_provider_fee__validate = _validate_percentage
    on_debit_fee__validate = _validate_percentage
    on_debit_pre_dated_fee__validate = _validate_percentage

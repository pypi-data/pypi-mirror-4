# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2008-2012 Async Open Source <http://www.async.com.br>
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
##
"""Dialog for listing payment categories"""

import random

import gtk
from kiwi.datatypes import ValidationError
from kiwi.ui.forms import ColorField, ChoiceField, TextField

from stoqlib.api import api
from stoqlib.domain.payment.category import PaymentCategory
from stoqlib.domain.payment.payment import Payment
from stoqlib.gui.base.dialogs import run_dialog
from stoqlib.gui.editors.baseeditor import BaseEditor
from stoqlib.lib.message import yesno
from stoqlib.lib.translation import stoqlib_gettext

_ = stoqlib_gettext

_TANGO_PALETTE = [
    u'#eeeeec',
    u'#d3d7cf',
    u'#babdb6',
    u'#fce94f',
    u'#edd400',
    u'#c4a000',
    u'#8ae234',
    u'#73d216',
    u'#4e9a06',
    u'#fcaf3e',
    u'#f57900',
    u'#ce5c00',
    u'#e9b96e',
    u'#c17d11',
    u'#8f5902',
    u'#729fcf',
    u'#3465a4',
    u'#204a87',
    u'#ad7fa8',
    u'#75507b',
    u'#5c3566',
    u'#888a85',
    u'#555753',
    u'#2e3436',
    u'#ef2929',
    u'#cc0000',
    u'#a40000',
    ]


class PaymentCategoryEditor(BaseEditor):
    model_name = _('Payment Category')
    model_type = PaymentCategory
    confirm_widgets = ['name']
    proxy_widgets = ['category_type']

    fields = dict(
        name=TextField(_('Name'), proxy=True),
        color=ColorField(_('Color'), proxy=True),
        category_type=ChoiceField(_('Type'), data_type=int),
    )

    def __init__(self, store, model=None,
                 category_type=None, visual_mode=False):
        self._category_type = category_type or PaymentCategory.TYPE_PAYABLE
        BaseEditor.__init__(self, store, model, visual_mode=visual_mode)
        if category_type is not None:
            self.category_type.set_sensitive(False)

    #
    # BaseEditor
    #

    def validate_confirm(self):
        category_type = self.model.category_type
        if (not self.edit_mode or
            self._original_category_type == category_type):
            return True

        payments = self.store.find(Payment,
                                   category=self.model)
        payments_count = payments.count()

        if (payments_count > 0 and not
            yesno(_("Changing the payment type will remove this category "
                    "from %s payments. Are you sure?") % payments_count,
                  gtk.RESPONSE_NO, _("Change"), _("Don't change"))):
            return False

        for p in payments:
            p.category = None

        return True

    def create_model(self, store):
        used_colors = set([
            pc.color for pc in store.find(PaymentCategory)])
        random.shuffle(_TANGO_PALETTE)
        for color in _TANGO_PALETTE:
            if not color in used_colors:
                break
        return PaymentCategory(name=u'',
                               color=color,
                               category_type=int(self._category_type),
                               store=store)

    def setup_proxies(self):
        self.name.grab_focus()
        self.category_type.prefill([
            (_('Payable'), PaymentCategory.TYPE_PAYABLE),
            (_('Receivable'), PaymentCategory.TYPE_RECEIVABLE)])
        self.add_proxy(self.model, self.proxy_widgets)
        self._original_category_type = self.model.category_type

    #
    # Kiwi Callbacks
    #

    def on_name__validate(self, widget, new_name):
        if not new_name:
            return ValidationError(
                _(u"The payment category should have name."))
        if self.model.check_unique_value_exists(PaymentCategory.name,
                                                new_name):
            return ValidationError(
                _(u"The payment category '%s' already exists.") % new_name)


def test():  # pragma nocover
    creator = api.prepare_test()
    retval = run_dialog(PaymentCategoryEditor, None, creator.store, None)
    creator.store.confirm(retval)


if __name__ == '__main__':  # pragma nocover
    test()

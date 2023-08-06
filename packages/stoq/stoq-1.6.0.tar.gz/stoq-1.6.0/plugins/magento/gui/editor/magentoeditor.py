# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2012 Async Open Source <http://www.async.com.br>
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

"""Editors for magento"""

from stoqlib.domain.person import Branch, SalesPerson
from stoqlib.gui.editors.baseeditor import BaseEditor
from stoqlib.lib.message import warning
from stoqlib.lib.translation import stoqlib_gettext

from domain.magentoconfig import MagentoConfig
from magentolib import validate_connection

_ = stoqlib_gettext


class MagentoConfigEditor(BaseEditor):
    """An editor for :class:`MagentoConfig`"""

    gladefile = 'MagentoConfigEditor'
    model_type = MagentoConfig
    model_name = _('Magento config')
    size = (-1, -1)
    proxy_widgets = ('url',
                     'api_user',
                     'api_key',
                     'branch',
                     'salesperson',
                     'tz_hours')

    #
    #  BaseEditor Hooks
    #

    def create_model(self, store):
        return MagentoConfig(store=store,
                             url=u'',
                             # defaults to brazil
                             tz_hours=-3)

    def setup_proxies(self):
        self._setup_widgets()
        self.proxy = self.add_proxy(self.model,
                                    self.proxy_widgets)

    def validate_confirm(self):
        url = self._get_fixed_url(self.model.url)
        self.model.url = url

        api_user, api_key = (self.model.api_user, self.model.api_key)

        try:
            if not validate_connection(url, api_user, api_key):
                warning(_("Could not validate the connection. "
                          "Try verifying the url, user and key"))
                return False
        except Exception as err:
            warning(_("An error occurried when trying to validate the "
                      "connection:"), err.message)
            return False

        return super(MagentoConfigEditor, self).validate_confirm()

    #
    #  Private
    #

    def _setup_widgets(self):
        self.branch.prefill(
            [(branch.person.name, branch) for branch in
              self.store.find(Branch)])
        if self.model.branch:
            self.branch.update(self.model.branch)

        self.salesperson.prefill(
            [(salesperson.person.name, salesperson) for salesperson in
              self.store.find(SalesPerson)])
        if self.model.salesperson:
            self.salesperson.update(self.model.salesperson)

    def _get_fixed_url(self, url):
        if not url.startswith('http'):
            url = 'http://' + url
        if not url.endswith('xmlrpc'):
            while url.endswith('/'):
                url = url[:-1]
            if not url.endswith('index.php'):
                url = url + '/index.php'
            url = url + '/api/xmlrpc'

        return url

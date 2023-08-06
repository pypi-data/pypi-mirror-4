# -*- Mode: Python; coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2007 Async Open Source <http://www.async.com.br>
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

import os
import sys

from kiwi.environ import environ
from zope.interface import implements

from stoqlib.database.migration import PluginSchemaMigration
from stoqlib.lib.interfaces import IPlugin
from stoqlib.lib.pluginmanager import register_plugin

plugin_root = os.path.dirname(__file__)
sys.path.append(plugin_root)


class ECFPlugin(object):
    implements(IPlugin)
    name = u'ecf'

    def __init__(self):
        self.ui = None

    #
    #  IPlugin
    #

    def get_migration(self):
        environ.add_resource('ecfsql', os.path.join(plugin_root, 'sql'))
        return PluginSchemaMigration(self.name, 'ecfsql', ['*.sql'])

    def get_tables(self):
        return [('ecfdomain', ["ECFPrinter", "DeviceConstant"])]

    def activate(self):
        environ.add_resource('glade', os.path.join(plugin_root, 'glade'))
        # Do this in a nested import so we can import the plugin without
        # importing gtk.
        from ecfui import ECFUI
        self.ui = ECFUI()

    def get_dbadmin_commands(self):
        return []

    def handle_dbadmin_command(self, command, options, args):
        assert False


register_plugin(ECFPlugin)

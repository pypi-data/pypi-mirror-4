# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2006-2008 Async Open Source <http://www.async.com.br>
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
"""Database routines which are used by the testsuite"""

# This needs to before the other commits, so the externals/
# path is properly setup.
from stoqlib.lib.kiwilibrary import library
library  # pyflakes

import os
import socket

from kiwi.component import provide_utility, utilities
from kiwi.log import Logger

from stoqlib.database.admin import initialize_system, ensure_admin_user
from stoqlib.database.interfaces import (
    ICurrentBranch, ICurrentBranchStation, ICurrentUser)
from stoqlib.database.orm import AND
from stoqlib.database.runtime import new_transaction, get_connection
from stoqlib.database.settings import db_settings
from stoqlib.domain.person import Branch, LoginUser, Person
from stoqlib.domain.station import BranchStation
from stoqlib.importers.stoqlibexamples import create
from stoqlib.lib.interfaces import IApplicationDescriptions, ISystemNotifier
from stoqlib.lib.message import DefaultSystemNotifier
from stoqlib.lib.osutils import get_username
from stoqlib.lib.parameters import ParameterAccess
from stoqlib.lib.pluginmanager import get_plugin_manager
from stoqlib.lib.settings import get_settings

log = Logger('stoqlib.database.testsuite')


# This notifier implementation is here to workaround trial; which
# refuses to quit if SystemExit is raised or if sys.exit() is called.
# For now it is assumed that errors() are fatal, that might change in
# the near future


class TestsuiteNotifier(DefaultSystemNotifier):
    def __init__(self):
        self._messages = []

    def reset(self):
        messages = self._messages
        self._messages = []
        return messages

    def message(self, name, short, description):
        self._messages.append((name, short, description))

    def error(self, short, description):
        DefaultSystemNotifier.error(self, short, description)
        os._exit(1)

test_system_notifier = TestsuiteNotifier()


def _provide_database_settings():
    db_settings.username = os.environ.get('STOQLIB_TEST_USERNAME',
                                          get_username())
    db_settings.hostname = os.environ.get('PGHOST', 'localhost')
    db_settings.port = int(os.environ.get('PGPORT', '5432'))
    db_settings.dbname = os.environ.get('STOQLIB_TEST_DBNAME',
                                        '%s_test' % db_settings.username)
    db_settings.password = ''


def _provide_current_user():
    user = LoginUser.selectOneBy(username='admin',
                                 connection=get_connection())
    provide_utility(ICurrentUser, user, replace=True)


def _provide_current_station(station_name=None, branch_name=None):
    if not station_name:
        station_name = socket.gethostname()
    trans = new_transaction()
    if branch_name:
        branch = Person.selectOne(
            AND(Person.q.name == branch_name,
                Branch.q.person_id == Person.q.id),
            connection=trans)
    else:
        branches = Branch.select(connection=trans)
        if branches.count() == 0:
            person = Person(name="test", connection=trans)
            branch = Branch(person=person, connection=trans)
        else:
            branch = branches[0]

    provide_utility(ICurrentBranch, branch)

    station = BranchStation.get_station(trans, branch, station_name)
    if not station:
        station = BranchStation.create(trans, branch, station_name)

    assert station
    assert station.is_active

    provide_utility(ICurrentBranchStation, station)
    trans.commit(close=True)


def _provide_app_info():
    from stoqlib.lib.interfaces import IAppInfo
    from stoqlib.lib.appinfo import AppInfo
    info = AppInfo()
    info.set("name", "Stoqlib")
    info.set("version", "1.0.0")
    provide_utility(IAppInfo, info)

# Public API


def provide_database_settings(dbname=None, address=None, port=None, username=None,
                              password=None, create=True):
    """
    Provide database settings.
    :param dbname:
    :param address:
    :param port:
    :param username:
    :param password:
    :param create: Create a new empty database if one is missing
    """
    if not username:
        username = get_username()
    if not dbname:
        dbname = username + '_test'
    if not address:
        address = os.environ.get('PGHOST', '')
    if not port:
        port = os.environ.get('PGPORT', '5432')
    if not password:
        password = ""

    # Remove all old utilities pointing to the previous database.
    utilities.clean()
    provide_utility(ISystemNotifier, test_system_notifier, replace=True)
    _provide_application_descriptions()
    _provide_domain_slave_mapper()
    _provide_app_info()

    db_settings.address = address
    db_settings.port = port
    db_settings.dbname = dbname
    db_settings.username = username
    db_settings.password = password

    rv = False
    if create:
        conn = db_settings.get_default_connection()
        if not conn.databaseExists(dbname):
            log.warning('Database %s missing, creating it' % dbname)
            conn.createEmptyDatabase(dbname)
            rv = True
        conn.close()

    return rv


def _provide_domain_slave_mapper():
    from stoqlib.gui.interfaces import IDomainSlaveMapper
    from stoqlib.gui.domainslavemapper import DefaultDomainSlaveMapper
    provide_utility(IDomainSlaveMapper, DefaultDomainSlaveMapper(),
                    replace=True)


def _provide_application_descriptions():
    from stoq.lib.applist import ApplicationDescriptions
    provide_utility(IApplicationDescriptions, ApplicationDescriptions(),
                    replace=True)


def provide_utilities(station_name, branch_name=None):
    """
    Provide utilities like current user and current station.
    :param station_name:
    :param branch_name:
    """
    _provide_current_user()
    _provide_current_station(station_name, branch_name)
    _provide_domain_slave_mapper()


def _enable_plugins():
    manager = get_plugin_manager()
    for plugin in ['nfe', 'ecf']:
        if not manager.is_installed(plugin):
            # STOQLIB_TEST_QUICK won't let dropdb on testdb run. Just a
            # precaution to avoid trying to install it again
            manager.install_plugin(plugin)


def bootstrap_suite(address=None, dbname=None, port=5432, username=None,
                    password="", station_name=None, quick=False):
    """
    Test.
    :param address:
    :param dbname:
    :param port:
    :param username:
    :param password:
    :param station_name:
    :param quick:
    """

    # XXX: Rewrite docstring
    try:
        empty = provide_database_settings(
            dbname, address, port, username, password)

        # Reset the user settings (loaded from ~/.stoq/settings), so that user
        # preferences don't affect the tests.
        settings = get_settings()
        settings.reset()

        if quick and not empty:
            provide_utilities(station_name)
        else:
            # XXX: Why clearing_cache if initialize_system will drop the
            # database?!
            ParameterAccess.clear_cache()

            initialize_system(testsuite=True, force=True)
            _enable_plugins()
            ensure_admin_user("")
            create(utilities=True)
    except Exception:
        # Work around trial
        import traceback
        traceback.print_exc()
        os._exit(1)

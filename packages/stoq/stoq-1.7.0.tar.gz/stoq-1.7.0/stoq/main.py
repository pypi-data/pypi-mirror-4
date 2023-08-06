# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005-2011 Async Open Source <http://www.async.com.br>
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
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
## Author(s): Stoq Team <stoq-devel@async.com.br>
##
##
""" Stoq startup routines"""

import logging
import optparse

# To avoid kiwi dependency at startup
log = logging.getLogger(__name__)


def get_shell(args):
    log.info('parsing command line arguments: %s ' % (args, ))
    from stoq.lib.options import get_option_parser
    parser = get_option_parser()

    group = optparse.OptionGroup(parser, 'Stoq')
    group.add_option('', '--wizard',
                     action="store_true",
                     dest="wizard",
                     default=None,
                     help='Run the wizard')
    group.add_option('', '--login-username',
                     action="store",
                     dest="login_username",
                     default=None,
                     help='Username to login to stoq with')
    group.add_option('', '--no-splash-screen',
                     action="store_false",
                     dest="splashscreen",
                     default=True,
                     help='Disable the splash screen')
    group.add_option('', '--version',
                     action="store_true",
                     dest="version",
                     help='Show the application version')
    parser.add_option_group(group)

    options, args = parser.parse_args(args)

    if options.version:
        import stoq
        raise SystemExit(stoq.version)

    from stoq.gui.shell.shell import Shell
    return args, Shell(options)


def main(args):
    args, shell = get_shell(args)

    if len(args) < 2:
        appname = None
    else:
        appname = args[1].strip()
        if appname.endswith('/'):
            appname = appname[:-1]

        from stoq.lib.applist import get_application_names
        apps = get_application_names()

        if not appname in apps:
            raise SystemExit("'%s' is not an application. "
                             "Valid applications are: %s" % (appname, apps))

    shell.main(appname)

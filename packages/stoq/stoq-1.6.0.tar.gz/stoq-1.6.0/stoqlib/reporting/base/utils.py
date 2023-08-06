# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005 Async Open Source
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU Lesser General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
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
## Author(s): Stoq Team <stoq-devel@async.com.br>
##

""" Useful functions related to reports building and visualization. """

import os
import platform
import tempfile

from kiwi.log import Logger

from stoqlib.database.runtime import get_current_branch, get_default_store
from stoqlib.exceptions import DatabaseInconsistency
from stoqlib.lib.formatters import format_phone_number
from stoqlib.lib.translation import stoqlib_gettext
from stoqlib.reporting.template import get_logotype_path

_ = stoqlib_gettext
_system = platform.system()
log = Logger('reporting.utils')
# a list of programs to be tried when a report needs be viewed
PROGRAMS = [('evince', '--preview'), ('xpdf', '-z 100'), 'ggv']


def get_header_data():
    default_store = get_default_store()

    person = get_current_branch(default_store).person
    company = person.company
    main_address = person.get_main_address()

    if not person.name:
        raise DatabaseInconsistency("The person by ID %d should have a "
                                    "name at this point" % person.id)

    data = {
        'title': person.name,
        'logo_path': get_logotype_path(default_store),
        'lines': [],
        }

    # Address
    if main_address:
        data['lines'].append(main_address.get_address_string())

        address_parts = []
        if main_address.postal_code:
            address_parts.append(main_address.postal_code)
        if main_address.get_city():
            address_parts.append(main_address.get_city())
        if main_address.get_state():
            address_parts.append(main_address.get_state())

        if address_parts:
            data['lines'].append(' - '.join(address_parts))

    # Contact
    contact_parts = []
    if person.phone_number:
        contact_parts.append(_("Phone: %s") %
                             format_phone_number(person.phone_number))
    if person.fax_number:
        contact_parts.append(_("Fax: %s") %
                             format_phone_number(person.fax_number))
    if contact_parts:
        data['lines'].append(' - '.join(contact_parts))

    # Company details
    if company:
        company_parts = []
        if company.get_cnpj_number():
            company_parts.append(_("CNPJ: %s") % company.cnpj)
        if company.get_state_registry_number():
            company_parts.append(_("State Registry: %s") %
                                 company.state_registry)

        if company_parts:
            data['lines'].append(' - '.join(company_parts))

    return data


def build_report(report_class, *args, **kwargs):
    """ Given a class (BaseReportTemplate instance), build a report. It is
    important to note that this function create a temporary file where the
    report will be drawed to -- the name of the temporary file is returned.

    :param report_class: The report class to be build.
    :type:             A BaseReportTemplate instance

    If specified, extra parameters will be send to the report class
    constructor.
    """
    filename = tempfile.mktemp()
    report = report_class(filename, *args, **kwargs)
    report.save()
    return filename


def print_file(filename, printer=None, extra_opts=[]):
    """ Given a filename try to print it. If no printer is specified, print
    the file on the default one.

    :param filename:   The filename to print.
    :type:             str

    :param printer:    The printer name where to print.
    :type:             str

    :param extra_opts: Extra options to be passed to the printing command.
    :type:             list of strings
    """
    if not os.path.exists(filename):
        raise ValueError("File %s not found" % filename)
    options = " ".join(extra_opts)
    if printer:
        options += " -P%s" % printer
    if _system == "Linux":
        ret = os.system("lpr %s %s" % (options, filename))
        os.remove(filename)
    elif _system == "Windows":
        log.info("Starting PDF reader for %r" % (filename, ))
        # Simply execute the file
        ret = os.startfile(filename)
    else:
        raise SystemExit("unknown system: %s" % (_system, ))

    return ret


def print_preview(filename, keep_file=False):
    """ Try preview the filename using one of the PDF viewers registred in
    the package.

    :param keep_file:  If the file don't must be deleted after the program
                       finish.
    :type:             bool
    """
    if not os.path.exists(filename):
        raise OSError("the file does not exist")

    path = os.environ['PATH'].split(':')

    for program in PROGRAMS:
        args = []
        if isinstance(program, tuple):
            # grab args and program from tuple
            args.extend(program[1:])
            program = program[0]
        elif not isinstance(program, str):
            raise AssertionError
        args.append(filename)
        for part in path:
            full = os.path.join(part, program)
            if not os.access(full, os.R_OK | os.X_OK):
                continue
            if not os.fork():
                args = " ".join(args)
                os.system("%s %s" % (full, args))
                if not keep_file:
                    os.remove(filename)
                # See http://www.gtk.org/faq/#AEN505 -- _exit()
                # keeps file descriptors open, which avoids X async
                # errors after we close the child window.
                os._exit(-1)
            return
    print "Could not find a pdf viewer, aborting"

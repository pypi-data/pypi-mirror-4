# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2011 Async Open Source <http://www.async.com.br>
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
"""Test pyflakes on stoq, stoqlib and plugins directories

Useful to early find syntax errors and other common problems.
"""

import _ast
import compiler
import os
import sys
import unittest

import pyflakes

import stoqlib

# stolen from pyflakes


def check(codeString, filename, warnings):
    try:
        if pyflakes.__version__ == '0.4.0':
            compile(codeString, filename, "exec")
            tree = compiler.parse(codeString)
        else:
            tree = compile(codeString, filename, "exec", _ast.PyCF_ONLY_AST)
    except (SyntaxError, IndentationError), value:
        msg = value.args[0]

        (lineno, offset, text) = value.lineno, value.offset, value.text

        # If there's an encoding problem with the file, the text is None.
        if text is None:
            # Avoid using msg, since for the only known case, it contains a
            # bogus message that claims the encoding the file declared was
            # unknown.
            print >> sys.stderr, "%s: problem decoding source" % (filename, )
        else:
            line = text.splitlines()[-1]

            if offset is not None:
                offset = offset - (len(text) - len(line))

            print >> sys.stderr, '%s:%d: %s' % (filename, lineno, msg)
            print >> sys.stderr, line

            if offset is not None:
                print >> sys.stderr, " " * offset, "^"

        return 1
    except UnicodeError, msg:
        print >> sys.stderr, 'encoding error at %r: %s' % (filename, msg)
        return 1
    else:
        # Okay, it's syntactically valid.  Now parse it into an ast and check
        # it.
        w = checker.Checker(tree, filename)
        warnings.extend(w.messages)
        return len(warnings)

checker = __import__('pyflakes.checker').checker


class TestPyflakes(unittest.TestCase):
    def setUp(self):
        self.root = os.path.dirname(os.path.dirname(stoqlib.__file__)) + '/'

    def _get_filenames(self):
        rv = []
        for name in ['stoq', 'stoqlib', 'plugins']:
            path = os.path.join(self.root, name)
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    if not filename.endswith('.py'):
                        continue
                    filename = os.path.join(dirpath, filename)
                    rv.append(filename)
        return rv

    def testPyflakes(self):
        warnings = []
        msgs = []
        result = 0
        for filename in self._get_filenames():
            try:
                fd = file(filename, 'U')
                try:
                    result = check(fd.read(), filename, warnings)
                finally:
                    fd.close()
            except IOError, msg:
                print >> sys.stderr, "%s: %s" % (filename, msg.args[1])
                result = 1

        warnings.sort(lambda a, b: cmp(a.lineno, b.lineno))
        for warning in warnings:
            msg = str(warning).replace(self.root, '')
            msgs.append(msg)
        if result:
            self.fail("%d warnings:\n%s\n" % (
                len(msgs), '\n'.join(msgs), ))

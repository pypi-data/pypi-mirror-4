# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005-2011 Async Open Source
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

#
# Dependency checking
#

from stoq.lib.dependencies import DependencyChecker
dc = DependencyChecker()
dc.text_mode = True
# We don't need latest kiwi in here
dc.check_kiwi([1, 9, 26])

#
# Package installation
#

import os
import sys

from kiwi.dist import setup, listfiles, listpackages

from stoq import website, version


building_egg = 'bdist_egg' in sys.argv
if building_egg:
    python_dir = ''
    plugin_dir = 'stoq/data'
else:
    python_dir = 'lib/stoqlib/'
    plugin_dir = python_dir


def listplugins(plugins, exts):
    dirs = []
    for package in listpackages('plugins'):
        # strip plugins
        dirs.append(package.replace('.', '/'))
    files = []
    for directory in dirs:
        install_dir = 'lib/stoqlib/%s' % directory
        files.append((install_dir, listfiles(directory, '*.py')))
        files.append((install_dir, listfiles(directory, '*.plugin')))

    for plugin in plugins:
        for kind, suffix in exts:
            x = listfiles('plugins', plugin, kind, suffix)
            if x:
                path = python_dir + '/plugins/%s/%s'
                files.append((path % (plugin, kind), x))

        files.append((python_dir + 'plugins/' + plugin,
                      listfiles('plugins', plugin, '*.py')))

    return files


def list_templates():
    files = []
    dir_prefix = '$datadir/'
    for root, _, _ in os.walk('data/template'):
        parts = root.split(os.sep)
        files.append((dir_prefix + os.sep.join(parts[1:]),
                     listfiles(*(parts + ['*html']))))
        files.append((dir_prefix + os.sep.join(parts[1:]),
                     listfiles(*(parts + ['*css']))))
    return files

packages = listpackages('stoq')
packages.extend(listpackages('stoqlib', exclude='stoqlib.tests'))

scripts = [
    'bin/stoq',
    'bin/stoqdbadmin',

    # FIXME: move these to /usr/lib/stoq/
    'bin/stoqcreatedbuser',
    'bin/stoq-daemon',
    ]
templates = []
install_requires = []
data_files = [
    ('$datadir/csv', listfiles('data', 'csv', '*.csv')),
    ('$datadir/glade', listfiles('data', 'glade', '*.ui')),
    ('$datadir/misc', listfiles('data/misc', '*.*')),
    ('$datadir/pixmaps', listfiles('data', 'pixmaps', '*.png')),
    ('$datadir/pixmaps', listfiles('data', 'pixmaps', '*.svg')),
    ('$datadir/pixmaps', listfiles('data', 'pixmaps', '*.jpg')),
    ('$datadir/pixmaps', listfiles('data', 'pixmaps', '*.gif')),
    ('$datadir/pixmaps', listfiles('data', 'pixmaps', '*.bmp')),
    ('$datadir/sql', listfiles('data', 'sql', '*.sql')),
    ('$datadir/sql', listfiles('data', 'sql', '*.py')),
    ('$datadir/uixml', listfiles('data', 'uixml', '*.xml')),
    ('$datadir/html', listfiles('data', 'html', '*.html')),
    ('$datadir/html/css', listfiles('data', 'html', 'css', '*.css')),
    ('$datadir/html/images', listfiles('data', 'html', 'images', '*.png')),
    ('$datadir/html/js', listfiles('data', 'html', 'js', '*.js')),
    ]

data_files += list_templates()

if building_egg:
    data_files.append(
        ('stoq/data/docs',
         ['AUTHORS', 'CONTRIBUTORS', 'COPYING', 'COPYING.pt_BR',
          'COPYING.stoqlib', 'README', 'docs/copyright']))
    install_requires.append('stoqdrivers')
else:
    data_files.extend([
    ('share/applications', ['stoq.desktop']),
    ('share/doc/stoq', ['AUTHORS', 'CONTRIBUTORS', 'COPYING', 'COPYING.pt_BR',
                        'COPYING.stoqlib', 'README', 'docs/copyright']),
    ('share/gnome/help/stoq/C', listfiles('docs/manual/pt_BR', '*.page')),
    ('share/gnome/help/stoq/C', listfiles('docs/manual/pt_BR', '*.xml')),
    ('share/gnome/help/stoq/C/figures',
     listfiles('docs/manual/pt_BR/figures', '*.png')),
    ('share/gnome/help/stoq/C/figures',
     listfiles('docs/manual/pt_BR/figures', '*.svg')),
    ('share/icons/hicolor/48x48/apps', ['data/pixmaps/stoq.png']),
    ('share/polkit-1/actions', ['data/br.com.stoq.createdatabase.policy']),
    ('$sysconfdir/stoq', '')])

resources = dict(
    locale='$prefix/share/locale',
    plugin='$prefix/lib/stoqlib/plugins',
    )
global_resources = dict(
    config='$sysconfdir/stoq',
    csv='$datadir/csv',
    docs='$prefix/share/doc/stoq',
    glade='$datadir/glade',
    uixml='$datadir/uixml',
    html='$datadir/html',
    misc='$datadir/misc',
    pixmaps='$datadir/pixmaps',
    sql='$datadir/sql',
    template='$datadir/template',
    )

PLUGINS = ['ecf', 'nfe', 'books', 'magento']
PLUGIN_EXTS = [('csv', '*csv'),
               ('glade', '*.ui'),
               ('sql', '*.sql'),
               ('sql', '*.py')]

data_files += listplugins(PLUGINS, PLUGIN_EXTS)

setup(name='stoq',
      version=version,
      author="Async Open Source",
      author_email="stoq-devel@async.com.br",
      description="A powerful retail system",
      long_description="""
      Stoq is an advanced retails system which has as main goals the
      usability, good devices support, and useful features for retails.
      """,
      url=website,
      license="GNU GPL 2.0 and GNU LGPL 2.1 (see COPYING and COPYING.stoqlib)",
      packages=packages,
      data_files=data_files,
      scripts=scripts,
      resources=resources,
      install_requires=install_requires,
      global_resources=global_resources,
      templates=templates,
      zip_safe=True)

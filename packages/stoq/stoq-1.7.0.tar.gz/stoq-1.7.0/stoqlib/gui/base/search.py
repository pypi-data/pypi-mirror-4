# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005, 2006, 2007 Async Open Source
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
""" Implementation of basic dialogs for searching data """

from dateutil.relativedelta import relativedelta
import os

import gtk
from kiwi.argcheck import argcheck
from kiwi.enums import SearchFilterPosition
from kiwi.environ import environ
from kiwi.log import Logger
from kiwi.ui.delegates import GladeSlaveDelegate
from kiwi.ui.search import (ComboSearchFilter, SearchSlaveDelegate,
                            DateSearchOption)
from kiwi.utils import gsignal
from storm.store import Store

from stoqlib.api import api
from stoqlib.database.orm import ORMObject
from stoqlib.database.queryexecuter import StoqlibQueryExecuter
from stoqlib.gui.base.dialogs import BasicDialog, run_dialog
from stoqlib.gui.base.gtkadds import button_set_image_with_label
from stoqlib.gui.editors.baseeditor import BaseEditor
from stoqlib.lib.decorators import public
from stoqlib.lib.defaults import get_weekday_start
from stoqlib.lib.osutils import get_application_dir
from stoqlib.lib.parameters import sysparam
from stoqlib.lib.permissions import PermissionManager
from stoqlib.lib.translation import stoqlib_gettext

_ = stoqlib_gettext

log = Logger(__name__)


class _SearchDialogDetailsSlave(GladeSlaveDelegate):
    """ Slave for internal use of SearchEditor, offering an eventbox for a
    toolbar and managing the 'New' and 'Edit' buttons. """

    gladefile = 'SearchDialogDetailsSlave'

    gsignal('details')
    gsignal('print')

    #
    # Kiwi handlers
    #

    def on_details_button__clicked(self, button):
        self.emit('details')

    def on_print_button__clicked(self, button):
        self.emit('print')


class StoqlibSearchSlaveDelegate(SearchSlaveDelegate):
    def __init__(self, columns, tree=False, restore_name=None):
        self._restore_name = restore_name
        self._settings_key = 'search-columns-%s' % (
            api.get_current_user(api.get_default_store()).username, )
        self._columns = self.restore_columns(columns)

        SearchSlaveDelegate.__init__(self, self._columns, tree=tree)
        self.search.connect("search-completed",
                            self._on_search__search_completed)

    #
    #  Public API
    #

    def save_columns(self):
        if not self._restore_name:
            return

        d = {}
        treeview = self.search.results.get_treeview()
        for position, col in enumerate(treeview.get_columns()):
            # Can happen if there's an empty space on columns' header.
            # Normally on searchs that doesn't have an expand column.
            if not hasattr(col, 'attribute'):
                continue
            d[col.attribute] = (
                col.get_visible(),
                col.get_width(),
                col.get_sort_indicator(),
                int(col.get_sort_order()),  # enums are not serializable
                position,
                )

        columns = api.user_settings.get(self._settings_key, {})
        columns[self._restore_name] = d

    def restore_columns(self, cols):
        if not self._restore_name:
            return cols

        columns = api.user_settings.get(self._settings_key, {})
        if columns:
            saved = columns.get(self._restore_name, {})
        else:
            saved = self._migrate_from_pickle()

        cols_dict = {}
        for original_pos, col in enumerate(cols):
            attr = col.attribute
            props = saved.get(attr)
            # This will happen for two reasons: a) the column is referenced by
            # another one (only the column that references is saved) and
            # b) Its a brand new column (not saved in the preferences)
            if not props:
                cols_dict[attr] = (col, original_pos)
                continue

            col.visible = props[0]
            # Expanded columns should not have a width set
            if not col.expand:
                col.width = props[1]

            # We didn't store sorted and order before
            if len(props) <= 2:
                continue

            col.sorted = props[2]
            col.order = props[3]

            pos = props[4]
            # If col references another column, the referenced column
            # should appear before this col
            if col.column:
                referenced_col = cols_dict[col.column][0]
                cols_dict[col.column] = (referenced_col, pos)
                cols_dict[attr] = (col, pos + 1)
                if col.sorted:
                    referenced_col.sorted, col.sorted = True, False
            else:
                cols_dict[attr] = (col, pos)

        cols.sort(key=lambda col: cols_dict[col.attribute][1])
        return cols

    def set_message(self, message):
        self.search.results.set_message(message)

    def get_column_by_attribute(self, attribute):
        """Returns a column by its model attribute."""
        for column in self._columns:
            if column.attribute == attribute:
                return column

    #
    #  Private
    #

    def _migrate_from_pickle(self):
        username = api.get_current_user(api.get_default_store()).username
        filename = os.path.join(get_application_dir(), 'columns-%s' % username,
                                self._restore_name + '.pickle')
        log.info("Migrating columns from pickle: %s" % (filename, ))
        try:
            with open(filename) as fd:
                import cPickle
                return cPickle.load(fd)
        except Exception, e:
            log.info("Exception while migrating: %r" % (e, ))
            return {}

    #
    #  Callbacks
    #

    def _on_search__search_completed(self, search, results, states):
        if not len(results):
            self.set_message(_("Nothing found."))


class SearchDialogPrintSlave(GladeSlaveDelegate):
    """ Slave for internal use of SearchEditor, offering an eventbox for a
    toolbar and managing the 'print_price_button' buttons. """

    gladefile = 'SearchDialogPrintSlave'

    gsignal('print')

    #
    # Kiwi handlers
    #

    def on_print_price_button__clicked(self, button):
        self.emit('print')


class SearchDialogButtonSlave(GladeSlaveDelegate):
    """ Slave for internal use of SearchEditor, offering an eventbox for a
    toolbar and managing buttons. """

    gladefile = 'SearchDialogButtonSlave'

    gsignal('click')

    #
    # Kiwi handlers
    #

    def on_button__clicked(self, button):
        self.emit('click')

#
# Base dialogs for search.
#


@public(since="1.5.0")
class SearchDialog(BasicDialog):
    """  Base class for *all* the search dialogs, responsible for the list
    construction and "Filter" and "Clear" buttons management.

    This class must be subclassed and its subclass *must* implement the methods
    'get_columns' and 'get_query_and_args' (if desired, 'get_query_and_args'
    can be implemented in the user's slave class, so SearchDialog will get its
    slave instance and call the method directly). Its subclass also must
    implement a setup_slaves method and call its equivalent base class method
    as in:

    >>> def setup_slave(self):
    ...    SearchDialog.setup_slaves(self)

    or then, call it in its constructor, like:

    >>> def __init__(self, *args):
    ...     SearchDialog.__init__(self)

    :cvar table: the table type which we will query on to get the objects.
    :cvar searchbar_labels: labels for SearchBar entry and date fields
    :cvar searchbar_result_strings: a tuple where each item has a singular
      and a plural form for searchbar results label
    :cvar advanced_search: If the advanced search is enabled or disabled
    """
    main_label_text = ''
    title = ''
    table = None
    search_table = None
    search_labels = None
    selection_mode = gtk.SELECTION_BROWSE
    size = ()
    advanced_search = True
    tree = False

    @argcheck(object, object, object, bool, basestring, int, bool)
    def __init__(self, store, table=None, search_table=None, hide_footer=True,
                 title='', selection_mode=None, double_click_confirm=False):
        """
        A base class for search dialog inheritance

        :param store: a store
        :param table:
        :param search_table:
        :param hide_footer:
        :param title:
        :param selection_mode:
        :param double_click_confirm: If double click a item in the list should
          automatically confirm
        """

        self.store = store
        self.search_table = self._setup_search_table(table, search_table)
        self.selection_mode = self._setup_selection_mode(selection_mode)
        self.summary_label = None
        self.double_click_confirm = double_click_confirm

        BasicDialog.__init__(self, hide_footer=hide_footer,
                             main_label_text=self.main_label_text,
                             title=title or self.title,
                             size=self.size)

        self.executer = StoqlibQueryExecuter(store)
        # FIXME: Remove this limit, but we need to migrate all existing
        #        searches to use lazy lists first. That in turn require
        #        us to rewrite the queries in such a way that count(*)
        #        will work properly.
        self.executer.set_limit(sysparam(self.store).MAX_SEARCH_RESULTS)
        self.set_table(self.search_table)

        self.enable_window_controls()
        self.disable_ok()
        self.set_ok_label(_('Se_lect Items'))
        self._setup_search()
        self._setup_details_slave()

        self.create_filters()
        self.setup_widgets()

    def _setup_search_table(self, table, search_table):
        search_table = search_table or self.search_table
        table = table or self.table
        if not (table or search_table):
            raise ValueError(
                "%r must define a table or search_table attribute" % self)
        return search_table or table

    def _setup_selection_mode(self, selection_mode):
        # For consistency do not allow none or single, in other words,
        # only allowed values are browse and multiple so we always will
        # be able to use both the keyboard and the mouse to select items
        # in the search list.
        selection_mode = selection_mode or self.selection_mode
        if (selection_mode != gtk.SELECTION_BROWSE and
            selection_mode != gtk.SELECTION_MULTIPLE):
            raise ValueError('Invalid selection mode %r' % selection_mode)
        return selection_mode

    def _setup_search(self):
        self.search = StoqlibSearchSlaveDelegate(
            self.get_columns(),
            tree=self.tree,
            restore_name=self.__class__.__name__,
            )
        self.search.set_query_executer(self.executer)
        if self.advanced_search:
            self.search.enable_advanced_search()
        self.attach_slave('main', self.search)
        self.header.hide()

        self.results = self.search.search.results
        self.results.set_selection_mode(self.selection_mode)
        self.results.connect('cell-edited', self._on_results__cell_edited)
        self.results.connect('selection-changed',
                             self._on_results__selection_changed)
        self.results.connect('row-activated', self._on_results__row_activated)

        self.search.search.connect("search-completed",
                                   self._on_search__search_completed)

    def _setup_details_slave(self):
        # FIXME: Gross hack
        has_details_btn = hasattr(self, 'on_details_button_clicked')
        has_print_btn = hasattr(self, 'on_print_button_clicked')
        if not (has_details_btn or has_print_btn):
            self._details_slave = None
            return
        self._details_slave = _SearchDialogDetailsSlave()
        self.attach_slave('details_holder', self._details_slave)
        if has_details_btn:
            self._details_slave.connect("details",
                                        self.on_details_button_clicked)
        else:
            self._details_slave.details_button.hide()
        if has_print_btn:
            self._details_slave.connect("print", self.on_print_button_clicked)
            self.set_print_button_sensitive(False)
            self.results.connect('has-rows', self._has_rows)
        else:
            self._details_slave.print_button.hide()

    #
    # Public API
    #

    def add_button(self, label, stock=None, image=None):
        """Adds a button in the bottom of the dialog.

        :param label: the text that will be displayed by the button.
        :param stock: the gtk stock id to be used in the button.
        :param image: the image filename.
        """
        button = gtk.Button(label=label)
        if image:
            image_widget = gtk.Image()
            image_widget.set_from_file(
                environ.find_resource('pixmaps', image))
            image_widget.show()
            button.set_image(image_widget)
        elif stock:
            button_set_image_with_label(button, stock, label)
        self.action_area.set_layout(gtk.BUTTONBOX_START)
        self.action_area.pack_start(button, False, False, 6)
        return button

    @argcheck(bool)
    def set_details_button_sensitive(self, value):
        self._details_slave.details_button.set_sensitive(value)

    @argcheck(bool)
    def set_print_button_sensitive(self, value):
        self._details_slave.print_button.set_sensitive(value)

    def get_selection(self):
        mode = self.results.get_selection_mode()
        if mode == gtk.SELECTION_BROWSE:
            return self.results.get_selected()
        return self.results.get_selected_rows()

    def confirm(self, retval=None):
        """Confirms the dialog
        :param retval: optional parameter which will be selected when the
          dialog is closed
        """
        if retval is None:
            retval = self.get_selection()
        self.retval = retval
        self.search.save_columns()
        # FIXME: This should chain up so the "confirm" signal gets emitted
        self.close()

    def cancel(self, *args):
        self.retval = []
        self.search.save_columns()
        # FIXME: This should chain up so the "cancel" signal gets emitted
        self.close()

    def set_table(self, table):
        self.executer.set_table(table)
        self.search_table = table

    # FIXME: -> remove/use

    def set_searchbar_labels(self, *args):
        search_filter = self.search.get_primary_filter()
        search_filter.set_label(args[0])

    def set_searchbar_search_string(self, string):
        if string == self.get_searchbar_search_string():
            return
        search_filter = self.search.get_primary_filter()
        search_filter.entry.set_text(string)

    def get_searchbar_search_string(self):
        search_filter = self.search.get_primary_filter()
        return search_filter.get_state().text

    def set_result_strings(self, *args):
        pass

    def set_text_field_columns(self, columns):
        """See :class:`SearchSlaveDelegate.set_text_field_columns`
        """
        self.search.set_text_field_columns(columns)

    def disable_search_entry(self):
        """See :class:`SearchSlaveDelegate.disable_search_entry`
        """
        self.search.disable_search_entry()

    def add_filter(self, search_filter, position=SearchFilterPosition.BOTTOM,
                   columns=None, callback=None):
        """See :class:`SearchSlaveDelegate.add_filter`
        """
        self.search.add_filter(search_filter, position, columns, callback)

    def row_activate(self, obj):
        """This is called when an item in the results list is double clicked.

        :param obj: the item that was double clicked.
        """
        if self.double_click_confirm:
            # But only if its also confirmable with ok_button
            if self.ok_button.props.sensitive:
                self.confirm()

    #
    # Filters
    #

    def create_branch_filter(self, label=None):
        from stoqlib.domain.person import Branch
        branches = Branch.get_active_branches(self.store)
        items = [(b.person.name, b.id) for b in branches]
        #if not items:
        #    raise ValueError('You should have at least one branch at '
        #                      'this point')
        items.insert(0, (_("Any"), None))

        if not label:
            label = _('Branch:')
        branch_filter = ComboSearchFilter(label, items)
        current = api.get_current_branch(self.store)
        if current:
            branch_filter.select(current.id)

        return branch_filter

    def create_payment_filter(self, label=None):
        from stoqlib.domain.payment.method import PaymentMethod
        methods = PaymentMethod.get_active_methods(self.store)
        items = [(_('Any'), None)]
        for method in methods:
            if method.method_name == 'multiple':
                continue
            items.append((method.description, method))

        if not label:
            label = _('Method:')
        payment_filter = ComboSearchFilter(label, items)
        payment_filter.select(None)

        return payment_filter

    def create_provider_filter(self, label=None):
        from stoqlib.domain.payment.card import CreditProvider
        providers = CreditProvider.get_card_providers(self.store)
        items = [(p.short_name, p) for p in providers]
        items.insert(0, (_("Any"), None))

        if not label:
            label = _('Provider:')
        provider_filter = ComboSearchFilter(label, items)

        return provider_filter

    #
    # Callbacks
    #

    def _on_search__search_completed(self, search, results, states):
        self.search_completed(results, states)

    def _on_results__cell_edited(self, results, obj, attr):
        """Override this method on child when it's needed to perform some
        tasks when editing a row.
        """

    def _on_results__selection_changed(self, results, selected):
        self.update_widgets()
        if selected:
            self.enable_ok()
        else:
            self.disable_ok()

    def _on_results__row_activated(self, results, obj):
        self.row_activate(obj)

    def _has_rows(self, results, obj):
        self.set_print_button_sensitive(obj)

    #
    # Hooks
    #

    def create_filters(self):
        raise NotImplementedError(
            "create_filters() must be implemented in %r" % self)

    def setup_widgets(self):
        pass

    def get_columns(self):
        raise NotImplementedError(
            "get_columns() must be implemented in %r" % self)

    def update_widgets(self):
        """Subclass can have an 'update_widgets', and this method will be
        called when a signal is emitted by 'Filter' or 'Clear' buttons and
        also when a list item is selected. """

    def search_completed(self, results, states):
        pass


class SearchEditorToolBar(GladeSlaveDelegate):
    """ Slave for internal use of SearchEditor, offering an eventbox for a
    toolbar and managing the 'New' and 'Edit' buttons. """

    toplevel_name = 'ToolBar'
    gladefile = 'SearchEditor'
    domain = 'stoqlib'

    gsignal('edit')
    gsignal('add')

    #
    # Kiwi handlers
    #

    def on_edit_button__clicked(self, button):
        self.emit('edit')

    def on_new_button__clicked(self, button):
        self.emit('add')


class SearchEditor(SearchDialog):
    """ Base class for a search "editor" dialog, that offers a 'new' and
    'edit' button on the dialog footer. The 'new' and 'edit' buttons will
    call 'editor_class' sending as its parameters a new connection and the
    object to edit for 'edit' button.

    This is also a subclass of SearchDialog and the same rules are required.

    Simple example:

    >>> from stoqlib.domain.person import ClientView
    >>> from stoqlib.gui.editors.personeditor import ClientEditor

    >>> class ClientSearch(SearchEditor):
    ...     title = _("Client Search")
    ...     table = ClientView
    ...     editor_class = ClientEditor
    ...     size = (465, 390)
    ...     searchbar_result_strings = _("Client"), _("Clients")
    ...
    ...     def get_columns(self):
    ...         return [Column('name', _('Client name'), data_type=str, width=90),
    ...                 Column('status', _('Status'), data_type=str,
    ...                         expand=True)]

    This will create a new editor called ClientSearch:

      - It will be populated using the table ClientView.
      - The title of the editor is "Client Search".
      - To create new Client objects or to edit an existing Client object the
        ClientEditor table will be used, which needs to be a subclass of BaseEditor.
      - The size of the new dialog will be 465 pixels wide and 390 pixels high.
      - When displaying results, the verb client and clients will be used, eg:
        ``1 client`` or ``34 clients``.
      - The get_columns() methods is required to be implemented, otherwise
        there's no way to know which data is going to be displayed.
        get_columns must return a list of kiwi objectlist columns.
        In this case we will display two columns, brand and description.
        They will be fetched from the client object using the attribute brand or
        description. Both of them are strings (data_type=str), the width of
        the first column is 90 pixels and the second column is expanded so
        it uses the rest of the available width.

    """
    has_new_button = has_edit_button = True
    model_list_lookup_attr = 'id'

    def __init__(self, store, table=None, editor_class=None, interface=None,
                 search_table=None, hide_footer=True,
                 title='', selection_mode=gtk.SELECTION_BROWSE,
                 hide_toolbar=False, double_click_confirm=False):
        """
        Create a new SearchEditor object.
        :param store:
        :param table:
        :param editor_class:
        :param interface: The interface which we need to apply to the objects in
          kiwi list to get adapter for the editor.
        :param search_table:
        :param hide_footer:
        :param title:
        :param selection_mode:
        :param hide_toolbar:
        :param double_click_confirm: If double click a item in the list should
          automatically confirm. Double click confirms takes precedence over
          editor_class (ie, if double_click_confirmis is True, it will
          confirm the dialog, instead of opening the editor).
        """

        self.interface = interface
        self._read_only = False
        self._message_bar = None

        SearchDialog.__init__(self, store, table, search_table,
                              hide_footer=hide_footer, title=title,
                              selection_mode=selection_mode,
                              double_click_confirm=double_click_confirm)

        self._setup_slaves()
        if hide_toolbar:
            self.accept_edit_data = False
            self._toolbar.get_toplevel().hide()
        else:
            if not (self.has_new_button or self.has_edit_button):
                raise ValueError("You must set hide_footer=False instead "
                                 "of disable these two attributes.")

            editor_class = editor_class or self.editor_class
            if not editor_class:
                raise ValueError('An editor_class argument is required')
            if not issubclass(editor_class, BaseEditor):
                raise TypeError("editor_class must be a BaseEditor subclass")
            self.editor_class = editor_class

            self.accept_edit_data = self.has_edit_button
            if not self.has_new_button:
                self.hide_new_button()
            if not self.has_edit_button:
                self.hide_edit_button()
        self._selected = None
        self.update_widgets()

        self.set_edit_button_sensitive(False)
        self.results.connect('selection-changed', self._on_selection_changed)
        self._check_permissions()

    def _setup_slaves(self):
        self._toolbar = SearchEditorToolBar()
        self._toolbar.connect("edit", self._on_toolbar__edit)
        self._toolbar.connect("add", self._on_toolbar__new)
        self.attach_slave('extra_holder', self._toolbar)

    def _check_permissions(self):
        if not self.editor_class:
            return

        pm = PermissionManager.get_permission_manager()
        key = self.editor_class.model_type.__name__
        if not pm.can_create(key):
            self.hide_new_button()

        if not pm.can_edit(key):
            if pm.can_see_details(key):
                # Replace edit button with a details button. self._read_only
                # will activate visual_mode for the editor
                self._read_only = True
                self._toolbar.edit_button_label.set_text(_('Details'))
                self._toolbar.edit_button_image.set_from_stock('gtk-info', gtk.ICON_SIZE_BUTTON)
            else:
                self.hide_edit_button()

    # Public API

    @argcheck(bool)
    def set_edit_button_sensitive(self, value):
        """Control sensitivity of button edit"""
        self._toolbar.edit_button.set_sensitive(value)

    def set_edit_button_label(self, label, stock=None):
        """Edits label and icon of the edit button
        """
        self._toolbar.edit_button_label.set_label(label)
        if stock:
            self._toolbar.edit_button_image.set_from_stock(stock,
                                                           gtk.ICON_SIZE_BUTTON)

    def update_widgets(self, *args):
        self._toolbar.edit_button.set_sensitive(len(self.results))

    def hide_edit_button(self):
        self.accept_edit_data = False
        self._toolbar.edit_button.hide()

    def hide_new_button(self):
        self._toolbar.new_button.hide()

    def update_edited_item(self, model):
        """Update the edited item to its proper type and select it on the
        list results.
        This method must be overwritten on subclasses when editors don't
        return a valid instance or when returning more than one model.
        """
        if self._selected:
            selected = self._selected
            Store.of(selected).flush()
            self.results.update(selected)
        else:
            # user just added a new instance
            selected = self.get_searchlist_model(model)
            self.results.append(selected)
        self.results.select(selected)

    def run(self, obj=None):
        self._selected = obj
        if obj:
            obj = self.get_editor_model(obj)
        if obj and self.interface:
            obj = self.interface(obj)

        rv = self.run_editor(obj)
        if rv:
            self.search.refresh()
            self.enable_ok()

    def run_dialog(self, editor_class, parent, *args, **kwargs):
        return run_dialog(editor_class, parent, *args, **kwargs)

    def run_editor(self, obj):
        store = api.new_store()
        retval = self.run_dialog(self.editor_class, self, store,
                                 store.fetch(obj), visual_mode=self._read_only)
        if store.confirm(retval):
            # If the return value is an ORMObject, fetch it from
            # the right connection
            if isinstance(retval, ORMObject):
                retval = type(retval).get(retval.id, store=self.store)
        store.close()
        return retval

    def row_activate(self, obj):
        """See :class:`SearchDialog.row_activate`
        """
        if self.double_click_confirm:
            SearchDialog.row_activate(self, obj)
        elif self.accept_edit_data:
            self._edit(obj)

    def _edit(self, obj):
        if obj is None:
            if self.results.get_selection_mode() == gtk.SELECTION_MULTIPLE:
                obj = self.results.get_selected_rows()
                qty = len(obj)
                if qty != 1:
                    raise AssertionError(
                      "There should be only one item selected. Got %s items"
                      % qty)
            else:
                obj = self.results.get_selected()
                if not obj:
                    raise AssertionError(
                        "There should be at least one item selected")

        self.run(obj)

    # Callbacks

    def _on_toolbar__edit(self, toolbar):
        self._edit(None)

    def _on_toolbar__new(self, toolbar):
        self.run()

    def _on_selection_changed(self, results, selected):
        can_edit = bool(selected)
        self.set_edit_button_sensitive(can_edit)

    #
    # Hooks
    #

    def get_searchlist_model(self, model):
        query = (getattr(self.search_table, self.model_list_lookup_attr) == model.id)
        return self.store.find(self.search_table, query).one()

    def get_editor_model(self, model):
        """This hook must be redefined on child when changing the type of
        the model is a requirement for edit method.
        """
        return model

#
# Date search options
#


class ThisWeek(DateSearchOption):
    name = _('This week')

    def get_interval(self):
        today = self.get_today_date()
        weekday = get_weekday_start()

        start = today + relativedelta(weekday=weekday(-1))
        end = start + relativedelta(days=+6)
        return start, end


class LastWeek(DateSearchOption):
    name = _('Last Week')

    def get_interval(self):
        today = self.get_today_date()
        weekday = get_weekday_start()

        start = today + relativedelta(weeks=-1, weekday=weekday(-1))
        end = start + relativedelta(days=+6)
        return start, end


class NextWeek(DateSearchOption):
    name = _('Next week')

    def get_interval(self):
        today = self.get_today_date()
        weekday = get_weekday_start()
        start = today + relativedelta(days=+1, weekday=weekday(+1))
        end = start + relativedelta(days=+6)
        return start, end


class ThisMonth(DateSearchOption):
    name = _('This month')

    def get_interval(self):
        today = self.get_today_date()
        start = today + relativedelta(day=1)
        end = today + relativedelta(day=31)
        return start, end


class LastMonth(DateSearchOption):
    name = _('Last month')

    def get_interval(self):
        today = self.get_today_date()
        start = today + relativedelta(months=-1, day=1)
        end = today + relativedelta(months=-1, day=31)
        return start, end


class NextMonth(DateSearchOption):
    name = _('Next month')

    def get_interval(self):
        today = self.get_today_date()
        start = today + relativedelta(months=+1, day=1)
        end = today + relativedelta(months=+1, day=31)
        return start, end

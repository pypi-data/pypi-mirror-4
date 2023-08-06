# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2006-2007 Async Open Source <http://www.async.com.br>
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
""" Abstract wizard and wizard steps definition

Note that a good aproach for all wizards steps defined here is do
not require some specific implementation details for the main wizard. Use
instead signals and interfaces for that.
"""

from decimal import Decimal
import sys

import gtk

from kiwi.currency import currency
from kiwi.datatypes import ValidationError
from kiwi.ui.widgets.list import SummaryLabel
from kiwi.ui.objectlist import SearchColumn, Column
from kiwi.python import Settable
from storm.expr import And

from stoqlib.api import api
from stoqlib.database.orm import ORMObject
from stoqlib.domain.sellable import Sellable
from stoqlib.domain.product import Product, ProductSupplierInfo
from stoqlib.domain.service import ServiceView
from stoqlib.domain.views import (ProductFullStockItemView,
                                  ProductComponentView, SellableFullStockView,
                                  ProductWithStockView)
from stoqlib.gui.base.search import SearchEditor
from stoqlib.gui.base.dialogs import run_dialog
from stoqlib.gui.base.lists import AdditionListSlave
from stoqlib.gui.base.wizards import WizardStep
from stoqlib.gui.editors.baseeditor import BaseEditorSlave
from stoqlib.gui.editors.producteditor import ProductEditor
from stoqlib.gui.events import WizardSellableItemStepEvent
from stoqlib.lib.defaults import sort_sellable_code
from stoqlib.lib.parameters import sysparam
from stoqlib.lib.translation import stoqlib_gettext


_ = stoqlib_gettext


# FIXME: Move this to stoqlib.gui.search.sellablesearch
class AdvancedSellableSearch(SearchEditor):

    title = _('Item search')
    size = (800, 450)
    has_new_button = True
    editor_class = ProductEditor

    def __init__(self, store, table, query=None, search_str=None,
                 supplier=None, hide_toolbar=False):
        """
        :param item_step: The item step this search is for.
        :param search_str: If this search should already filter for some string
        :param supplier: If provided and a new product is created from this
          search, then the created product will be associated with this
          supplier.
        :param hide_toolbar: if the search's toolbar, not allowing you
          to create/edit sellables
        """
        self._table = table
        self._query = query
        self._supplier = supplier

        SearchEditor.__init__(self, store, selection_mode=gtk.SELECTION_BROWSE,
                              hide_footer=False, table=self._table,
                              double_click_confirm=True,
                              hide_toolbar=hide_toolbar)
        if search_str:
            self.set_searchbar_search_string(search_str)
            self.search.refresh()

        self.set_ok_label(_('_Select item'))

    #
    # SearchDialog Hooks
    #

    def create_filters(self):
        self.set_text_field_columns(['description', 'barcode',
                                     'category_description', 'code'])
        self.executer.set_query(self.executer_query)

    def executer_query(self, store):
        results = store.find(self._table)
        if self._query:
            return results.find(self._query)
        return results

    def update_widgets(self):
        sellable_view = self.results.get_selected()
        self.ok_button.set_sensitive(bool(sellable_view))

    def get_columns(self):
        columns = [SearchColumn('code', title=_(u'Code'), data_type=str),
                   SearchColumn('barcode', title=_('Barcode'), data_type=str,
                                sort_func=sort_sellable_code, width=80),
                   SearchColumn('category_description', title=_('Category'),
                                data_type=str, width=120),
                   SearchColumn('description', title=_('Description'),
                                data_type=str, expand=True, sorted=True),
                   SearchColumn('manufacturer', title=_('Manufacturer'),
                                data_type=str, visible=False),
                   SearchColumn('model', title=_('Model'),
                                data_type=str, visible=False)]

        if hasattr(self._table, 'minimum_quantity'):
            columns.append(SearchColumn('minimum_quantity',
                                        title=_(u'Minimum Qty'),
                                        data_type=Decimal, visible=False))

        if hasattr(self._table, 'stock'):
            columns.append(Column('stock', title=_(u'In Stock'),
                                  data_type=Decimal))

        return columns

    #
    # SearchEditor Hooks
    #

    def get_editor_model(self, model):
        return model.product

    def run_editor(self, obj=None):
        store = api.new_store()
        product = self.run_dialog(self.editor_class, self, store,
                                 store.fetch(obj), visual_mode=self._read_only)

        # This means we are creating a new product. After that, add the
        # current supplier as the supplier for this product
        if (obj is None and product
            and not product.is_supplied_by(self._supplier)):
            ProductSupplierInfo(store=store,
                                supplier=store.fetch(self._supplier),
                                product=product,
                                base_cost=product.sellable.cost,
                                is_main_supplier=True)

        if store.confirm(product):
            # If the return value is an ORMObject, fetch it from
            # the right connection
            if isinstance(product, ORMObject):
                product = type(product).get(product.id, store=self.store)

            # If we created a new object, confirm the dialog automatically
            if obj is None:
                self.confirm(product)
                store.close()
                return
        store.close()

        return product

#
# Abstract Wizards for items
#


# FIXME: move this to stoqlib.gui.slaves.sellableslave
class SellableItemSlave(BaseEditorSlave):
    """A slave for selecting sellable items.

    It defines the following:

      - barcode entry
      - quantity spinbutton
      - cost entry
      - add button
      - find product button
      - sellable objectlist

    Optionally buttons to modify the list

      - Add
      - Remove
      - Edit

    Subclasses should define a sellable_view property and a
    get_sellable_view_query, both used to define what sellables can be added
    to the step.

    The view used should have the following properties:

     - barcode
     - description
     - category_description

    and should also provide an acessor that returns the sellable object.

    """
    gladefile = 'SellableItemSlave'
    proxy_widgets = ('quantity',
                     'unit_label',
                     'cost',
                     'minimum_quantity',
                     'stock_quantity',
                     'sellable_description', )
    summary_label_text = None
    summary_label_column = 'total'
    value_column = 'cost'
    sellable_view = ProductFullStockItemView
    sellable_editable = False
    validate_stock = False
    validate_value = False
    # FIXME: s/cost/value/
    cost_editable = True
    item_editor = None

    def __init__(self, store, model=None, visual_mode=None):
        super(SellableItemSlave, self).__init__(store, model=model,
                                                visual_mode=visual_mode)
        self._setup_widgets()

    #
    #  BaseEditorSlave
    #

    def setup_proxies(self):
        self.proxy = self.add_proxy(None, self.proxy_widgets)

    def setup_slaves(self):
        self.slave = AdditionListSlave(
            self.store, self.get_columns(),
            editor_class=self.item_editor,
            klist_objects=self.get_saved_items(),
            restore_name=self.__class__.__name__,
            visual_mode=self.visual_mode)
        self.slave.connect('before-delete-items',
                           self._on_list_slave__before_delete_items)
        self.slave.connect('after-delete-items',
                           self._on_list_slave__after_delete_items)
        self.slave.connect('on-edit-item', self._on_list_slave__edit_item)
        self.slave.connect('on-add-item', self._on_list_slave__add_item)
        self.attach_slave('list_holder', self.slave)

    def update_visual_mode(self):
        for widget in [self.barcode, self.product_button]:
            widget.set_sensitive(False)

    #
    # Public API
    #

    def add_sellable(self, sellable):
        """Add a sellable to the current step

        This will call step.get_order_item to create the correct item for the
        current model, and this created item will be returned.
        """
        quantity = self.get_quantity()
        cost = self.cost.read()
        item = self.get_order_item(sellable, cost, quantity)
        if item is None:
            return

        if item in self.slave.klist:
            self.slave.klist.update(item)
        else:
            self.slave.klist.append(item)

        self._update_total()
        self._reset_sellable()
        return item

    def remove_items(self, items):
        """Remove items from the current :class:`IContainer`.

        Subclasses can override this if special logic is necessary.
        """
        for item in items:
            self.model.remove_item(item)

    def hide_item_addition_toolbar(self):
        self.item_table.hide()

    def hide_add_button(self):
        """Hides the add button
        """
        self.slave.hide_add_button()

    def hide_del_button(self):
        """Hides the del button
        """
        self.slave.hide_del_button()

    def hide_edit_button(self):
        """Hides the edit button
        """
        self.slave.hide_edit_button()

    def get_quantity(self):
        """Returns the quantity of the current model or 1 if there is no model
        :returns: the quantity
        """
        return self.proxy.model and self.proxy.model.quantity or Decimal(1)

    def get_model_item_by_sellable(self, sellable):
        """Returns a model instance by the given sellable.
        :returns: a model instance or None if we could not find the model.
        """
        for item in self.slave.klist:
            if item.sellable == sellable:
                return item

    def get_parent(self):
        return self.get_toplevel().get_toplevel()

    def validate(self, value):
        self.add_sellable_button.set_sensitive(value
                                               and bool(self.proxy.model)
                                               and bool(self.proxy.model.sellable))

    #
    # Hooks
    #

    def get_sellable_view_query(self):
        """This method should return a tuple containing the viewable that should
        be used and a query that should filter the sellables that can and cannot
        be added to this step.
        """
        return (self.sellable_view,
                Sellable.get_unblocked_sellables_query(self.store))

    def get_order_item(self, sellable, value, quantity):
        """Adds the sellable to the current model

        This method is called when the user added the sellable in the wizard
        step. Subclasses should implement this method to add the sellable to the
        current model.
        """
        raise NotImplementedError('This method must be defined on child')

    def get_saved_items(self):
        raise NotImplementedError('This method must be defined on child')

    def get_columns(self):
        raise NotImplementedError('This method must be defined on child')

    def can_add_sellable(self, sellable):
        """Whether we can add a sellable to the list or not

        This is a hook method that gets called when trying to add a
        sellable to the list. It can be rewritten on child classes for
        extra functionality
        :param sellable: the selected sellable
        :returns: True or False (True by default)
        """
        return True

    def sellable_selected(self, sellable):
        """This will be called when a sellable is selected in the combo.
        It can be overriden in a subclass if they wish to do additional
        logic at that point
        :param sellable: the selected sellable
        """
        has_storable = False
        minimum = Decimal(0)
        stock = Decimal(0)
        cost = currency(0)
        quantity = Decimal(0)
        description = u''
        unit_label = u''

        if sellable:
            description = "<b>%s</b>" % api.escape(sellable.get_description())
            cost = getattr(sellable, self.value_column)
            quantity = Decimal(1)
            storable = sellable.product_storable
            unit_label = sellable.get_unit_description()
            if storable:
                has_storable = True
                minimum = storable.minimum_quantity
                stock = storable.get_balance_for_branch(self.model.branch)
        else:
            self.barcode.set_text('')

        model = Settable(quantity=quantity,
                         cost=cost,
                         sellable=sellable,
                         minimum_quantity=minimum,
                         stock_quantity=stock,
                         sellable_description=description,
                         unit_label=unit_label)

        self.proxy.set_model(model)

        has_sellable = bool(sellable)
        self.add_sellable_button.set_sensitive(has_sellable)
        self.force_validation()
        self.quantity.set_sensitive(has_sellable)
        self.cost.set_sensitive(has_sellable and self.cost_editable)
        self._update_product_labels_visibility(has_storable)

    #
    #  Private
    #

    def _setup_widgets(self):
        self._update_product_labels_visibility(False)
        self.quantity.set_sensitive(False)
        self.cost.set_sensitive(False)
        self.add_sellable_button.set_sensitive(False)
        self.unit_label.set_bold(True)

        for widget in [self.quantity, self.cost]:
            widget.set_adjustment(gtk.Adjustment(lower=0, upper=sys.maxint,
                                                 step_incr=1))

        self._reset_sellable()
        self._setup_summary()
        self.cost.set_digits(sysparam(self.store).COST_PRECISION_DIGITS)
        self.quantity.set_digits(3)

        self.barcode.grab_focus()
        self.item_table.set_focus_chain([self.barcode,
                                         self.quantity, self.cost,
                                         self.add_sellable_button,
                                         self.product_button])
        self.register_validate_function(self.validate)

    def _setup_summary(self):
        # FIXME: Move this into AdditionListSlave
        if not self.summary_label_column:
            self.summary = None
            return
        self.summary = SummaryLabel(klist=self.slave.klist,
                                    column=self.summary_label_column,
                                    label=self.summary_label_text,
                                    value_format='<b>%s</b>')
        self.summary.show()
        self.slave.list_vbox.pack_start(self.summary, expand=False)

    def _run_advanced_search(self, search_str=None):
        supplier = None
        has_supplier = hasattr(self.model, 'supplier')
        if has_supplier:
            supplier = self.model.supplier

        table, query = self.get_sellable_view_query()
        ret = run_dialog(AdvancedSellableSearch, self.get_parent(),
                         self.store,
                         table=table,
                         query=query,
                         search_str=search_str,
                         supplier=supplier,
                         hide_toolbar=not self.sellable_editable)
        if not ret:
            return

        # We receive different items depend on if we
        # - selected an item in the search
        # - created a new item and it closed the dialog for us
        if not isinstance(ret, (Product, ProductFullStockItemView,
                                ProductComponentView, SellableFullStockView,
                                ServiceView, ProductWithStockView)):
            raise AssertionError(ret)

        sellable = ret.sellable
        if not self.can_add_sellable(sellable):
            return
        self.barcode.set_text(sellable.barcode)
        self.sellable_selected(sellable)
        self.quantity.grab_focus()

    def _get_sellable(self):
        """This method always read the barcode and searches de database.

        If you only need the current selected sellable, use
        self.proxy.model.sellable
        """
        barcode = self.barcode.get_text()
        if not barcode:
            return None
        barcode = unicode(barcode, 'utf-8')

        viewable, default_query = self.get_sellable_view_query()
        query = viewable.barcode == barcode

        if default_query:
            query = And(query, default_query)

        # FIXME: doing list() here is wrong. But there is a bug in one of
        # the queries, that len() == 1 but results.count() == 2.
        results = list(self.store.find(viewable, query))

        if len(results) != 1:
            return None

        sellable = results[0].sellable
        if not sellable:
            return None
        elif not self.can_add_sellable(sellable):
            return

        return sellable

    def _add_sellable(self):
        sellable = self.proxy.model.sellable
        assert sellable

        sellable = self.store.fetch(sellable)

        self.add_sellable(sellable)
        self.proxy.set_model(None)
        self.sellable_selected(None)
        self.barcode.grab_focus()

    def _reset_sellable(self):
        self.proxy.set_model(None)
        self.barcode.set_text('')

    def _update_total(self):
        if self.summary:
            self.summary.update_total()
        self.force_validation()

    def _update_product_labels_visibility(self, visible):
        for widget in [self.minimum_quantity_lbl, self.minimum_quantity,
                       self.stock_quantity, self.stock_quantity_lbl]:
            widget.set_visible(visible)

    #
    #  Callbacks
    #

    def _on_list_slave__before_delete_items(self, slave, items):
        self.remove_items(items)
        self.force_validation()

    def _on_list_slave__after_delete_items(self, slave):
        self._update_total()

    def _on_list_slave__add_item(self, slave, item):
        self._update_total()

    def _on_list_slave__edit_item(self, slave, item):
        self._update_total()

    def on_add_sellable_button__clicked(self, button):
        self._add_sellable()

    def on_product_button__clicked(self, button):
        self._run_advanced_search()

    def on_barcode__activate(self, widget):
        sellable = self._get_sellable()

        if not sellable:
            search_str = unicode(self.barcode.get_text())
            self._run_advanced_search(search_str)
            return

        self.sellable_selected(sellable)
        self.quantity.grab_focus()

    def on_quantity__activate(self, entry):
        if self.add_sellable_button.get_sensitive():
            self._add_sellable()

    def on_cost__activate(self, entry):
        if self.add_sellable_button.get_sensitive():
            self._add_sellable()

    def on_quantity__validate(self, entry, value):
        if not self.proxy.model.sellable:
            return

        # only support positive quantities
        if value <= 0:
            return ValidationError(_(u'The quantity must be positive'))

        sellable = self.proxy.model.sellable
        if sellable and not sellable.is_valid_quantity(value):
            return ValidationError(_(u"This product unit (%s) does not "
                                     u"support fractions.") %
                                     sellable.get_unit_description())

        storable = sellable.product_storable
        if (self.validate_stock and storable and
                value > storable.get_balance_for_branch(self.model.branch)):
            return ValidationError(_("This quantity is not available in stock"))

    def on_cost__validate(self, widget, value):
        sellable = self.proxy.model.sellable
        if not sellable:
            return

        if value <= 0:
            return ValidationError(_(u'Cost must be greater than zero.'))

        if self.validate_value:
            client = getattr(self.model, 'client', None)
            if not sellable.is_valid_price(value, client.category):
                return ValidationError(_(u"Max discount for this product "
                                         u"is %.2f%%") % sellable.max_discount)


# FIXME: Instead of doing multiple inheritance, attach
# SellableItemSlave. This will need a lot of refactoring
class SellableItemStep(SellableItemSlave, WizardStep):
    model_type = None

    def __init__(self, wizard, previous, store, model):
        self.wizard = wizard
        WizardStep.__init__(self, previous)
        SellableItemSlave.__init__(self, store, model=model)
        WizardSellableItemStepEvent.emit(self)

    def get_parent(self):
        return self.wizard

    def post_init(self):
        self.barcode.grab_focus()
        self.force_validation()

    def validate(self, value):
        SellableItemSlave.validate(self, value)
        self.wizard.refresh_next(value and bool(len(self.slave.klist)))

    def validate_step(self):
        # FIXME: This should NOT be done here.
        #        Find another way of saving the columns when exiting this
        #        step, without having to depend on next_step, that should
        #        raise NotImplementedError.
        self.slave.save_columns()
        return True

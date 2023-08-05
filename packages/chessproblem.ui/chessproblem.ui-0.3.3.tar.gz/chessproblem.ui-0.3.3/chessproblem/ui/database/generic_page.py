# Copyright 2012 Stefan Hoening
# 
# This file is part of the "Chess-Problem-Editor" software.
# 
# Chess-Problem-Editor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Chess-Problem-Editor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
# Diese Datei ist Teil der Software "Chess-Problem-Editor".
# 
# Chess-Problem-Editor ist Freie Software: Sie koennen es unter den Bedingungen
# der GNU General Public License, wie von der Free Software Foundation,
# Version 3 der Lizenz oder (nach Ihrer Option) jeder spaeteren
# veroeffentlichten Version, weiterverbreiten und/oder modifizieren.
# 
# Chess-Problem-Editor wird in der Hoffnung, dass es nuetzlich sein wird, aber
# OHNE JEDE GEWAEHRLEISTUNG, bereitgestellt; sogar ohne die implizite
# Gewaehrleistung der MARKTFAEHIGKEIT oder EIGNUNG FUER EINEN BESTIMMTEN ZWECK.
# Siehe die GNU General Public License fuer weitere Details.
# 
# Sie sollten eine Kopie der GNU General Public License zusammen mit diesem
# Programm erhalten haben. Wenn nicht, siehe <http://www.gnu.org/licenses/>.

'''
'''

import pygtk
pygtk.require("2.0")
import gtk, gtk.gdk, gobject

import chessproblem.ui.gtk_search as search

MODE_DISPLAY_EMPTY = 0
MODE_DISPLAY_OBJECT = 1
MODE_EDIT_NEW = 2
MODE_EDIT_OBJECT = 3

class InvalidModeException(Exception):
    def __init__(self):
        Exception.__init__(self)

class FormButtonBox(gtk.HBox):
    '''
    The standard buttons for an edit form beside a selectable listbox.
    There are buttons for:
    -   delete
    -   edit
    -   save
    -   new
    -   cancel
    When when clicking the buttons the button activation is changed and
    the appropriate "on_button_xxx" method is called on the target 
    given in constructor.
    '''
    def __init__(self, target):
        gtk.HBox.__init__(self, False, 0)
        self.target = target
        self.button_delete = gtk.Button('delete')
        self.button_delete.connect('clicked', target.on_button_delete)
        self.button_delete.set_sensitive(False)
        self.button_delete.show()
        self.pack_start(self.button_delete, padding=10)
        self.button_edit = gtk.Button('edit')
        self.button_edit.connect('clicked', target.on_button_edit)
        self.button_edit.set_sensitive(False)
        self.button_edit.show()
        self.pack_start(self.button_edit, padding=10)
        self.button_save = gtk.Button('save')
        self.button_save.connect('clicked', target.on_button_save)
        self.button_save.set_sensitive(False)
        self.button_save.show()
        self.pack_start(self.button_save, padding=10)
        self.button_new = gtk.Button('new')
        self.button_new.connect('clicked', target.on_button_new)
        self.button_new.show()
        self.pack_start(self.button_new, padding=10)
        self.button_cancel = gtk.Button('cancel')
        self.button_cancel.connect('clicked', target.on_button_cancel)
        self.button_cancel.set_sensitive(False)
        self.button_cancel.show()
        self.pack_start(self.button_cancel, padding=10)

    def edit_mode(self):
        self.button_delete.set_sensitive(False)
        self.button_edit.set_sensitive(False)
        self.button_save.set_sensitive(True)
        self.button_new.set_sensitive(False)
        self.button_cancel.set_sensitive(True)

    def display_object_mode(self):
        self.button_delete.set_sensitive(True)
        self.button_edit.set_sensitive(True)
        self.button_save.set_sensitive(False)
        self.button_new.set_sensitive(True)
        self.button_cancel.set_sensitive(False)

    def display_empty_mode(self):
        self.button_delete.set_sensitive(False)
        self.button_edit.set_sensitive(False)
        self.button_save.set_sensitive(False)
        self.button_new.set_sensitive(True)
        self.button_cancel.set_sensitive(False)


class AbstractDataPage(gtk.VBox):
    '''
    This class implements an abstract base page for all base data pages.
    The page contains a SearchPanel on the left side, an edit form on the right side
    with a button box below.
    This class implements the generic event handling for events of the search panel and the button box.
    The given 'edit_form' should implement:
    -   clear_display()
    -   display_object(selected_object)
    -   enable_edit()
    -   get_edit_object()
    The given 'search_data_provider' should implement:
    -   create_liststore() (method called by SearchListBox)
    -   column_headings() (method called by SearchListBox)
    -   filtered objects() (method called by SearchListBox)
    -   create_liststore_data (method called by SearchListBox)
    '''
    def __init__(self, db_service, edit_form, search_data_provider):
        gtk.VBox.__init__(self, False, 0)
        self.hbox = gtk.HBox(False, 0)
        self.hbox.show()
        self.pack_start(self.hbox)
        self.db_service = db_service
        self.edit_form = edit_form
        self.search_panel = search.SearchPanel(search_data_provider, self.object_selected)
        self.search_panel.add_filter_listener(self._on_filter_changed)
        self.search_panel.show()
        self.hbox.pack_start(self.search_panel)
        self.edit_box = gtk.VBox(False, 0)
        self.edit_box.show()
        self.hbox.pack_start(self.edit_box, padding=10)
        self.edit_form.show()
        self.edit_box.pack_start(self.edit_form, False, False, 10)
        self.button_box = FormButtonBox(self)
        self.button_box.show()
        self.edit_box.pack_start(self.button_box, False, False, 10)
        self.mode = MODE_DISPLAY_EMPTY
        self.selected_object = None
        self.status_box = gtk.HBox()
        self.status_box.show()
        self.pack_end(self.status_box, False, False, 0)
        self.status_bar = gtk.Statusbar()
        # self.status_bar.set_has_resize_grip(False)
        self.status_bar.show()
        self.status_box.pack_start(self.status_bar, True, True, 0)
        self.status_context_id = self.status_bar.get_context_id('context_id')
        self.status_message_id = self.status_bar.push(self.status_context_id, 'Statusbar')
        self._on_filter_changed()

    def _on_filter_changed(self):
        '''
        This method is registered to be called, when the filter within the search_panel changes.
        It is used to change the status message to display the appropriate count of filtered objects.
        '''
        self.status_bar.pop(self.status_context_id)
        self.status_bar.push(self.status_context_id, self.search_panel.status_message())

    def object_selected(self, selected_object):
        self.selected_object = selected_object
        if (self.mode == MODE_DISPLAY_EMPTY) or (self.mode == MODE_DISPLAY_OBJECT):
            if selected_object == None:
                self.edit_form.clear_display()
                self.button_box.display_empty_mode()
                self.mode = MODE_DISPLAY_EMPTY
            else:
                self.edit_form.display_object(selected_object)
                self.button_box.display_object_mode()
                self.mode = MODE_DISPLAY_OBJECT
        else:
            raise InvalidModeException()

    def on_button_delete(self, widget, data=None):
        if self.mode == MODE_DISPLAY_OBJECT:
            if self.selected_object != None:
                self.db_service.delete(self.selected_object)
                self.search_panel.run_filter()
        else:
            raise InvalidModeException()


    def on_button_edit(self, widget, data=None):
        if self.mode == MODE_DISPLAY_OBJECT:
            self.mode = MODE_EDIT_OBJECT
            self.search_panel.enable_panel(False)
            self.edit_form.enable_edit()
            self.button_box.edit_mode()
        else:
            raise InvalidModeException()

    def on_button_save(self, widget, data=None):
        if self.mode == MODE_EDIT_OBJECT:
            edit_object = self.edit_form.get_edit_object()
            self.db_service.store_object(edit_object)
            self.search_panel.selection_updated()
            self.search_panel.enable_panel(True)
            self.edit_form.enable_edit(False)
            self.button_box.display_object_mode()
            self.mode = MODE_DISPLAY_OBJECT
        elif self.mode == MODE_EDIT_NEW:
            edit_object = self.edit_form.get_edit_object()
            self.db_service.store_object(edit_object)
            self.search_panel.enable_panel(True)
            self.edit_form.enable_edit(False)
            if (self.selected_object == None):
                self.button_box.display_empty_mode()
                self.mode = MODE_DISPLAY_EMPTY
            else:
                self.button_box.display_object_mode()
                self.mode = MODE_DISPLAY_OBJECT
        else:
            raise InvalidModeException()

    def on_button_new(self, widget, data=None):
        if (self.mode == MODE_DISPLAY_EMPTY) or (self.mode == MODE_DISPLAY_OBJECT):
            self.mode = MODE_EDIT_NEW
            self.edit_form.clear_display()
            self.search_panel.enable_panel(False)
            self.edit_form.enable_edit()
            self.button_box.edit_mode()
        else:
            raise InvalidModeException()

    def on_button_cancel(self, widget, data=None):
        if (self.mode == MODE_EDIT_OBJECT) or ((self.mode == MODE_EDIT_NEW) and (self.selected_object != None)):
            self.mode = MODE_DISPLAY_OBJECT
            self.search_panel.enable_panel(True)
            self.edit_form.display_object(self.selected_object)
            self.edit_form.enable_edit(False)
            self.button_box.display_object_mode()
        elif self.mode == MODE_EDIT_NEW:
            self.mode = MODE_DISPLAY_EMPTY
            self.search_panel.enable_panel(True)
            self.edit_form.clear_display()
            self.edit_form.enable_edit(False)
            self.button_box.display_empty_mode()
        else:
            raise InvalidModeException()


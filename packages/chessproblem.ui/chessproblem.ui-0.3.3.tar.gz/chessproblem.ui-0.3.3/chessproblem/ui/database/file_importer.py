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
This package contains classes and methods used to import data from LaTeX files into
the database holding the chessproblem basedata.
'''

import pygtk
pygtk.require("2.0")
import gtk, gtk.gdk, gobject

from chessproblem.model import Chessproblem

from chessproblem.io import ChessProblemLatexParser

from chessproblem.ui.gtk_search import SearchPanel

from chessproblem.ui.search_descriptors import CountrySearchDataProvider, CitySearchDataProvider, AuthorSearchDataProvider

import logging

LOGGER = logging.getLogger('chessproblem.ui.database.file_importer')

# Notes:
# I should be able to iterate through the list of authors while being able to change not only references to cities and countries but also exchaning authors.
# To be fast I should try to set the focus to the most appropriate element, this means:
#   -   when the entry was found inside the database, the button 'use from db' should have the focus
#   -   when the entry was not found, the focus should be inside the first entry of the acual section
#   -   if everything is found I should have some means to "skip"
#   -   to make this visible the focus button should be highlighted
#   -   I should set a more than light-grey background for my info-fields.

class AuthorIterator(object):
    '''
    Allows to iterate over all authors within a list of chessproblems.
    '''
    def __init__(self, document):
        self.document = document
        self.author_indices = []
        for problem_index in range(self.document.get_problem_count()):
            problem = self.document.get_problem(problem_index)
            for author_index in range(len(problem.authors)):
                self.author_indices.append((problem_index, author_index))
        self.author_index = -1

    def next_author(self):
        '''
        Return the next author.
        If there is no more author to iterate over, a StopIteration exception is raised.
        '''
        self.author_index += 1
        if self.author_index < len(self.author_indices):
            (problem_index, author_index) = self.author_indices[self.author_index]
            LOGGER.debug('returning author from problem ' + str(problem_index) + ' with author index ' + str(author_index))
            problem = self.document.get_problem(problem_index)
            author = problem.authors[author_index]
            return author
        else:
            raise StopIteration

    def save_author(self, author):
        (problem_index, author_index) = self.author_indices[self.author_index]
        problem = self.document.get_problem(problem_index)
        problem.authors[author_index] = author

def _create_and_attach_label(label, to_table, x, y, width=1):
    result = gtk.Label(label)
    result.show()
    _attach_to_table(to_table, result, x, y, width)
    return result

def _create_and_attach_entry(to_table, x, y, sensitive=True, width=1):
    result = gtk.Entry()
    result.set_sensitive(sensitive)
    result.show()
    _attach_to_table(to_table, result, x, y, width)
    return result

def _create_and_attach_button(label, to_table, x, y, clicked_handler):
    result = gtk.Button(label)
    result.show()
    result.connect('clicked', clicked_handler)
    _attach_to_table(to_table, result, x, y)
    return result

def _attach_to_table(to_table, widget, x, y, width=1):
    to_table.attach(widget, x, x+width, y, y+1, yoptions=0, xpadding=5, ypadding=5)


def import_all_from_tex(db_service, filename):
    '''
    Reads problems from the file with the given filename and starts opens the dialog to
    import authors, cities and countries from chessproblems found in this file.
    '''
    if filename != None:
        with open(filename, 'r') as f:
            s = f.read()
        parser = ChessProblemLatexParser()
        document = parser.parse_latex_str(s)
        dialog = ImportAllFromTexDialog(db_service, document)
        response = dialog.run()
        dialog.destroy()
        if response == gtk.RESPONSE_ACCEPT:
            LOGGER.info('import_all_from_tex - rewriting latex file: ' + filename)
            with open(filename, 'w') as f:
                write_latex(chessproblems, f)


class ImportAllFromTexDialog(gtk.Dialog):
    def __init__(self, db_service, document):
        self.db_service = db_service
        self.document = document
        self.author_iterator = AuthorIterator(self.document)
        self.file_author = None
        self.file_city = None
        self.file_country = None
        self.db_author = None
        self.db_city = None
        self.db_country = None
        self.selected_author = None
        self.selected_city = None
        self.selected_country = None
        gtk.Dialog.__init__(self, title='Import all from TeX', flags=gtk.DIALOG_MODAL,
                buttons=(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        # self.set_response_sensitive(gtk.RESPONSE_ACCEPT, False)
        # ----- country section -----
        # self.get_content_area().pack_start(self.country_frame, True, True)
        self.current_values_frame = gtk.Frame('current values from file')
        self.current_values_frame.set_visible(True)
        self.get_content_area().pack_start(self.current_values_frame, True, True)
        self.current_values_area = gtk.Table(2, 3)
        self.current_values_area.show()
        self.current_values_frame.add(self.current_values_area)
        self.current_lastname_label = _create_and_attach_label('lastname', self.current_values_area, 0, 0)
        self.current_firstname_label = _create_and_attach_label('firstname', self.current_values_area, 1, 0)
        self.current_city_label = _create_and_attach_label('city', self.current_values_area, 2, 0)
        self.current_country_label = _create_and_attach_label('country', self.current_values_area, 3, 0)
        self.current_lastname_entry = _create_and_attach_entry(self.current_values_area, 0, 1, sensitive=False)
        self.current_firstname_entry = _create_and_attach_entry(self.current_values_area, 1, 1, sensitive=False)
        self.current_city_entry = _create_and_attach_entry(self.current_values_area, 2, 1, sensitive=False)
        self.current_country_entry = _create_and_attach_entry(self.current_values_area, 3, 1, sensitive=False)
        self.current_country_entry.set_width_chars(5)
        # ----- Add an area handle the country -----
        self.country_frame = gtk.Frame('handle country')
        self.country_frame.show()
        self.get_content_area().pack_start(self.country_frame, True, True)
        self.country_area = gtk.HBox()
        self.country_area.show()
        self.country_frame.add(self.country_area)
        self.country_form = gtk.Table(4, 3)
        self.country_form.show()
        self.country_area.pack_start(self.country_form, True, True)
        self.label_country_file = _create_and_attach_label('from file', self.country_form, 0, 0)
        self.entry_country_file = _create_and_attach_entry(self.country_form, 1, 0)
        self.button_country_file = _create_and_attach_button('use from file', self.country_form, 2, 0, self.on_button_country_file)
        self.label_country_db = _create_and_attach_label('from db', self.country_form, 0, 1)
        self.entry_country_db = _create_and_attach_entry(self.country_form, 1, 1, sensitive=False)
        self.button_country_db = _create_and_attach_button('use from db', self.country_form, 2, 1, self.on_button_country_db)
        self.entry_country_info = _create_and_attach_entry(self.country_form, 0, 2, width=2, sensitive=False)
        self.button_country_selected = _create_and_attach_button('use selected', self.country_form, 2, 2, self.on_button_country_selected)
        self.button_country_selected.set_sensitive(False)
        self.country_search_panel = SearchPanel(CountrySearchDataProvider(db_service), self._on_country_selected)
        self.country_search_panel.show()
        self.country_area.pack_start(self.country_search_panel, True, True)
        # ----- Add an area handle the city -----
        self.city_frame = gtk.Frame('handle city')
        self.city_frame.show()
        self.get_content_area().pack_start(self.city_frame, True, True)
        self.city_area = gtk.HBox()
        self.city_area.show()
        self.city_frame.add(self.city_area)
        self.city_form = gtk.Table(4, 3)
        self.city_form.show()
        self.city_area.pack_start(self.city_form, True, True)
        self.label_city_file = _create_and_attach_label('from file', self.city_form, 0, 0)
        self.entry_city_file = _create_and_attach_entry(self.city_form, 1, 0)
        self.button_city_file = _create_and_attach_button('use from file', self.city_form, 2, 0, self.on_button_city_file)
        self.label_city_db = _create_and_attach_label('from db', self.city_form, 0, 1)
        self.entry_city_db = _create_and_attach_entry(self.city_form, 1, 1, sensitive=False)
        self.button_city_db = _create_and_attach_button('use from db', self.city_form, 2, 1, self.on_button_city_db)
        self.entry_city_info = _create_and_attach_entry(self.city_form, 0, 2, width=2, sensitive=False)
        self.button_city_selected = _create_and_attach_button('use selected', self.city_form, 2, 2, self.on_button_city_selected)
        self.button_city_selected.set_sensitive(False)
        self.city_search_panel = SearchPanel(CitySearchDataProvider(db_service), self._on_city_selected)
        self.city_search_panel.show()
        self.city_area.pack_start(self.city_search_panel, True, True)
        # ----- Add an area handle the author -----
        self.author_frame = gtk.Frame('handle author')
        self.author_frame.show()
        self.get_content_area().pack_start(self.author_frame, True, True)
        self.author_area = gtk.HBox()
        self.author_area.show()
        self.author_frame.add(self.author_area)
        self.author_form = gtk.Table(4, 3)
        self.author_form.show()
        self.author_area.pack_start(self.author_form, True, True)
        self.label_author_file = _create_and_attach_label('from file', self.author_form, 0, 1)
        self.entry_author_lastname_file = _create_and_attach_entry(self.author_form, 1, 1)
        self.entry_author_firstname_file = _create_and_attach_entry(self.author_form, 2, 1)
        self.button_author_file = _create_and_attach_button('use from file', self.author_form, 3, 1, self.on_button_author_file)
        self.label_author_db = _create_and_attach_label('from db', self.author_form, 0, 2)
        self.entry_author_lastname_db = _create_and_attach_entry(self.author_form, 1, 2, sensitive=False)
        self.entry_author_firstname_db = _create_and_attach_entry(self.author_form, 2, 2, sensitive=False)
        self.button_author_db = _create_and_attach_button('use from db', self.author_form, 3, 2, self.on_button_author_db)
        self.entry_author_info = _create_and_attach_entry(self.author_form, 1, 3, width=2, sensitive=False)
        self.button_author_selected = _create_and_attach_button('use selected', self.author_form, 3, 3, self.on_button_author_selected)
        self.button_author_selected.set_sensitive(False)
        self.author_search_panel = SearchPanel(AuthorSearchDataProvider(db_service), self._on_author_selected)
        self.author_search_panel.show()
        self.author_area.pack_start(self.author_search_panel, True, True)
        # ----- Add a box containing the action buttons -----
        self.button_box = gtk.HBox()
        self.button_box.show()
        self.get_content_area().pack_start(self.button_box, False, False)
        self.button_next_author = gtk.Button('next author')
        self.button_next_author.connect('clicked', self.on_button_next_author)
        self.button_next_author.show()
        self.button_box.pack_start(self.button_next_author)

        # ----- Now we can start to walk through the file -----
        self._next_author()

    def _on_country_selected(self, country):
        self.selected_country = country
        self.button_country_selected.set_sensitive(country != None)

    def _on_city_selected(self, city):
        self.selected_city = city
        self.button_city_selected.set_sensitive(city != None)

    def _on_author_selected(self, author):
        self.selected_author = author
        self.button_author_selected.set_sensitive(author != None)
        

    def on_button_next_author(self, widget, data=None):
        self._next_author()

    def on_button_country_file(self, widget, data=None):
        LOGGER.info('Storing countries not implemented')

    def on_button_country_db(self, widget, data=None):
        self.file_city.country = self.db_country
        self.current_country_entry.set_text(self.db_country.code())
        self.city_mode()

    def on_button_country_selected(self, widget, data=None):
        self.file_city.country = self.selected_country
        self.current_country_entry.set_text(self.selected_country.code())
        self.city_mode()

    def on_button_city_file(self, widget, data=None):
        if self.db_city != None:
            self.db_city.name = self.entry_city_file.get_text()
            self.db_city.country = self.file_city.country
        else:
            self.db_city = self.file_city
        self.db_service.store_city(self.db_city)
        self.on_button_city_db(widget, data)

    def on_button_city_db(self, widget, data=None):
        self.file_author.city = self.db_city
        self.current_city_entry.set_text(self.db_city.name)
        self.author_mode()

    def on_button_city_selected(self, widget, data=None):
        self.file_author.city = self.selected_city
        self.current_city_entry.set_text(self.selected_city.name)
        self.author_mode()

    def on_button_author_file(self, widget, data=None):
        if self.db_author != None:
            self.db_author.lastname = self.entry_author_lastname_file.get_text()
            self.db_author.firstname = self.entry_author_firstname_file.get_text()
            self.db_author.city = self.file_author.city
        else:
            self.db_author = self.file_author
        self.db_service.store_author(self.db_author)
        self.on_button_author_db(widget, data)

    def on_button_author_db(self, widget, data=None):
        self.author_iterator.save_author(self.db_author)
        self._next_author()

    def on_button_author_selected(self, widget, data=None):
        self.author_iterator.save_author(self.selected_author)
        self._next_author()

    def country_mode(self):
        self.author_frame.hide()
        self.city_frame.hide()
        self.country_frame.show()
        # Search for country in db
        self.db_country = self.db_service.find_country_by_code(self.file_country.car_code)
        # fill countries frame
        self.entry_country_file.set_text(self.file_country.car_code)
        if self.db_country != None:
            self.entry_country_db.set_text(str(self.db_country))
            if self.file_country.car_code == self.db_country.code():
                self.entry_country_info.set_text('country found')
                self.on_button_country_db(None, None)
            else:
                self.entry_country_info.set_text('country found - use preferred code ' + self.db_country.code())
            self.button_country_db.grab_focus()
        else:
            self.entry_country_db.set_text('')
            self.entry_country_info.set_text('country code not found')
            self.button_country_file.grab_focus()

    def city_mode(self):
        self.author_frame.hide()
        self.city_frame.show()
        self.country_frame.hide()
        # Search for country in db
        self.db_city = self.db_service.find_city_by_name_and_country(self.file_city.name, self.file_city.country)
        # fill cities frame
        self.entry_city_file.set_text(self.file_city.name)
        if self.db_city != None:
            self.entry_city_db.set_text(self.db_city.name)
            if self.file_city.name == self.db_city.name:
                self.entry_city_info.set_text('city found - exact match')
                self.on_button_city_db(None, None)
            else:
                self.entry_city_info.set_text('city found - written different')
            self.button_city_db.grab_focus()
        else:
            self.entry_city_db.set_text('')
            self.entry_city_info.set_text('city not found')
            self.button_city_file.grab_focus()

    def author_mode(self):
        self.author_frame.show()
        self.city_frame.hide()
        self.country_frame.hide()
        # search for author in db
        self.db_author = self.db_service.find_author_by_lastname_firstname(self.file_author.lastname, self.file_author.firstname)
        # fill authors frame
        self.entry_author_lastname_file.set_text(self.file_author.lastname)
        self.entry_author_firstname_file.set_text(self.file_author.firstname)
        if self.db_author != None:
            self.entry_author_lastname_db.set_text(self.db_author.lastname)
            self.entry_author_firstname_db.set_text(self.db_author.firstname)
            if (self.file_author.lastname == self.db_author.lastname) and (self.file_author.firstname == self.db_author.firstname):
                self.entry_author_info.set_text('author found - exact match')
                # On exact matches I want to have an automatic mode
                self.on_button_author_db(None, None)
            else:
                self.entry_author_info.set_text('author found - written different')
            self.button_author_db.grab_focus()
        else:
            self.entry_author_lastname_db.set_text('')
            self.entry_author_firstname_db.set_text('')
            self.entry_author_info.set_text('author not found')
            self.button_author_file.grab_focus()

    def _next_author(self):
        try:
            self.file_author = self.author_iterator.next_author()
            self.current_lastname_entry.set_text(self.file_author.lastname)
            self.current_firstname_entry.set_text(self.file_author.firstname)
            if self.file_author.city != None:
                self.file_city = self.file_author.city
                self.current_city_entry.set_text(self.file_city.name)
                if self.file_city.country != None:
                    self.file_country = self.file_city.country
                    self.current_country_entry.set_text(self.file_country.car_code)
                    self.country_mode()
                else:
                    self.file_country = None
                    self.current_country_entry.set_text('')
                    self.city_mode()
            else:
                self.file_city = None
                self.current_city_entry.set_text('')
                self.file_country = None
                self.current_country_entry.set_text('')
                self.author_mode()
        except StopIteration:
            self.author_frame.hide()



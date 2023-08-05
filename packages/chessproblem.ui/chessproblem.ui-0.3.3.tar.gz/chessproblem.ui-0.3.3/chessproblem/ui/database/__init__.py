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
This module contains the application to edit the author database data used inside the chess problem editor application.
'''

import sys
import pygtk
pygtk.require("2.0")
import gtk, gtk.gdk, gobject

import chessproblem.model as model
import chessproblem.model.db as db

import chessproblem.ui.gtk_search as search

from chessproblem.ui.search_descriptors import CountrySearchDataProvider, CitySearchDataProvider, AuthorSearchDataProvider, SourceSearchDataProvider

import logging

from chessproblem.config import DEFAULT_CONFIG
from chessproblem.io import ChessProblemLatexParser, write_latex

from generic_page import AbstractDataPage
from generic_page import FormButtonBox

from file_importer import import_all_from_tex

LOGGER = logging.getLogger('chessproblem.ui.database')

def _country_name(country):
    if country == None:
        return ''
    else:
        return country.name


class CitySearchDialog(search.AbstractSearchDialog):
    '''
    A dialog to search for cities.
    '''
    def __init__(self, db_service):
        search.AbstractSearchDialog.__init__(self, 'City search', CitySearchDataProvider(db_service), self.object_selected)
        self.result = None

    def object_selected(self, city):
        self.set_response_sensitive(gtk.RESPONSE_ACCEPT, city != None)
        self.result = city

class AuthorForm(gtk.Table):
    def __init__(self, db_service):
        self.db_service = db_service
        gtk.Table.__init__(self, 2, 3)
        self.label_lastname = gtk.Label('lastname')
        self.label_lastname.show()
        self.attach(self.label_lastname, 0, 1, 0, 1, yoptions=0, xpadding=5)
        self.label_firstname = gtk.Label('firstname')
        self.label_firstname.show()
        self.attach(self.label_firstname, 0, 1, 1, 2, yoptions=0, xpadding=5)
        self.button_city = gtk.Button('city')
        self.button_city.set_sensitive(False)
        self.button_city.connect('clicked', self._on_button_city)
        self.button_city.show()
        self.attach(self.button_city, 0, 1, 2, 3, yoptions=0, xpadding=5)
        self.entry_lastname = gtk.Entry()
        self.entry_lastname.set_sensitive(False)
        self.entry_lastname.show()
        self.attach(self.entry_lastname, 1, 2, 0, 1, yoptions=0, xpadding=5)
        self.entry_firstname = gtk.Entry()
        self.entry_firstname.set_sensitive(False)
        self.entry_firstname.show()
        self.attach(self.entry_firstname, 1, 2, 1, 2, yoptions=0, xpadding=5)
        self.entry_city = gtk.Entry()
        self.entry_city.set_sensitive(False)
        self.entry_city.show()
        self.attach(self.entry_city, 1, 2, 2, 3, yoptions=0, xpadding=5)
        self.author = None
        self.city = None

    def _on_button_city(self, widget, data=None):
        city_search_dialog = CitySearchDialog(self.db_service)
        response = city_search_dialog.run()
        city_search_dialog.destroy()
        if response == gtk.RESPONSE_ACCEPT:
            self.city = city_search_dialog.result
            self.entry_city.set_text(str(self.city))

    def display_object(self, author):
        self.author = author
        self.city = author.city
        self.entry_lastname.set_text(author.lastname)
        self.entry_firstname.set_text(author.firstname)
        self.entry_city.set_text(str(author.city))

    def clear_display(self):
        self.author = None
        self.city = None
        self.entry_lastname.set_text('')
        self.entry_firstname.set_text('')
        self.entry_city.set_text('')

    def enable_edit(self, mode=True):
        self.entry_lastname.set_sensitive(mode)
        self.entry_firstname.set_sensitive(mode)
        self.button_city.set_sensitive(mode)

    def get_edit_object(self):
        if self.author == None:
            result = model.Author()
        else:
            result = self.author
        result.lastname = self.entry_lastname.get_text()
        result.firstname = self.entry_firstname.get_text()
        result.city = self.city
        return result

class AuthorsPage(AbstractDataPage):
    def __init__(self, db_service):
        AbstractDataPage.__init__(self, db_service, AuthorForm(db_service), AuthorSearchDataProvider(db_service))

class CountrySearchDialog(search.AbstractSearchDialog):
    def __init__(self, db_service):
        search.AbstractSearchDialog.__init__(self, 'Country search', CountrySearchDataProvider(db_service), self.object_selected)
        self.result = None

    def object_selected(self, country):
        self.set_response_sensitive(gtk.RESPONSE_ACCEPT, country != None)
        self.result = country


class CityForm(gtk.Table):
    def __init__(self, db_service):
        gtk.Table.__init__(self, 2, 3)
        self.db_service = db_service
        self.city = None
        self.country = None
        self.label_name = gtk.Label('City')
        self.label_name.show()
        self.attach(self.label_name, 0, 1, 0, 1, yoptions=0, ypadding=5)
        self.entry_name = gtk.Entry()
        self.entry_name.show()
        self.attach(self.entry_name, 1, 2, 0, 1, yoptions=0, ypadding=5)
        self.button_country = gtk.Button('Country')
        self.button_country.connect('clicked', self._on_button_country)
        self.button_country.show()
        self.attach(self.button_country, 0, 1, 1, 2, yoptions=0, ypadding=5)
        self.entry_country = gtk.Entry()
        self.entry_country.set_property('editable', False)
        self.entry_country.set_sensitive(False)
        self.entry_country.show()
        self.attach(self.entry_country, 1, 2, 1, 2, yoptions=0, ypadding=5)
        self.enable_edit(False)

    def _on_button_country(self, widget, data=None):
        country_search_dialog = CountrySearchDialog(self.db_service)
        response = country_search_dialog.run()
        country_search_dialog.destroy()
        if response == gtk.RESPONSE_ACCEPT:
            self.country = country_search_dialog.result
            self.entry_country.set_text(_country_name(self.country))
        country_search_dialog.destroy()

    def display_object(self, city):
        self.city = city
        self.entry_name.set_text(city.name)
        self.country = city.country
        self.entry_country.set_text(_country_name(city.country))

    def clear_display(self):
        self.city = None
        self.entry_name.set_text('')
        self.country = None
        self.entry_country.set_text('')

    def enable_edit(self, mode=True):
        self.entry_name.set_sensitive(mode)
        self.button_country.set_sensitive(mode)

    def get_edit_object(self):
        if self.city == None:
            city_name = self.entry_name.get_text()
            city = model.City(city_name)
        else:
            city = self.city
            city.name = self.entry_name.get_text()
        city.country = self.country
        return city


class CitiesPage(AbstractDataPage):
    def __init__(self, db_service):
        AbstractDataPage.__init__(self, db_service, CityForm(db_service), CitySearchDataProvider(db_service))

class CountryForm(gtk.Table):
    def __init__(self, db_service):
        gtk.Table.__init__(self, 2, 3)
        self.db_service = db_service
        self.country = None
        self.label_name = self._create_label('name', 0)
        self.label_car_code = self._create_label('car_code', 1)
        self.label_iso_3166_2 = self._create_label('iso 3166 2', 2)
        self.label_iso_3166_3 = self._create_label('iso 3166 3', 3)
        self.label_iso_3166_3 = self._create_label('iso 3166 n', 4)
        self.entry_name = self._create_entry(0)
        self.entry_car_code = self._create_entry(1)
        self.entry_iso_3166_2 = self._create_entry(2)
        self.entry_iso_3166_3 = self._create_entry(3)
        self.entry_iso_3166_n = self._create_entry(4)
        self.enable_edit(False)

    def _create_label(self, label, row):
        result = gtk.Label(label)
        result.show()
        self.attach(result, 0, 1, row, row + 1, yoptions=0, ypadding=5, xpadding=5)
        return result

    def _create_entry(self, row):
        result = gtk.Entry()
        result.show()
        self.attach(result, 1, 2, row, row + 1, yoptions=0, ypadding=5, xpadding=5)
        return result

    def display_object(self, country):
        self.country = country
        self.entry_name.set_text(country.name)
        if country.car_code == None:
            self.entry_car_code.set_text('')
        else:
            self.entry_car_code.set_text(country.car_code)
        self.entry_iso_3166_2.set_text(country.iso_3166_2)
        self.entry_iso_3166_3.set_text(country.iso_3166_3)
        self.entry_iso_3166_n.set_text(country.iso_3166_n)

    def clear_display(self):
        self.country = None
        self.entry_name.set_text('')
        self.entry_car_code.set_text('')
        self.entry_iso_3166_2.set_text('')
        self.entry_iso_3166_3.set_text('')
        self.entry_iso_3166_n.set_text('')

    def enable_edit(self, mode=True):
        self.entry_name.set_sensitive(mode)
        self.entry_car_code.set_sensitive(mode)
        self.entry_iso_3166_2.set_sensitive(mode)
        self.entry_iso_3166_3.set_sensitive(mode)
        self.entry_iso_3166_n.set_sensitive(mode)

    def get_edit_object(self):
        car_code = self.entry_car_code.get_text()
        if car_code == '':
            car_code = None
        if self.country == None:
            country = model.Country(car_code)
        else:
            country = self.country
            country.car_code = car_code
        country.name = self.entry_name.get_text()
        country.iso_3166_2 = self.entry_iso_3166_2.get_text()
        country.iso_3166_3 = self.entry_iso_3166_3.get_text()
        country.iso_3166_n = self.entry_iso_3166_n.get_text()
        return country

class CountriesPage(AbstractDataPage):
    def __init__(self, db_service):
        AbstractDataPage.__init__(self, db_service, CountryForm(db_service), CountrySearchDataProvider(db_service))

class SourceForm(gtk.Table):
    def __init__(self, db_service):
        gtk.Table.__init__(self, 1, 2)
        self.db_service = db_service
        self.source = None
        self.label_name = gtk.Label('name')
        self.label_name.show()
        self.attach(self.label_name, 0, 1, 0, 1, yoptions=0, ypadding=5, xpadding=5)
        self.entry_name = gtk.Entry()
        self.entry_name.show()
        self.attach(self.entry_name, 1, 2, 0, 1, yoptions=0, ypadding=5, xpadding=5)
        self.enable_edit(False)

    def display_object(self, source):
        self.source = source
        self.entry_name.set_text(source.name)

    def clear_display(self):
        self.source = None
        self.entry_name.set_text('')

    def enable_edit(self, mode=True):
        self.entry_name.set_sensitive(mode)


    def get_edit_object(self):
        name = self.entry_name.get_text()
        if name == '':
            return None
        if self.source == None:
            source = model.Source(name)
        else:
            source = self.source
            source.name = name
        return source

class SourcesPage(AbstractDataPage):
    def __init__(self, db_service):
        AbstractDataPage.__init__(self, db_service, SourceForm(db_service), SourceSearchDataProvider(db_service))

class MainFrame(object):
    def __init__(self):
        '''
        Initializes the instance.
        '''
        self.db_service = db.DbService(DEFAULT_CONFIG.database_url)
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('ChessProblemEditor / Database')
        self.window.connect("delete_event", self._on_delete)
        self.window.connect("destroy", self._on_destroy)
        self.window_area = gtk.VBox(False, 0)
        self.window_area.set_size_request(640, 480)
        self.window_area.show()
        self.window.add(self.window_area)
        self._create_menu()
        self._create_main_area()
        self.window.show()

    def _create_menu(self):
        '''
        Creates our applications main menu.
        '''
        self.menu_bar = gtk.MenuBar()
        accel_group = gtk.AccelGroup()
        self.window.add_accel_group(accel_group)

        # Our file menu
        self.file_menu_item = gtk.MenuItem("File")
        self.file_menu_item.show()
        self.file_menu = gtk.Menu()
        self.file_menu_item.set_submenu(self.file_menu)
        # file menu items
        self.file_exit_item = self._add_menu_item_with_accelerator(
                self.file_menu, 'Exit', self.on_file_exit, accel_group, ord('Q'), gtk.gdk.CONTROL_MASK)
        self.menu_bar.append(self.file_menu_item)
        # Our import menu
        self.import_menu_item = gtk.MenuItem("Import")
        self.import_menu_item.show()
        self.import_menu = gtk.Menu()
        self.import_menu_item.set_submenu(self.import_menu)
        # file import items
        self.import_from_tex = self._add_menu_item(self.import_menu, 'from TeX Source', self._on_import_from_tex)
        # self.import_countries = self._add_menu_item(self.import_menu, 'Countries', self._on_import_countries)
        # self.import_cities = self._add_menu_item(self.import_menu, 'Cities', self._on_import_cities)
        # self.import_authors = self._add_menu_item(self.import_menu, 'Authors', self._on_import_authors)
        self.menu_bar.append(self.import_menu_item)
        self.menu_bar.show()
        self.window_area.pack_start(self.menu_bar, False, False, 0)
        # Our reindex menu
        self.reindex_menu_item = gtk.MenuItem("Reindex")
        self.reindex_menu_item.show()
        self.reindex_menu = gtk.Menu()
        self.reindex_menu_item.set_submenu(self.reindex_menu)
        # reindex menu entries
        self.reindex_cities = self._add_menu_item(self.reindex_menu, 'cities', self._on_reindex_cities)
        self.reindex_authors = self._add_menu_item(self.reindex_menu, 'authors', self._on_reindex_authors)
        self.menu_bar.append(self.reindex_menu_item)

    def _add_menu_item_with_accelerator(self, menu, label, handler, accel_group, accel_char, key_modifier=0):
        result = self._add_menu_item(menu, label, handler)
        result.add_accelerator('activate', accel_group, accel_char, key_modifier, gtk.ACCEL_VISIBLE)
        return result

    def _add_menu_item(self, menu, label, handler):
        result = gtk.MenuItem(label)
        result.show()
        result.connect('activate', handler, None)
        menu.append(result)
        return result

    def _create_main_area(self):
        self.database_notebook = gtk.Notebook()
        self.authors_page = AuthorsPage(self.db_service)
        self.authors_page.show()
        self.database_notebook.append_page(self.authors_page)
        self.database_notebook.set_tab_label_text(self.authors_page, 'Authors')
        self.cities_page = CitiesPage(self.db_service)
        self.cities_page.show()
        self.database_notebook.append_page(self.cities_page)
        self.database_notebook.set_tab_label_text(self.cities_page, 'Cities')
        self.countries_page = CountriesPage(self.db_service)
        self.countries_page.show()
        self.database_notebook.append_page(self.countries_page)
        self.database_notebook.set_tab_label_text(self.countries_page, 'Countries')
        self.sources_page = SourcesPage(self.db_service)
        self.sources_page.show()
        self.database_notebook.append_page(self.sources_page)
        self.database_notebook.set_tab_label_text(self.sources_page, 'Sources')
        self.database_notebook.show()
        self.window_area.pack_start(self.database_notebook, True, True, 0)


    def _open_file_dialog(self, title):
        dialog = gtk.FileChooserDialog(
                title=title, action=gtk.FILE_CHOOSER_ACTION_OPEN,
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        response = dialog.run()
        filename = dialog.get_filename()
        dialog.destroy()
        if response == gtk.RESPONSE_OK:
            return filename
        else:
            LOGGER.info('on_file_open: No files selected')
            return None

    def _on_import_from_tex(self, widget, event, data=None):
        filename = self._open_file_dialog('Open file for countries import')
        import_all_from_tex(self.db_service, filename)

    def _on_import_countries(self, widget, event, data=None):
        filename = self._open_file_dialog('Open file for countries import')
        if filename != None:
            with open(filename, 'r') as f:
                s = f.read()
            parser = ChessProblemLatexParser()
            document = parser.parse_latex_str(s)
            self.import_countries(document)

    def import_countries(self, document):
        filename = self._open_file_dialog('Open file for countries import')
        if filename != None:
            pass

    def _on_import_cities(self, widget, event, data=None):
        filename = self._open_file_dialog('Open file for cities import')
        if filename != None:
            pass

    def _on_import_authors(self, widget, event, data=None):
        filename = self._open_file_dialog('Open file for authors import')
        if filename != None:
            pass

    def _on_reindex_cities(self, widget, event, data=None):
        self.db_service.reindex_cities()

    def _on_reindex_authors(self, widget, event, data=None):
        self.db_service.reindex_authors()

    def _on_delete(self, widget, event, data=None):
        '''
        Called when the application should be closed.
        '''
        return False

    def _on_destroy(self, widget, data=None):
        '''
        Called when the destroy_event occurs.
        '''
        self.quit()

    def on_file_exit(self, widget, event, data=None):
        '''
        Event handler for menu entry File / Exit.
        '''
        self.quit()

    def quit(self):
        gtk.main_quit()
        sys.exit(0)

    def main(self):
        gtk.main()



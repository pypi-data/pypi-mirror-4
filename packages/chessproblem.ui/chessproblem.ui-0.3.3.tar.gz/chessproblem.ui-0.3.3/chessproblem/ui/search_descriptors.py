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
This module contains the concrete data_provider implementations for countries,
cities, authors, sources and conditions which are used inside the 'gtk_search' module.
'''

import pygtk
pygtk.require("2.0")
import gtk, gtk.gdk, gobject


def _country_name(country):
    if country == None:
        return ''
    else:
        return country.name


class CountrySearchDataProvider(object):
    '''
    Implements all required methods for a country search_data_provider.
    '''
    def __init__(self, db_service):
        self.db_service = db_service

    def create_liststore(self):
        return gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)

    def column_headings(self):
        return ['car sign', 'name', 'iso-3166-2', 'iso-3166-3']

    def filtered_objects(self, expr):
        return self.db_service.find_countries_by_search(expr)

    def create_liststore_data(self, country):
        return [country.car_code, country.name, country.iso_3166_2, country.iso_3166_3]

    def _all_countries_count(self):
        '''
        Returns the count of countries inside the database.
        '''
        return self.db_service.count_countries()

    def status_message(self, current_count):
        '''
        Creates a status message for the given number of countries.
        '''
        return '%d of %d countries' % (current_count, self._all_countries_count())

class CitySearchDataProvider(object):
    '''
    Implements all required methods for a city search_descriptor.
    '''
    def __init__(self, db_service):
        self.db_service = db_service

    def create_liststore(self):
        return gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)

    def column_headings(self):
        return ['name', 'country']

    def filtered_objects(self, expr):
        return self.db_service.find_cities_by_search(expr)

    def create_liststore_data(self, city):
        return [city.name, str(city.country)]

    def _all_cities_count(self):
        '''
        Returns the count of cities inside the database.
        '''
        return self.db_service.count_cities()

    def status_message(self, current_count):
        '''
        Creates a status message for the given number of cities.
        '''
        return '%d of %d cities' % (current_count, self._all_cities_count())

def _city_name(author):
    if author.city != None:
        return author.city.name
    else:
        return ''

def _country_name(author):
    if author.city != None and author.city.country != None:
        return str(author.city.country)
    else:
        return ''


class AuthorSearchDataProvider(object):
    '''
    Implements all required methods for a city search_descriptor.
    '''
    def __init__(self, db_service):
        self.db_service = db_service

    def create_liststore(self):
        return gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)

    def column_headings(self):
        return ['lastname', 'firstname', 'city', 'country']

    def filtered_objects(self, expr):
        return self.db_service.find_authors_by_search(expr)

    def create_liststore_data(self, author):
        return [author.lastname, author.firstname, _city_name(author), _country_name(author)]

    def _all_authors_count(self):
        '''
        Returns the count of authors inside the database.
        '''
        return self.db_service.count_authors()

    def status_message(self, current_count):
        '''
        Creates a status message for the given number of authors.
        '''
        return '%d of %d authors' % (current_count, self._all_authors_count())


class SourceSearchDataProvider(object):
    '''
    Implements all required methods for a city search_descriptor.
    '''
    def __init__(self, db_service):
        self.db_service = db_service

    def create_liststore(self):
        return gtk.ListStore(gobject.TYPE_STRING)

    def column_headings(self):
        return ['name']

    def filtered_objects(self, expr):
        return self.db_service.find_sources_by_search(expr)

    def create_liststore_data(self, source):
        return [source.name]

    def _all_sources_count(self):
        '''
        Returns the count of sources inside the database.
        '''
        return self.db_service.count_sources()

    def status_message(self, current_count):
        '''
        Creates a status message for the given number of sources.
        '''
        return '%d of %d sources' % (current_count, self._all_sources_count())

class ConditionSearchDataProvider(object):
    '''
    Implements all required methods for a condition search_descriptor.
    '''
    def __init__(self, db_service):
        self.db_service = db_service

    def create_liststore(self):
        return gtk.ListStore(gobject.TYPE_STRING)

    def column_headings(self):
        return ['name']

    def filtered_objects(self, name):
        return self.db_service.filter_conditions_by_name(name)

    def create_liststore_data(self, condition):
        return [condition.get_name()]

    def _all_conditions_count(self):
        '''
        Returns the count of conditions inside the database.
        '''
        return self.db_service.count_sources()

    def status_message(self, current_count):
        '''
        Creates a status message for the given number of sources.
        '''
        return '%d of %d conditions' % (current_count, self._all_sources_count())


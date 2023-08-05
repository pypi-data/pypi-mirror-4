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

import unittest

import logging

LOGGER = logging.getLogger('chessproblem.model')
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(logging.FileHandler('db_test.log'))

from db import DbService, DatabaseChessProblemModelFactory

from . import Author
from . import City
from . import Country

from sqlalchemy.orm import clear_mappers

import kph

class DatabaseTestCase(unittest.TestCase):
    def _update(self, stmt, params=None):
        sf = self.db_service.session_factory()
        con = sf.connection().connection
        c = con.cursor()
        if params == None:
            c.execute(stmt)
        else:
            c.execute(stmt, params)
        con.commit()

    def query(self, query):
        sf = self.db_service.session_factory()
        con = sf.connection().connection
        c = con.cursor()
        c.execute(query)
        return [row for row in c]

    def databaseSetup(self):
        clear_mappers()
        self.db_service = DbService('sqlite:///:memory:')
        # Insert some test data
        self._update('INSERT INTO countries (id, car_code, name, search) VALUES (?, ?, ?, ?)', (0, 'B', 'Belgien', 'belgien'))
        self._update('INSERT INTO cities (id, name, search, country_id, kph) VALUES (?, ?, ?, ?, ?)', (0, 'Genk', 'genk', 0, kph.encode('genk')))
        self._update('INSERT INTO authors (id, lastname, firstname, search, city_id, lastname_kph, firstname_kph) VALUES(?, ?, ?, ?, ?, ?, ?)', (0, 'ellinghoven', 'bernd', 'ellinghoven, bernd', 0, kph.encode('ellinghoven'), kph.encode('bernd')))
        # persistente objects from these instances
        self.belgium = self.db_service.find_country_by_code('B')
        self.genk = self.db_service.find_city_by_name_and_country('Genk', self.belgium)

class DbServiceTest(DatabaseTestCase):
    '''
    Contains testcases for the chessproblem.model.db.DbService class.
    '''

    def setUp(self):
        self.databaseSetup()

    def test_find_country_by_code(self):
        country = self.db_service.find_country_by_code('B')
        self.assertTrue(country != None)
        self.assertEqual(country.car_code, 'B')
        self.assertEqual(country.name, 'Belgien')
        self.assertEqual(country.search, 'belgien')

    def test_store_country(self):
        country = Country('D', 'Deutschland')
        self.db_service.store_country(country)
        rows = self.query("select car_code, name, search from countries where car_code = 'D'")
        self.assertEqual(1, len(rows))
        row = rows[0]
        self.assertEqual(3, len(row))
        self.assertEqual('D', row[0])
        self.assertEqual('Deutschland', row[1])
        self.assertEqual('deutschland', row[2])

    def test_find_city_by_name_and_country(self):
        city = self.db_service.find_city_by_name_and_country('Genk', self.belgium)
        self.assertTrue(city != None)
        self.assertEqual(city.name, 'Genk')
        self.assertEqual(city.search, 'genk')
        self.assertEqual(city.country.car_code, self.belgium.car_code)

    def test_store_city(self):
        city = City('Antwerpen', self.belgium)
        self.db_service.store_city(city)
        rows = self.query("select name, search, country_id from cities where id > 0")
        self.assertEqual(1, len(rows))
        row = rows[0]
        self.assertEqual(3, len(row))
        self.assertEqual('Antwerpen', row[0])
        self.assertEqual('antwerpen', row[1])
        self.assertEqual(self.belgium.id, int(row[2]))



    def test_test_find_author_by_lastname_firstname_city(self):
        author = self.db_service.find_author_by_lastname_firstname_city(self.genk, 'ellinghoven', 'bernd')
        self.assertTrue(author != None, 'existing author not found')

    def test_store_author(self):
        author = Author('Brixen', 'Thierry', self.genk)
        self.db_service.store_author(author)
        rows = self.query("select lastname, firstname, city_id, search from authors where id > 0")
        self.assertEqual(1, len(rows))
        row = rows[0]
        self.assertEqual(4, len(row))
        self.assertEqual('Brixen', row[0])
        self.assertEqual('Thierry', row[1])
        self.assertEqual(self.genk.id, int(row[2]))
        self.assertEqual('brixen, thierry', row[3])


class DatabaseChessProblemModelFactoryTest(DatabaseTestCase):

    def setUp(self):
        self.databaseSetup()
        self.factory = DatabaseChessProblemModelFactory(self.db_service)

    def test_create_country(self):
        country = self.factory.create_country('S', 'Schweden')
        self.assertEqual('S', country.car_code)
        self.assertEqual('Schweden', country.name)
        self.assertEqual('schweden', country.search)
        rows = self.query("select car_code, name, search from countries where car_code = 'S'")
        self.assertEqual(1, len(rows))
        row = rows[0]
        self.assertEqual(3, len(row))
        self.assertEqual('S', row[0])
        self.assertEqual('Schweden', row[1])
        self.assertEqual('schweden', row[2])

    def test_create_city(self):
        oslo = self.factory.create_city(self.belgium, 'Antwerpen')
        rows = self.query("select country_id, name, search from cities where search='antwerpen'")
        self.assertEqual(1, len(rows))
        row = rows[0]
        self.assertEqual(3, len(row))
        self.assertEqual(self.belgium.id, int(row[0]))
        self.assertEqual('Antwerpen', row[1])
        self.assertEqual('antwerpen', row[2])

    def test_create_author(self):
        author = self.factory.create_author(self.genk, 'Hubert', 'Hans')
        rows = self.query("select id, lastname, firstname, city_id, search from authors where id > 0")
        self.assertEqual(1, len(rows))
        row = rows[0]
        self.assertEqual(5, len(row))
        self.assertEqual('Hubert', row[1])
        self.assertEqual('Hans', row[2])
        self.assertEqual(0, row[3])
        self.assertEqual('hubert, hans', row[4])

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

LOGGER = logging.getLogger('chessproblem.ui.database.file_importer')
LOGGER.setLevel(logging.DEBUG)
filehandler = logging.FileHandler('file_importer_test.log')
LOGGER.addHandler(filehandler)

from chessproblem.model import Country, City, Author, Chessproblem, ChessproblemDocument

from chessproblem.ui.database.file_importer import AuthorIterator

def _create_author(lastname, firstname, city_name, country_code):
    country = Country(country_code)
    city = City(city_name, country)
    author = Author(lastname, firstname, city)
    return author

class AuthorIteratorTest(unittest.TestCase):
    def setUp(self):
        self.problem_without_author = Chessproblem()
        self.problem_with_single_author = Chessproblem()
        self.problem_with_single_author.authors.append(_create_author('ellinghoven', 'bernd', 'Aachen', 'D'))
        self.problem_with_multiple_authors = Chessproblem()
        self.problem_with_multiple_authors.authors.append(_create_author('ellinghoven', 'bernd', 'Aachen', 'D'))
        self.problem_with_multiple_authors.authors.append(_create_author('Borst', 'Dirk', 'Utrecht', 'NL'))
        self.problem_with_multiple_authors.authors.append(_create_author('Rehm', 'Hans-Peter', 'Karlsruhe', 'D'))


    def _expect_exception(self, it):
        try:
            it.next_author()
            self.fail('AuthorIterator should raise a StopIterationException')
        except StopIteration:
            pass

    def test_emptyList(self):
        it = AuthorIterator(ChessproblemDocument([]))
        self._expect_exception(it)

    def test_singleProblemWithoutAuthors(self):
        it = AuthorIterator(ChessproblemDocument([self.problem_without_author]))
        self._expect_exception(it)

    def test_problemsWithOneAuthor(self):
        it = AuthorIterator(ChessproblemDocument([self.problem_with_single_author, self.problem_without_author]))
        author = it.next_author()
        self.assertEqual('ellinghoven', author.lastname)
        self.assertEqual('bernd', author.firstname)
        self.assertEqual('Aachen', author.city.name)
        self.assertEqual('D', author.city.country.car_code)
        self._expect_exception(it)

    def test_multipleProblemsWithMultipleAuthors(self):
        it = AuthorIterator(ChessproblemDocument([self.problem_with_single_author, self.problem_without_author, self.problem_with_multiple_authors]))
        author = it.next_author()
        self.assertEqual('ellinghoven', author.lastname)
        self.assertEqual('bernd', author.firstname)
        self.assertEqual('Aachen', author.city.name)
        self.assertEqual('D', author.city.country.car_code)
        author = it.next_author()
        self.assertEqual('ellinghoven', author.lastname)
        self.assertEqual('bernd', author.firstname)
        self.assertEqual('Aachen', author.city.name)
        self.assertEqual('D', author.city.country.car_code)
        author = it.next_author()
        self.assertEqual('Borst', author.lastname)
        self.assertEqual('Dirk', author.firstname)
        self.assertEqual('Utrecht', author.city.name)
        self.assertEqual('NL', author.city.country.car_code)
        author = it.next_author()
        self.assertEqual('Rehm', author.lastname)
        self.assertEqual('Hans-Peter', author.firstname)
        self.assertEqual('Karlsruhe', author.city.name)
        self.assertEqual('D', author.city.country.car_code)
        self._expect_exception(it)


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

from chessproblem.model import Chessproblem, ChessproblemDocument

import unittest

import logging

LOGGER = logging.getLogger('chessproblem.io')
LOGGER.setLevel(logging.DEBUG)
filehandler = logging.FileHandler('parse_latex_str_test.log')
LOGGER.addHandler(filehandler)


class ChessproblemDocumentTest(unittest.TestCase):
    def setUp(self):
        self.initial_document = ChessproblemDocument()
        self.simple_diagram_document = ChessproblemDocument(['%\n', Chessproblem(), '\n%\n'])
        self.document_with_3_problems = ChessproblemDocument(['%\n', Chessproblem(), '\n%\n', Chessproblem(), '\n%\n', Chessproblem(), '\n%\n'])
        self.text_only_document = ChessproblemDocument(['blabla'])

    def test_initial_document(self):
        self.assertEquals(2, self.initial_document.get_text_count())
        self.assertEquals(1, self.initial_document.get_problem_count())

    def test_simple_diagram_document(self):
        self.assertEquals(2, self.simple_diagram_document.get_text_count())
        self.assertEquals(1, self.simple_diagram_document.get_problem_count())

    def test_get_problem(self):
        self.assertTrue(isinstance(self.document_with_3_problems.get_problem(0), Chessproblem))
        self.assertTrue(isinstance(self.document_with_3_problems.get_problem(1), Chessproblem))
        self.assertTrue(isinstance(self.document_with_3_problems.get_problem(2), Chessproblem))

    def test_text_only_document(self):
        self.assertEquals(0, self.text_only_document.get_problem_count())
        self.assertEquals(1, self.text_only_document.get_text_count())
        self.assertEquals(1, len(self.text_only_document.document_content))

    def test_insert_problem_at_begin(self):
        new_problem = Chessproblem()
        new_problem.sourcenr = 'New'
        self.initial_document.insert_problem(0, new_problem)
        self.assertEquals(2, self.initial_document.get_problem_count())
        self.assertEquals(3, self.initial_document.get_text_count())
        self.assertEquals('%\n', self.initial_document.document_content[0])
        self.assertTrue(isinstance(self.initial_document.document_content[1], Chessproblem))
        self.assertEquals('New', self.initial_document.document_content[1].sourcenr)
        self.assertEquals('%\n%\n%\n', self.initial_document.document_content[2])
        self.assertTrue(isinstance(self.initial_document.document_content[3], Chessproblem))
        self.assertEquals('%\n%\n', self.initial_document.document_content[4])


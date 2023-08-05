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

import StringIO

import logging

from chessproblem.io import ChessProblemLatexParser, write_latex

LOGGER = logging.getLogger('chessproblem.io')
LOGGER.setLevel(logging.DEBUG)
filehandler = logging.FileHandler('read_write_test.log')
LOGGER.addHandler(filehandler)


class ReadWriteLatexTest(unittest.TestCase):
    def setUp(self):
        self.parser = ChessProblemLatexParser()

    def _test_read_write(self, source, expected_output):
        _document = self.parser.parse_latex_str(source)
        output = StringIO.StringIO()
        write_latex(_document, output, False)
        self.assertEqual(expected_output, output.getvalue())


    def test_empty_document(self):
        self._test_read_write(u'\n', u'\n')

    def test_document_without_diagrams(self):
        self._test_read_write(
            u'% Some comment\nThe next text should be centered\\begin{center}blabla\\end{center} this is the end.\n% comment\n',
            u'% Some comment\nThe next text should be centered\\begin{center}blabla\\end{center} this is the end.\n% comment\n')

    def test_document_with_single_empty_diagram(self):
        self._test_read_write(
                u'Some starting text\\begin{diagram}\\end{diagram}%\nThis is the last line\n',
                u'Some starting text\\begin{diagram}\\end{diagram}%\nThis is the last line\n')

    def test_diagram_with_comments_inside(self):
        self._test_read_write(
                u'%\n\\begin{diagram}% Is this in PDB?\n\\end{diagram}%\n%\n',
                u'%\n\\begin{diagram}% Is this in PDB?\n\\end{diagram}%\n%\n')

    def test_diagram_with_comment_at_pieces(self):
        self._test_read_write(
                u'%\n\\begin{diagram}\n\\pieces{nKd1}% There are some pieces missing here\n\\end{diagram}%\n%\n',
                u'%\n\\begin{diagram}\n\\pieces{nKd1}% There are some pieces missing here\n\\end{diagram}%\n%\n')

    def test_diagram_with_comment_at_condition(self):
        self._test_read_write(
                u'%\n\\begin{diagram}\n\\condition{Circe; Madrasi}% Any more conditions\n\\end{diagram}%\n%\n',
                u'%\n\\begin{diagram}\n\\condition{Circe; Madrasi}% Any more conditions\n\\end{diagram}%\n%\n')

    def test_diagram_with_comment_at_gridchess(self):
        self._test_read_write(
                u'%\n\\begin{diagram}\n\\gridchess% Should be automatically set in the future\n\\condition{Gitterschach}% yes\n\\end{diagram}%\n%\n',
                u'%\n\\begin{diagram}\n\\condition{Gitterschach}% yes\n\\gridchess% Should be automatically set in the future\n\\end{diagram}%\n%\n')

    def test_diagram_with_piecedefs(self):
        self._test_read_write(
                u'%\n\\begin{diagram}\n\\piecedefs{{sn}{SU}{Nachtreiter}; {ws}{TL}{Turm-L\\"aufer-J\\"ager}}% Explains the fairy pieces\n\\end{diagram}%\n%\n',
                u'%\n\\begin{diagram}\n\\piecedefs{{sn}{SU}{Nachtreiter}; {ws}{TL}{Turm-L\\"aufer-J\\"ager}}% Explains the fairy pieces\n\\end{diagram}%\n%\n')

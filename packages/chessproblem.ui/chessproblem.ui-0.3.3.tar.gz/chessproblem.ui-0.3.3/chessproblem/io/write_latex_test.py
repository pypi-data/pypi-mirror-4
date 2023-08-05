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

from chessproblem.io import write_latex

import chessproblem.model as model

logger = logging.getLogger('chessproblem.io')
logger.setLevel(logging.DEBUG)
filehandler = logging.FileHandler('write_latex_test.log')
logger.addHandler(filehandler)

class WriteLatexTest(unittest.TestCase):
    def _verify_write_latex_problems(self, problems, expected_output, problems_only=False):
        output = StringIO.StringIO()
        write_latex(model.ChessproblemDocument(problems), output, problems_only)
        self.assertEqual(expected_output, output.getvalue())

    def test_writeEmptyList(self):
        logger.debug('test_writeEmptyList')
        problems = []
        self._verify_write_latex_problems(problems, '')

    def test_write_document_with_no_diagrams(self):
        logger.debug('test_write_document_with_no_diagrams')
        text = 'This is some text \\begin{center} centered \\end{center}\n% some comment'
        self._verify_write_latex_problems([ text ], text)

    
    def test_writeSingleEmptyProblem(self):
        logger.debug('test_writeSingleEmptyProblem')
        problems = [model.Chessproblem()]
        self._verify_write_latex_problems(problems, '\\begin{diagram}%\n\\end{diagram}')

    def test_writeTwoEmptyProblems(self):
        logger.debug('test_writeTwoEmptyProblems')
        problems = [model.Chessproblem(), model.Chessproblem()]
        self._verify_write_latex_problems(problems, '\\begin{diagram}%\n\\end{diagram}\\begin{diagram}%\n\\end{diagram}')

    def test_write_empty_problem_with_comment_inside(self):
        logger.debug('test_write_empty_problem_with_comment_inside')
        problem = model.Chessproblem()
        problem.after_command_text['{diagram}'] = '% Is this in PDB?\n'
        problems = [problem]
        self._verify_write_latex_problems(problems, '\\begin{diagram}% Is this in PDB?\n\\end{diagram}')

    def test_write_problem_with_comment_after_condition(self):
        logger.debug('test_write_problem_with_comment_after_condition')
        problem = model.Chessproblem()
        problem.condition = ['Anticirce']
        problem.after_command_text['condition'] = '% Any more conditions\n'
        problems = [problem]
        self._verify_write_latex_problems(problems, '\\begin{diagram}%\n\\condition{Anticirce}% Any more conditions\n\\end{diagram}')

    def test_write_problem_with_comment_after_sourcenr(self):
        logger.debug('test_write_problem_with_comment_after_sourcenr')
        problem = model.Chessproblem()
        problem.sourcenr = '4711'
        problem.after_command_text['sourcenr'] = '% Echt Koellnisch Wasser\n'
        problems = [problem]
        self._verify_write_latex_problems(problems, '\\begin{diagram}%\n\\sourcenr{4711}% Echt Koellnisch Wasser\n\\end{diagram}')

    def test_writePosition(self):
        logger.debug('test_writePosition')
        problem = model.Chessproblem()
        problem.board.fields[7][0].set_piece(model.Piece(model.PIECE_COLOR_BLACK, model.PIECE_TYPE_KING))
        problem.board.fields[7][2].set_piece(model.Piece(model.PIECE_COLOR_WHITE, model.PIECE_TYPE_KING))
        problem.board.fields[6][0].set_piece(model.Piece(model.PIECE_COLOR_BLACK, model.PIECE_TYPE_PAWN))
        problem.board.fields[5][1].set_piece(model.Piece(model.PIECE_COLOR_WHITE, model.PIECE_TYPE_PAWN))
        problem.board.fields[4][4].set_piece(model.Piece(model.PIECE_COLOR_NEUTRAL, model.PIECE_TYPE_KNIGHT, model.PIECE_ROTATION_LEFT))
        problem.board.fields[0][0].set_piece(model.Piece(model.PIECE_COLOR_BLACK, model.PIECE_TYPE_CIRCLE))
        problem.board.fields[1][1].set_piece(model.Piece(model.PIECE_COLOR_NEUTRAL, model.PIECE_TYPE_EQUIHOPPER))
        problems = [problem]
        self._verify_write_latex_problems(problems, '\\begin{diagram}%\n\\pieces{wKc8, wBb6, sKa8, sBa7, sCa1, nEb2, nSLe5}%\n\\end{diagram}')

    def test_writePosition2(self):
        logger.debug('test_writePosition2')
        problem = model.Chessproblem()
        problem.board.fields[0][4].set_piece(model.Piece(model.PIECE_COLOR_WHITE, model.PIECE_TYPE_KING))
        problem.board.fields[1][4].set_piece(model.Piece(model.PIECE_COLOR_WHITE, model.PIECE_TYPE_KING))
        problem.board.fields[2][4].set_piece(model.Piece(model.PIECE_COLOR_WHITE, model.PIECE_TYPE_KING))
        problem.board.fields[3][4].set_piece(model.Piece(model.PIECE_COLOR_WHITE, model.PIECE_TYPE_KING))
        problems = [problem]
        self._verify_write_latex_problems(problems, '\\begin{diagram}%\n\\pieces{wKe1e2e3e4}%\n\\end{diagram}')

    def test_writeAuthor(self):
        logger.debug('test_writeAuthor')
        problem = model.Chessproblem()
        problem.authors.append(model.Author(lastname='ellinghoven', firstname='bernd'))
        problem.authors.append(model.Author(lastname='H\\"oning', firstname='Stefan'))
        problems = [problem]
        self._verify_write_latex_problems(problems, '\\begin{diagram}%\n\\author{ellinghoven, bernd; H\\"oning, Stefan}%\n\\end{diagram}')

    def test_writeCity(self):
        logger.debug('test_writeCity')
        problem = model.Chessproblem()
        problem.cities = [model.City('Aachen', model.Country('D'))]
        problems = [problem]
        self._verify_write_latex_problems(problems, '\\begin{diagram}%\n\\city{D--Aachen}%\n\\end{diagram}')

    def _test_write_simple_member(self, member_name, value):
        problem = model.Chessproblem()
        setattr(problem, member_name, value)
        problems = [problem]
        expected = '\\begin{diagram}%%\n\\%s{%s}%%\n\\end{diagram}' % (member_name, value)
        self._verify_write_latex_problems(problems, expected)

    def test_writeDedication(self):
        logger.debug('test_writeDedication')
        self._test_write_simple_member('dedication', 'Hans Gruber zum 100000. Cook gewidmet')

    def test_writeAfter(self):
        logger.debug('test_writeAfter')
        self._test_write_simple_member('after', 'nach hg und be')

    def test_writeStipulation(self):
        logger.debug('test_writeStipulation')
        self._test_write_simple_member('stipulation', 'H\\#\\#4 0.1;1.1')

    def test_writeRemark(self):
        logger.debug('test_writeRemark')
        self._test_write_simple_member('remark', '{\\wSU} = Nachtreiter')

    def test_writeSolution(self):
        logger.debug('test_writeSolution')
        self._test_write_simple_member('solution', '1.b5')

    def test_writeCondition(self):
        logger.debug('test_writeCondition')
        problem = model.Chessproblem()
        problem.condition = ['Gitterschach', 'Anticirce']
        problems = [problem]
        self._verify_write_latex_problems(problems, '\\begin{diagram}%\n\\condition{Gitterschach; Anticirce}%\n\\end{diagram}')

    def test_writeTwins(self):
        logger.debug('test_writeTwins')
        problem = model.Chessproblem()
        problem.twins = ['b) +{\\wB}a7', 'c) +{\\sB}f5']
        problems = [problem]
        self._verify_write_latex_problems(problems, '\\begin{diagram}%\n\\twins{b) +{\\wB}a7; c) +{\\sB}f5}%\n\\end{diagram}')

    def test_writeThemes(self):
        logger.debug('test_writeThemes')
        problem = model.Chessproblem()
        problem.themes = ['Platzwechsel', 'Allumwandlung']
        problems = [problem]
        self._verify_write_latex_problems(problems, '\\begin{diagram}%\n\\themes{Platzwechsel; Allumwandlung}%\n\\end{diagram}')

    def _test_write_boolean_member(self, member_name):
        problem = model.Chessproblem()
        setattr(problem, member_name, False)
        problems = [problem]
        self._verify_write_latex_problems(problems, '\\begin{diagram}%\n\\end{diagram}')
        problem = model.Chessproblem()
        setattr(problem, member_name, True)
        problems = [problem]
        expected = '\\begin{diagram}%%\n\\%s%%\n\\end{diagram}' % member_name
        self._verify_write_latex_problems(problems, expected)

    def test_writeHorizontalcylinder(self):
        logger.debug('test_writeHorizontalcylinder')
        self._test_write_boolean_member('horizontalcylinder')

    def test_writeVerticalcylinder(self):
        logger.debug('test_writeVerticalcylinder')
        self._test_write_boolean_member('verticalcylinder')

    def test_writeGridchess(self):
        logger.debug('test_writeGridchess')
        self._test_write_boolean_member('gridchess')

    def test_writeNoframe(self):
        logger.debug('test_writeNoframe')
        self._test_write_boolean_member('noframe')

    def test_writeAllwhite(self):
        logger.debug('test_writeAllwhite')
        self._test_write_boolean_member('allwhite')
        
    def test_writeSwitchcolors(self):
        logger.debug('test_writeSwitchcolors')
        self._test_write_boolean_member('switchcolors')
        
    def test_writeFieldframe(self):
        logger.debug('test_writeFieldframe')
        problem = model.Chessproblem()
        problem.board.fields[2][4].set_has_frame(True)
        problem.board.fields[4][1].set_has_frame(True)
        problem.board.fields[7][2].set_has_frame(True)
        problems = [problem]
        self._verify_write_latex_problems(problems, '\\begin{diagram}%\n\\fieldframe{e3, b5, c8}%\n\\end{diagram}')

    def test_writeNoFields(self):
        logger.debug('test_writeNoFields')
        problem = model.Chessproblem()
        problem.board.fields[0][4].set_nofield(True)
        problem.board.fields[2][3].set_nofield(True)
        problem.board.fields[7][6].set_nofield(True)
        problems = [problem]
        self._verify_write_latex_problems(problems, '\\begin{diagram}%\n\\nofields{e1, d3, g8}%\n\\end{diagram}')

    def test_piecedef(self):
        logger.debug('test_piecedef')
        problem = model.Chessproblem()
        problem.piecedefs = [model.PieceDef('sn', 'SU', 'Nachtreiter'), model.PieceDef('ws', 'TL', 'Turm-L\\"aufer-J\\"ager')]
        problems = [problem]
        self._verify_write_latex_problems(problems, '\\begin{diagram}%\n\\piecedefs{{sn}{SU}{Nachtreiter}; {ws}{TL}{Turm-L\\"aufer-J\\"ager}}%\n\\end{diagram}')


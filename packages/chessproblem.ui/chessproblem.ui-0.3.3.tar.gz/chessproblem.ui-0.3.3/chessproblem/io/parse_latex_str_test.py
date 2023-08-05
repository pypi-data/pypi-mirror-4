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

from chessproblem.io import ChessProblemLatexParser

from chessproblem.model import PIECE_TYPE_KING
from chessproblem.model import PIECE_TYPE_QUEEN
from chessproblem.model import PIECE_TYPE_BISHOP
from chessproblem.model import PIECE_TYPE_CIRCLE
from chessproblem.model import PIECE_TYPE_EQUIHOPPER
from chessproblem.model import PIECE_COLOR_WHITE
from chessproblem.model import PIECE_COLOR_BLACK
from chessproblem.model import PIECE_COLOR_NEUTRAL
from chessproblem.model import PIECE_ROTATION_NORMAL
from chessproblem.model import PIECE_ROTATION_LEFT
from chessproblem.model import PIECE_ROTATION_UPSIDEDOWN

logger = logging.getLogger('chessproblem.io')
logger.setLevel(logging.DEBUG)
filehandler = logging.FileHandler('parse_latex_str_test.log')
logger.addHandler(filehandler)

class ChessproblemLatexParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = ChessProblemLatexParser()

    def test_emptyInput(self):
        logger.debug('test_emptyInput started')
        document = self.parser.parse_latex_str('')
        self.assertEqual(0, document.get_problem_count())
        self.assertEqual(1, document.get_text_count())
        self.assertEqual(u'\n', document.get_text(0))
        logger.debug('test_emptyInput finished')

    def test_nonDiagramInput(self):
        logger.debug('test_nonDiagramInput started')
        document = self.parser.parse_latex_str('%some comment\nsome text and some \\begin{center}latex code\\end{center}\n% this is the end')
        self.assertEqual(0, document.get_problem_count())
        self.assertTrue(document.document_content != None)
        self.assertEqual(1, len(document.document_content))
        self.assertEqual(1, document.get_text_count())
        self.assertEqual(u'%some comment\nsome text and some \\begin{center}latex code\\end{center}\n% this is the end\n', document.get_text(0))
        logger.debug('test_nonDiagramInput finished')

    def test_singleDiagram(self):
        logger.debug('test_singleEmptyDiagram started')
        document = self.parser.parse_latex_str('%\n\\begin{diagram}\\end{diagram}\n%\n')
        self.assertEqual(1, document.get_problem_count())
        self.assertEqual(2, document.get_text_count())
        self.assertEqual(u'%\n', document.get_text(0))
        self.assertEqual(u'\n%\n', document.get_text(1))
        logger.debug('test_singleEmptyDiagram finished')

    def test_diagramWithSingleAuthor(self):
        logger.debug('test_diagramWithSingleAuthor')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\author{H\\"oning, Stefan}%\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual(1, len(problem.authors))
        author = problem.authors[0]
        self.assertEqual('H\\"oning', author.lastname)
        self.assertEqual('Stefan', author.firstname)
        self.assertEqual(None, author.city)
        self.assertEqual('\n', problem.after_command_text['{diagram}'])
        self.assertEqual('%\n', problem.after_command_text['author'])
        self.assertEqual(1, document.get_text_count())
        self.assertEqual('\n', document.get_text(0))

    def test_diagramWithAdditionalSpacesInAuthor(self):
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\author{Osorio, Roberto ; Lois, Jorge Joaquin}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual(2, len(problem.authors))
        author = problem.authors[0]
        self.assertEqual('Osorio', author.lastname)
        self.assertEqual('Roberto', author.firstname)
        author = problem.authors[1]
        self.assertEqual('Lois', author.lastname)
        self.assertEqual('Jorge Joaquin', author.firstname)

    def test_diagramWithMultipleAuthors(self):
        logger.debug('test_diagramWithMultipleAuthors')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\author{Gruber, Hans; ellinghoven, bernd}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual(2, len(problem.authors))
        author = problem.authors[0]
        self.assertEqual('Gruber', author.lastname)
        self.assertEqual('Hans', author.firstname)
        author = problem.authors[1]
        self.assertEqual('ellinghoven', author.lastname)
        self.assertEqual('bernd', author.firstname)

    def test_diagramWithAuthorAndCityNoCountry(self):
        logger.debug('test_diagramWithAuthorAndCity')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\author{Gruber, Hans}\\city{Regensburg}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual(1, len(problem.authors))
        author = problem.authors[0]
        self.assertEqual('Gruber', author.lastname)
        self.assertEqual('Hans', author.firstname)
        self.assertEqual('Regensburg', author.city.name)
        self.assertEqual('D', author.city.country.car_code)
        self.assertEqual(1, len(problem.cities))

    def test_diagramWithMissingNonDefaultCountry(self):
        logger.debug('test_diagramWithMissingNonDefaultCountry')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\author{Lind, Ingemar; Uppstr"om, Rolf}\n\\city{S--Bj"arred; G"oteborg}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual(2, len(problem.authors))
        author = problem.authors[0]
        self.assertEqual('Lind', author.lastname)
        self.assertEqual('Ingemar', author.firstname)
        self.assertEqual('Bj"arred', author.city.name)
        self.assertEqual('S', author.city.country.car_code)
        author = problem.authors[1]
        self.assertEqual('Uppstr"om', author.lastname)
        self.assertEqual('Rolf', author.firstname)
        self.assertEqual('G"oteborg', author.city.name)
        self.assertEqual('S', author.city.country.car_code)
        self.assertEqual(2, len(problem.cities))

    def test_diagramWithDifferentAuthorAndCityCounts(self):
        logger.debug('test_diagramWithDifferentAuthorAndCityCounts')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\author{Lind, Ingemar; Uppstr"om, Rolf; H\\"oning, Stefan}\n\\city{S--Bj"arred; G"oteborg}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual(3, len(problem.authors))
        author = problem.authors[0]
        self.assertEqual('Lind', author.lastname)
        self.assertEqual('Ingemar', author.firstname)
        self.assertEqual(None, author.city)
        author = problem.authors[1]
        self.assertEqual('Uppstr"om', author.lastname)
        self.assertEqual('Rolf', author.firstname)
        self.assertEqual(None, author.city)
        author = problem.authors[2]
        self.assertEqual('H\\"oning', author.lastname)
        self.assertEqual('Stefan', author.firstname)
        self.assertEqual(None, author.city)
        self.assertEqual(2, len(problem.cities))

    def test_diagramWithSingleCityAndMultipleAuthors(self):
        logger.debug('test_diagramWithSingleCityAndMultipleAuthors')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\author{Reich, Hans-Peter; H\\"oning, Stefan}\\city{D--Neuss}\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual(2, len(problem.authors))
        author = problem.authors[0]
        self.assertEqual('Reich', author.lastname)
        self.assertEqual('Hans-Peter', author.firstname)
        self.assertTrue(author.city != None)
        self.assertEqual('Neuss', author.city.name)
        self.assertTrue(author.city.country != None)
        self.assertEqual('D', author.city.country.car_code)
        author = problem.authors[1]
        self.assertEqual('H\\"oning', author.lastname)
        self.assertEqual('Stefan', author.firstname)
        self.assertTrue(author.city != None)
        self.assertEqual('Neuss', author.city.name)
        self.assertTrue(author.city.country != None)
        self.assertEqual('D', author.city.country.car_code)


    def test_diagramWithSingleKing(self):
        logger.debug('test_diagramWithSingleKing')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\pieces{wKd5}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        board = problem.board
        self.assertEqual(8, board.rows)
        self.assertEqual(8, board.columns)
        piece = board.fields[4][3].get_piece()
        self.assertEqual(PIECE_TYPE_KING, piece.piece_type)
        self.assertEqual(PIECE_COLOR_WHITE, piece.piece_color)
        self.assertEqual(PIECE_ROTATION_NORMAL, piece.piece_rotation)

    def test_diagramWithEquihopperAndImitator(self):
        logger.debug('test_diagramEquihopperAndImitator')
        document = self.parser.parse_latex_str('\\begin{diagram}[2x2]\n\\pieces{nCa2, sELb1}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        board = problem.board
        self.assertEqual(2, board.rows)
        self.assertEqual(2, board.columns)
        piece = board.fields[0][1].get_piece()
        self.assertEqual(PIECE_TYPE_EQUIHOPPER, piece.piece_type)
        self.assertEqual(PIECE_COLOR_BLACK, piece.piece_color)
        self.assertEqual(PIECE_ROTATION_LEFT, piece.piece_rotation)
        piece = board.fields[1][0].get_piece()
        self.assertEqual(PIECE_TYPE_CIRCLE, piece.piece_type)
        self.assertEqual(PIECE_COLOR_NEUTRAL, piece.piece_color)
        self.assertEqual(PIECE_ROTATION_NORMAL, piece.piece_rotation)

    def test_diagramWithMultiplePieces(self):
        logger.debug('test_diagramWithMultiplePieces')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\pieces{wKd5, sDLc7, nLUh3h4h5, sCa1}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        board = problem.board
        self.assertEqual(8, board.rows)
        self.assertEqual(8, board.columns)
        piece = board.fields[4][3].get_piece()
        self.assertEqual(PIECE_TYPE_KING, piece.piece_type)
        self.assertEqual(PIECE_COLOR_WHITE, piece.piece_color)
        self.assertEqual(PIECE_ROTATION_NORMAL, piece.piece_rotation)
        piece = board.fields[6][2].get_piece()
        self.assertEqual(PIECE_TYPE_QUEEN, piece.piece_type)
        self.assertEqual(PIECE_COLOR_BLACK, piece.piece_color)
        self.assertEqual(PIECE_ROTATION_LEFT, piece.piece_rotation)
        piece = board.fields[2][7].get_piece()
        self.assertEqual(PIECE_TYPE_BISHOP, piece.piece_type)
        self.assertEqual(PIECE_COLOR_NEUTRAL, piece.piece_color)
        self.assertEqual(PIECE_ROTATION_UPSIDEDOWN, piece.piece_rotation)
        piece = board.fields[3][7].get_piece()
        self.assertEqual(PIECE_TYPE_BISHOP, piece.piece_type)
        self.assertEqual(PIECE_COLOR_NEUTRAL, piece.piece_color)
        self.assertEqual(PIECE_ROTATION_UPSIDEDOWN, piece.piece_rotation)
        piece = board.fields[4][7].get_piece()
        self.assertEqual(PIECE_TYPE_BISHOP, piece.piece_type)
        self.assertEqual(PIECE_COLOR_NEUTRAL, piece.piece_color)
        self.assertEqual(PIECE_ROTATION_UPSIDEDOWN, piece.piece_rotation)
        piece = board.fields[0][0].get_piece()
        self.assertEqual(PIECE_TYPE_CIRCLE, piece.piece_type)
        self.assertEqual(PIECE_COLOR_BLACK, piece.piece_color)
        self.assertEqual(PIECE_ROTATION_NORMAL, piece.piece_rotation)

    def test_diagramWithLineBreakWithinPieces(self):
        logger.debug('test_diagramWithLineBreakWithinPieces')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\pieces{wKa1, %\n    wDa2}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        board = problem.board
        king = board.fields[0][0].get_piece()
        self.assertEqual(PIECE_TYPE_KING, king.piece_type)
        self.assertEqual(PIECE_COLOR_WHITE, king.piece_color)
        self.assertEqual(PIECE_ROTATION_NORMAL, king.piece_rotation)
        queen = board.fields[1][0].get_piece()
        self.assertEqual(PIECE_TYPE_QUEEN, queen.piece_type)
        self.assertEqual(PIECE_COLOR_WHITE, queen.piece_color)
        self.assertEqual(PIECE_ROTATION_NORMAL, queen.piece_rotation)

    def test_diagramWithPieceCounter(self):
        logger.debug('test_diagramWithPieceCounter')
        document = self.parser.parse_latex_str('''
                \\begin{diagram}
                \\pieces[3+7]{wKa1, wDa2, sKc7, sTf8h8, sBh7h6}
                \\end{diagram}
                %
                \\begin{diagram}
                \\pieces[0+0+6]{nKd1, nDc5, nTg3, nLd5, nBc3}
                \\end{diagram}
                ''')
        self.assertEqual(2, document.get_problem_count())
        # Check first problem
        problem = document.get_problem(0)
        self.assertTrue(problem.pieces_control != None)
        # Check second problem
        problem = document.get_problem(1)
        self.assertTrue(problem.pieces_control != None)


    def test_diagramWithStipulation(self):
        logger.debug('test_diagramWithStipulation')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\stip{H\\#4}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual('H\\#4', problem.stipulation)
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\stipulation{H\\#4}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual('H\\#4', problem.stipulation)

    def test_diagramWithConditions(self):
        logger.debug('test_diagramWithConditions')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\cond{Circe; Madrasi}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual(2, len(problem.condition))
        self.assertEqual('Circe', problem.condition[0].get_name())
        self.assertEqual('Madrasi', problem.condition[1].get_name())
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\condition{Gitterschach}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual(1, len(problem.condition))
        self.assertEqual('Gitterschach', problem.condition[0].get_name())
        self.assertTrue(problem.gridchess)

    def test_diagramWithSolution(self):
        logger.debug('test_diagramWithSolution')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\sol{NL}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual('NL', problem.solution)
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\solution{NL}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual('NL', problem.solution)

    def test_diagramWithDedication(self):
        logger.debug('test_diagramWithDedication')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\dedic{be gewidmet}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual('be gewidmet', problem.dedication)
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\dedication{be gewidmet}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual('be gewidmet', problem.dedication)

    def test_diagramWithDedication(self):
        logger.debug('test_diagramWithAfter')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\after{nach be und hg}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual('nach be und hg', problem.after)

    def test_diagramWithRemark(self):
        logger.debug('test_diagramWithRemark')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\rem{\\wSU = Nachtreiter}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual('\\wSU = Nachtreiter', problem.remark)
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\remark{\\wSU = Nachtreiter}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual('\\wSU = Nachtreiter', problem.remark)

    def test_diagramWithVersion(self):
        logger.debug('test_diagramWithRemark')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\version{Version Thomas Brand}\n\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual('Version Thomas Brand', problem.version)

    def test_diagramWithDayMonthYear(self):
        logger.debug('test_diagramWithDayMonthYear')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\day{1}\n\\month{4-8}\\year{1942}\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual('1', problem.day)
        self.assertEqual('4-8', problem.month)
        self.assertEqual('1942', problem.year)

    def test_diagramWithNofields(self):
        logger.debug('test_diagramWithNofields')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\nofields{f7, c4, g5}\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual(True, problem.board.fields[6][5].is_nofield())
        self.assertEqual(True, problem.board.fields[3][2].is_nofield())
        self.assertEqual(True, problem.board.fields[4][6].is_nofield())
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\nosquares{f3, c5, g8}\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual(True, problem.board.fields[2][5].is_nofield())
        self.assertEqual(True, problem.board.fields[4][2].is_nofield())
        self.assertEqual(True, problem.board.fields[7][6].is_nofield())

    def test_diagramWithFieldframe(self):
        logger.debug('test_diagramWithFieldframe')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\fieldframe{f2, d4, h5}\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual(True, problem.board.fields[1][5].has_frame())
        self.assertEqual(True, problem.board.fields[3][3].has_frame())
        self.assertEqual(True, problem.board.fields[4][7].has_frame())

    def test_diagramWithFieldtext(self):
        logger.debug('test_diagramWithFieldtext')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\fieldtext{{Stefan}f2, {bernd}d4, {hans}h5}\\end{diagram}')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual('{Stefan}f2, {bernd}d4, {hans}h5', problem.fieldtext)

    def _test_boolean(self, debug_log, latex_command, member_name=None):
        '''
        A Helper method for test of boolean switches.
        '''
        logger.debug(debug_log)
        document = self.parser.parse_latex_str('\\begin{diagram}\n\\%s\\end{diagram}' % (latex_command))
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        if member_name == None:
            member_name = latex_command
        value = getattr(problem, member_name)
        self.assertEqual(True, value)

    def test_diagramWithVerticalcylinder(self):
        self._test_boolean('test_diagramWithVerticalcylinder', 'verticalcylinder')

    def test_diagramWithHorizontalcylinder(self):
        self._test_boolean('test_diagramWithHorizontalcylinder', 'horizontalcylinder')

    def test_diagramWithNoframe(self):
        self._test_boolean('test_diagramWithNoframe', 'noframe')

    def test_diagramWithGridchess(self):
        self._test_boolean('test_diagramWithGridchess', 'gridchess')

    def test_diagramWithAllwhite(self):
        self._test_boolean('test_diagramWithAllwhite', 'allwhite')

    def test_diagramWithSwitchcolors(self):
        self._test_boolean('test_diagramWithSwitchcolors', 'switchcolors')

    def test_BigDiagram(self):
        logger.debug('test_BigDiagram')
        document = self.parser.parse_latex_str('\\begin{diagram}[10x10]\n\\pieces{wBb4d4g6h6d7, wLa{10}, wTh4, wKe1, wSLh1b2, wLLj2a5e8, wTLj5b6i6c7d9f{10}, wDLg5, wLUi5, sBc3g3c4i8, sSf9, sKe6, sSLf2b9, sLLa4h8d{10}, sLUh{10}}\n\\end{diagram}\n')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertTrue(problem.board != None)
        self.assertEqual(10, problem.board.columns)
        self.assertEqual(10, problem.board.rows)
        self.assertEqual('\n', problem.after_command_text['{diagram}'])
        self.assertTrue(problem.board.fields[4][8].get_piece() != None)
        self.assertTrue(problem.board.fields[9][7].get_piece() != None)

    def test_diagramWith_piecedefs(self):
        logger.debug('test_diagramWith_piecedefs')
        document = self.parser.parse_latex_str('\\begin{diagram}\n\piecedefs{{sn}{SU}{Nachtreiter}; {ws}{TL}{Turm-L\\"aufer-J\\"ager}}\n\\end{diagram}\n')
        self.assertEqual(1, document.get_problem_count())
        problem = document.get_problem(0)
        self.assertEqual(2, len(problem.piecedefs))
        piecedef = problem.piecedefs[0]
        self.assertEqual('sn', piecedef.colors)
        self.assertEqual('SU', piecedef.piece_symbol)
        self.assertEqual('Nachtreiter', piecedef.name)
        piecedef = problem.piecedefs[1]
        self.assertEqual('ws', piecedef.colors)
        self.assertEqual('TL', piecedef.piece_symbol)
        self.assertEqual('Turm-L\\"aufer-J\\"ager', piecedef.name)


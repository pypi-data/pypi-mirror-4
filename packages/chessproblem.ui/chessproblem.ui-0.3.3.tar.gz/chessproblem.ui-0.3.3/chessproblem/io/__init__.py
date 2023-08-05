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
This modules contains the code to read and write chessproblems from and to latex files.
'''

from pygments.lexers import TexLexer
from pygments.token import Token

from chessproblem.config import DEFAULT_CONFIG

from chessproblem.model import Chessproblem, ChessproblemDocument, PieceCounter
from chessproblem.model import Author
from chessproblem.model import Piece
from chessproblem.model import ChessProblemModelFactory
from chessproblem.model import PIECE_ROTATION_NORMAL
from chessproblem.model import PIECE_COLOR_COUNT
from chessproblem.model import PIECE_TYPE_COUNT
from chessproblem.model import PIECE_ROTATION_COUNT
import chessproblem.model as model

from chessproblem.model.conditions import CONDITION_SERVICE

import logging
import re
import string

LOGGER = logging.getLogger('chessproblem.io')

DEFAULT_STATE  = 0
START_DIAGRAM  = 1
WITHIN_DIAGRAM = 2

PIECE_CHARACTERS = ['B', 'S', 'L', 'T', 'D', 'K', 'E', 'C']
PIECE_COLORS = ['w', 's', 'n']
PIECE_ROTATIONS = ['L', 'R', 'U']

COLUMN_CHARACTERS = string.ascii_lowercase


CONTENT_COMMANDS = set([
    'author',
    'pieces',
    'city',
    'stipulation',
    'sourcenr',
    'source',
    'issue',
    'day',
    'month',
    'year',
    'condition',
    'twins',
    'version',
    'solution',
    'themes',
    'dedication',
    'after',
    'remark',
    'specialdiagnum',
    'pages',
    'comment',
    'tournament',
    'award',
    'nofields',
    'fieldframe',
    'gridlines',
    'fieldtext',
    'piecedefs'])

TRUE_COMMANDS = set(['verticalcylinder', 'horizontalcylinder', 'gridchess', 'noframe', 'allwhite', 'switchcolors'])

ABBREVIATED_CONTENT_COMMANDS = {
    'stip': 'stipulation',
    'cond': 'condition',
    'sol': 'solution',
    'dedic': 'dedication',
    'rem': 'remark',
    'months': 'month',
    'nosquares': 'nofields'}

class InvalidLatexCode(BaseException):
    '''
    This Exception is raised by method parse_latex_str when there are syntactical problems in the input string.
    '''
    def __init__(self,text):
        self.text = text

def ignore_token(token, text):
    '''
    Used as callback to ignore tokens.
    '''
    LOGGER.debug('Ignoring token: ' + str(token) + ' - ' + text)

def _command_name(command_str):
    if command_str[0] == '\\':
        return command_str[1:]
    else:
        return command_str

class LatexTokenizer(object):
    def __init__(self, text):
        lexer = TexLexer()
        self.tokens = lexer.get_tokens(text)

    def next_token(self):
        token, text = self.tokens.next()
        LOGGER.debug('LatexTokenizer.next_token(): ' + str(token) + ', "' + text + '"')
        return token, text


class ChessProblemLatexParser(object):
    def __init__(self, model_object_factory=ChessProblemModelFactory()):
        self.model_object_factory = model_object_factory

    def parse_latex_str(self,latex_text):
        '''
        This function parses a given string (file) and creates a list of Chessproblem instances from its contents.
        '''
        problems = []
        tokenizer = LatexTokenizer(latex_text)
        state = DEFAULT_STATE
        current_problem_content = None
        current_text = ''
        last_command_name = None
        after_command_text = None
        try:
            while True:
                token, text = tokenizer.next_token()
                LOGGER.debug('parse_latex_str - text: ' + text)
                if state == DEFAULT_STATE:
                    if token is Token.Keyword and text == '\\begin':
                        LOGGER.debug("Reading environment start (token - text): %s - %s", token, text)
                        environment_name = _read_environment_name(tokenizer)
                        if environment_name == 'diagram':
                            if len(current_text) > 0:
                                LOGGER.debug('parse_latex_str - got text before \\begin{diagram}: "' + current_text + '"')
                                problems.append(current_text)
                            state = START_DIAGRAM
                            current_problem_content = {}
                            current_text = ''
                            after_command_text = {}
                            last_command_name = '{diagram}'
                        else:
                            current_text += '\\begin{' + environment_name + '}'
                    else:
                        current_text += text
                else: # state == START_DIAGRAM or state == WITHIN_DIAGRAM
                    if token is Token.Keyword:
                        if text == '\\end':
                            LOGGER.debug("Reading environment end (token - text): %s - %s", token, text)
                            environment_name = _read_environment_name(tokenizer)
                            if environment_name == 'diagram':
                                if current_text != '':
                                    after_command_text[last_command_name] = current_text
                                problem = self.create_problem(current_problem_content, after_command_text)
                                problems.append(problem)
                                current_problem_content = None
                                state = DEFAULT_STATE
                                current_text = ''
                                last_command_name = None
                                after_command_text = None
                        else:
                            command = content_command(text)
                            if command != None:
                                if current_text != '':
                                    after_command_text[last_command_name] = current_text
                                current_text = ''
                                last_command_name = _command_name(text)
                                command.parse_to_problem_content(tokenizer, current_problem_content)
                            else:
                                current_text += text
                            state = WITHIN_DIAGRAM
                    elif token == Token.Text:
                        if state == START_DIAGRAM:
                            match_result = re.match('\[([0-9]+)x([0-9]+)\]', text)
                            if match_result != None:
                                columns = int(match_result.group(1))
                                rows = int(match_result.group(2))
                                current_problem_content['board_size'] = (columns, rows)
                                current_text += text[len(match_result.group(0)):]
                            else:
                                current_text += text
                        else:
                            current_text += text
                        state = WITHIN_DIAGRAM
                    else:
                        current_text += text
        except StopIteration:
            if not state == DEFAULT_STATE:
                raise InvalidLatexCode('\\begin{diagram} not closed using \\end{diagram}.')
        if len(current_text) > 0:
            LOGGER.debug('parse_latex_str - got text before end of document: ' + current_text)
            problems.append(current_text)
        return ChessproblemDocument(problems)


    def create_problem(self, problem_content, after_command_text):
        '''
        Creates a Chessproblem instance filled with values from the given dictionary object.
        '''
        if 'board_size' in problem_content:
            (columns, rows) = problem_content['board_size']
            LOGGER.info('Creating larger board size (columns, rows): (' + str(columns) + ',' + str(rows) + ')')
            result = Chessproblem(columns=columns, rows=rows)
        else:
            result = Chessproblem()
        result.after_command_text = after_command_text
        if 'city' in problem_content:
            result.cities = self._parse_cities(problem_content['city'])
        if 'author' in problem_content:
            result.authors = self._parse_authors(problem_content['author'], result.cities)
        if 'pieces' in problem_content:
            result.pieces = _parse_pieces(problem_content['pieces'], result.board)
        if 'piece_count' in problem_content:
            result.pieces_control = _parse_pieces_control(problem_content['piece_count'])
        if 'stipulation' in problem_content:
            result.stipulation = problem_content['stipulation']
        if 'sourcenr' in problem_content:
            result.sourcenr = problem_content['sourcenr']
        if 'source' in problem_content:
            result.source = problem_content['source']
        if 'issue' in problem_content:
            result.issue = problem_content['issue']
        if 'day' in problem_content:
            result.day = problem_content['day']
        if 'month' in problem_content:
            result.month = problem_content['month']
        if 'year' in problem_content:
            result.year = problem_content['year']
        if 'condition' in problem_content:
            result.condition = self._create_conditions(problem_content['condition'])
        if 'twins' in problem_content:
            result.twins = [s.strip() for s in re.split('[;,] ', problem_content['twins'])]
        if 'solution' in problem_content:
            result.solution = problem_content['solution']
        if 'themes' in problem_content:
            result.themes = [s.strip() for s in re.split('[;,] ', problem_content['themes'])]
        if 'dedication' in problem_content:
            result.dedication = problem_content['dedication']
        if 'version' in problem_content:
            result.version = problem_content['version']
        if 'after' in problem_content:
            result.after = problem_content['after']
        if 'remark' in problem_content:
            result.remark = problem_content['remark']
        if 'specialdiagnum' in problem_content:
            result.specialdiagnum = problem_content['specialdiagnum']
        if 'pages' in problem_content:
            result.pages = problem_content['pages']
        if 'comment' in problem_content:
            result.comment = problem_content['comment']
        if 'tournament' in problem_content:
            result.tournament = problem_content['tournament']
        if 'award' in problem_content:
            result.award = problem_content['award']
        if 'horizontalcylinder' in problem_content:
            result.horizontalcylinder = True
        if 'verticalcylinder' in problem_content:
            result.verticalcylinder = True
        if 'gridchess' in problem_content:
            result.gridchess = True
        if 'noframe' in problem_content:
            result.noframe = True
        if 'allwhite' in problem_content:
            result.allwhite = True
        if 'switchcolors' in problem_content:
            result.switchcolors = True
        if 'nofields' in problem_content:
            _parse_nofields(problem_content['nofields'], result.board)
        if 'fieldframe' in problem_content:
            _parse_fieldframe(problem_content['fieldframe'], result.board)
        if 'gridlines' in problem_content:
            result.gridlines = problem_content['gridlines']
        if 'fieldtext' in problem_content:
            result.fieldtext = problem_content['fieldtext']
        if 'piecedefs' in problem_content:
            result.piecedefs = _parse_piecedefs(problem_content['piecedefs'])
        # Any conditions which have problem actions should run these actions now
        for condition in result.condition:
            condition.execute_problem_action(result)
        return result

    def _parse_cities(self, cities_str):
        '''
        Parses the given cities string and creates a list of City instances from its values.
        '''
        cities = [s.strip() for s in cities_str.split(';')]
        result = []
        last_country = DEFAULT_CONFIG.default_country
        for i in range(len(cities)):
            city_str = cities[i]
            country_city = DEFAULT_CONFIG.city_split(city_str)
            if len(country_city) == 2:
                last_country = country_city[0]
                country = self.model_object_factory.create_country(last_country)
                city = self.model_object_factory.create_city(country, country_city[1])
            else:
                country = self.model_object_factory.create_country(last_country)
                city = self.model_object_factory.create_city(country, country_city[0])
            result.append(city)
        return result

    def _parse_authors(self, authors_str, cities):
        '''
        Parses the given authors string and creates a list of Author instances from its values.
        The provided cities will be distributed among the authors.
        '''
        result = []
        authors_split = [s.strip() for s in authors_str.split(';')]
        if len(authors_split) == len(cities):
            LOGGER.debug('Number of authors matches number of cities.')
            for i in range(len(authors_split)):
                city = cities[i]
                author_name = authors_split[i]
                parts = author_name.split(', ')
                author = self.model_object_factory.create_author(city, parts[0].strip(), parts[1].strip())
                result.append(author)
        elif len(cities) == 1:
            city = cities[0]
            for i in range(len(authors_split)):
                author_name = authors_split[i]
                parts = author_name.split(', ')
                author = self.model_object_factory.create_author(city, parts[0].strip(), parts[1].strip())
                result.append(author)
        else:
            LOGGER.warn('Number of authors does not match number of cities.')
            for author_name in authors_split:
                parts = author_name.split(', ')
                author = self.model_object_factory.create_author(None, parts[0].strip(), parts[1].strip())
                result.append(author)
        return result

    def _parse_fields(self, fields_str):
        pass

    def _create_conditions(self, condition_str):
        result = []
        for s in re.split('[;,] ', condition_str):
            condition_name = s.strip()
            condition = CONDITION_SERVICE.get_condition_by_name(condition_name)
            result.append(condition)
        return result

def parse_one_parameter(tokenizer):
    result = _read_parameter(tokenizer)
    LOGGER.debug('parse_one_parameter(tokens) => %s' % result)
    return result

def true_parameter(tokens):
    return True

class ContentCommand(object):
    def __init__(self, name, parameter_parser=parse_one_parameter):
        self.name = name
        self._parameter_parser = parameter_parser

    def parse_to_problem_content(self, tokenizer, problem_content):
        problem_content[self.name] = self._parameter_parser(tokenizer)

class PiecesCommand(object):
    '''
    A special command to parse pieces, as we need to handle the optional piece count.
    '''
    def __init__(self):
        self.piece_count = None

    def parse_to_problem_content(self, tokenizer, problem_content):
        problem_content['pieces'] = _read_parameter(tokenizer, token_handler=self._handle_piececounter)
        problem_content['piece_count'] = self.piece_count

    def _handle_piececounter(self, token, text):
        if token == Token.Name.Attribute:
            self.piece_count = text
            LOGGER.debug('Got piece count from file: ' + text)


def content_command(s):
    '''
    Used to determine the command inside the diagram environment.

    The leading \\ is removed from the given string and then compared to the given registered CONTENT_COMMANDS.
    If no match is found, the command is checked, whether it is a known abbreviation for a known content command.
    '''
    LOGGER.debug('content_command(%s)' % s)
    cmd = _command_name(s)
    if cmd in ABBREVIATED_CONTENT_COMMANDS:
        command = ABBREVIATED_CONTENT_COMMANDS[cmd]
        LOGGER.debug('mapping abbreviated command %s to %s' % (cmd, command))
    else:
        command = cmd
    if command == 'pieces':
        return PiecesCommand()
    elif command in CONTENT_COMMANDS:
        return ContentCommand(command)
    elif command in TRUE_COMMANDS:
        return ContentCommand(command, true_parameter)
    else:
        return None

def _parse_pieces(pieces, board):
    '''
    Parses the given pieces specification and places the found pieces on the fields in the given board.
    '''
    for piece_spec in pieces.split(','):
        piece_spec = piece_spec.strip()
        LOGGER.debug('parsing piece_spec: ' + piece_spec)
        _piece_color = piece_color(piece_spec[0])
        _piece_type = piece_type(piece_spec[1])
        rotation = piece_spec[2]
        if rotation in PIECE_ROTATIONS:
            _piece_rotation = piece_rotation(rotation)
            index = 3
        else:
            _piece_rotation = PIECE_ROTATION_NORMAL
            index = 2
        piece = Piece(_piece_color, _piece_type, _piece_rotation)
        try:
            while index < len(piece_spec):
                _column = column(piece_spec[index])
                index += 1
                if piece_spec[index] == '{':
                    _row_value = ''
                    index += 1
                    while piece_spec[index] != '}':
                        _row_value += piece_spec[index]
                        index += 1
                    LOGGER.debug('parsed large row: ' + _row_value)
                    _row = int(_row_value) - 1
                else:
                    _row = row(piece_spec[index])
                board.fields[_row][_column].set_piece(piece)
                index += 1
        except IndexError as e:
            LOGGER.error('Error parsing pieces specification: ' + pieces)
            raise e

def _parse_pieces_control(text):
    m = re.match('\[([0-9]+)\+([0-9]+)(?:\+([0-9]+))?\]', str(text))
    if m:
        (s_white, s_black, s_neutral) = m.groups('0')
        return PieceCounter(int(s_white), int(s_black), int(s_neutral))
    return None

def _set_fieldframe(board, row, column):
    board.fields[row][column].set_has_frame(True)

def _parse_fieldframe(text, board):
    '''
    Used to parse the contents of the \\fieldframe command and set the has_frame value on the appropriate fields within the given board.
    '''
    _parse_fieldlist(text, board, _set_fieldframe)

def _set_nofield(board, row, column):
    board.fields[row][column].set_nofield(True)

def _parse_nofields(text, board):
    _parse_fieldlist(text, board, _set_nofield)

def _parse_fieldlist(text, board, action):
    for field_spec in text.split(','):
        field_spec = field_spec.strip()
        _column = column(field_spec[0])
        index = 1
        if field_spec[index] == '{':
            _row_value = ''
            index += 1
            while field_spec[index] != '}':
                _row_value += field_spec[index]
                index += 1
            LOGGER.debug('parsed large row: ' + _row_value)
            _row = int(_row_value) - 1
        else:
            _row = row(field_spec[index])
        action(board, _row, _column)

def _parse_piecedefs(text):
    result = []
    for _s in text.split(';'):
        _s = _s.strip()
        LOGGER.debug('found piecedef: %s' % (_s))
        _tokenizer = LatexTokenizer(_s)
        colors = _read_parameter(_tokenizer)
        LOGGER.debug('colors: %s' % (colors))
        piece_type = _read_parameter(_tokenizer)
        name = _read_parameter(_tokenizer)
        result.append(model.PieceDef(colors, piece_type, name))
    return result

def _read_environment_name(tokenizer):
    _expect_token(tokenizer, Token.Text, '')
    _expect_token(tokenizer, Token.Name.Builtin, '{')
    token, text = tokenizer.next_token()
    if token is Token.Text:
        result = text
    else:
        LOGGER.error('Expecting environment name \\begin or \\end.')
        raise InvalidLatexCode('Expecting environment name between { and }')
    _expect_token(tokenizer, Token.Name.Builtin, '}')
    return result

def _expect_token(tokenizer, expected_token, expected_text):
    token, text = tokenizer.next_token()
    LOGGER.debug('_expect_token: token - text: %s - %s', token, text)
    if (token is expected_token) and (text == expected_text):
        return
    else:
        raise InvalidLatexCode('Expecting ' + expected_text)

def _read_parameter(tokenizer, token_handler=ignore_token):
    groups = 0
    result = ''
    token, text = tokenizer.next_token()
    while not ((token == Token.Name.Builtin) and (text == '{')):
        token_handler(token, text)
        token, text = tokenizer.next_token()
    while True:
        token, text = tokenizer.next_token()
        if (token is Token.Name.Builtin):
            if ('{' == text):
                result = result + text
                groups = groups + 1
            elif ('}' == text):
                if (groups == 0):
                    LOGGER.debug('_read_parameter(...): ' + result)
                    return result
                else:
                    result = result + text
                    groups = groups - 1
        elif (token is Token.Comment):
            pass
        else:
            result = result + text
            
def _array_index(ch, arr):
    for i in range(0, len(arr)):
        if arr[i] == ch:
            return i
    return -1

def piece_color(ch):
    return _array_index(ch, PIECE_COLORS)

def piece_type(ch):
    return _array_index(ch, PIECE_CHARACTERS)

def piece_rotation(ch):
    return _array_index(ch, PIECE_ROTATIONS) + 1

def column(ch):
    return _array_index(ch, COLUMN_CHARACTERS)

def row(text):
    return int(text) - 1


def write_latex(problem_document, output, problems_only=False):
    '''
    This method is used to write the given list of problems to the given output.
    '''
    if problems_only:
        for index in range(problem_document.get_problem_count()):
            problem = problem_document.get_problem(index)
            output.write('%\n')
            _write_problem(problem, output)
            output.write('%\n%\n')
    else:
        for element in problem_document:
            if isinstance(element, Chessproblem):
                _write_problem(element, output)
            elif isinstance(element, str) or isinstance(element, unicode):
                output.write(element)

def _write_after_command_text(problem, member_name, output, anyway):
    if member_name in problem.after_command_text.keys():
        output.write(problem.after_command_text[member_name])
    elif anyway:
        output.write('%\n')


def _write_simple_member(problem, member_name, output):
    value = getattr(problem, member_name)
    if value != None:
        output.write('\\')
        output.write(member_name)
        output.write('{')
        try:
            output.write(value)
        except UnicodeEncodeError as e:
            LOGGER.error('_write_simple_member(' + member_name + ', ' + value + ')')
            raise e
        output.write('}')
    _write_after_command_text(problem, member_name, output, value != None)

def _write_problem(problem, output):
    '''
    This method is used to write a single chessproblem to the given output.
    '''
    if problem.board.rows == 8 and problem.board.columns == 8:
        output.write('\\begin{diagram}')
    else:
        output.write('\\begin{diagram}[')
        output.write(str(problem.board.columns))
        output.write('x')
        output.write(str(problem.board.rows))
        output.write(']')
    _write_after_command_text(problem, '{diagram}', output, False)
    _write_simple_member(problem, 'specialdiagnum', output)
    _write_array_member(problem, output, 'authors', 'author', _latex_author_str)
    _write_array_member(problem, output, 'cities', 'city')
    _write_pieces(problem, output)
    _write_simple_member(problem, 'dedication', output)
    _write_simple_member(problem, 'after', output)
    _write_simple_member(problem, 'stipulation', output)
    _write_array_member(problem, output, 'condition')
    _write_array_member(problem, output, 'twins')
    _write_simple_member(problem, 'version', output)
    _write_simple_member(problem, 'remark', output)
    _write_array_member(problem, output, 'piecedefs', member_tostr=_piecedef_tostr)
    _write_simple_member(problem, 'solution', output)
    _write_array_member(problem, output, 'themes')
    _write_simple_member(problem, 'comment', output)
    _write_simple_member(problem, 'sourcenr', output)
    _write_simple_member(problem, 'source', output)
    _write_simple_member(problem, 'issue', output)
    _write_simple_member(problem, 'pages', output)
    _write_simple_member(problem, 'day', output)
    if problem.month != None:
        if problem.month.find('-') == -1:
            output.write('\\month{' + problem.month + '}\n')
        else:
            output.write('\\months{' + problem.month + '}\n')
    _write_simple_member(problem, 'year', output)
    _write_simple_member(problem, 'tournament', output)
    _write_simple_member(problem, 'award', output)
    _write_nofields(problem, output)
    _write_fieldframe(problem, output)
    _write_simple_member(problem, 'gridlines', output)
    _write_simple_member(problem, 'fieldtext', output)
    _write_boolean_member(problem, 'verticalcylinder', output)
    _write_boolean_member(problem, 'horizontalcylinder', output)
    _write_boolean_member(problem, 'gridchess', output)
    _write_boolean_member(problem, 'noframe', output)
    _write_boolean_member(problem, 'allwhite', output)
    _write_boolean_member(problem, 'switchcolors', output)
    output.write('\\end{diagram}')

def _latex_author_str(author):
    return str(author.lastname) + ', ' + str(author.firstname)

def _write_boolean_member(problem, member_name, output):
    value = getattr(problem, member_name)
    if value:
        output.write('\\')
        output.write(member_name)
    _write_after_command_text(problem, member_name, output, value)

def _write_array_member(problem, output, member_name, latex_command=None, member_tostr=None):
    if latex_command == None:
        latex_command = member_name
    array = getattr(problem, member_name)
    if len(array) > 0:
        output.write('\\')
        output.write(latex_command)
        output.write('{')
        first = True
        for value in array:
            if first:
                first = False
            else:
                output.write('; ')
            if member_tostr == None:
                try:
                    output.write(str(value))
                except UnicodeEncodeError as e:
                    LOGGER.error('_write_array_member(' + member_name + ', ' + value + ')')
                    raise e
            else:
                output.write(member_tostr(value))
        output.write('}')
    _write_after_command_text(problem, member_name, output, len(array) > 0)

def _has_pieces(board):
    for row in range(board.rows):
        for column in range(board.columns):
            if board.fields[row][column].get_piece() != None:
                return True
    return False

PIECE_TYPE_OUTPUT_ORDER = [
        model.PIECE_TYPE_KING,
        model.PIECE_TYPE_QUEEN,
        model.PIECE_TYPE_ROOK,
        model.PIECE_TYPE_BISHOP,
        model.PIECE_TYPE_KNIGHT,
        model.PIECE_TYPE_PAWN,
        model.PIECE_TYPE_EQUIHOPPER,
        model.PIECE_TYPE_CIRCLE]

def _write_pieces(problem, output):
    board = problem.board
    has_pieces = _has_pieces(board)
    if has_pieces:
        output.write('\\pieces')
        if problem.pieces_control != None:
            output.write('[')
            output.write(str(problem.pieces_control.count_white))
            output.write('+')
            output.write(str(problem.pieces_control.count_black))
            if problem.pieces_control.count_neutral > 0:
                output.write('+')
                output.write(str(problem.pieces_control.count_neutral))
            output.write(']')
        output.write('{')
        _first_list = True
        for piece_color in range(PIECE_COLOR_COUNT):
            for piece_rotation in range(PIECE_ROTATION_COUNT):
                for piece_type in PIECE_TYPE_OUTPUT_ORDER:
                    _first_in_list = True
                    for row in range(board.rows):
                        for column in range(board.columns):
                            piece = board.fields[row][column].get_piece()
                            if (piece != None
                                and piece.piece_color == piece_color
                                and piece.piece_rotation == piece_rotation
                                and piece.piece_type == piece_type):
                                if _first_list:
                                    _first_list = False
                                elif _first_in_list:
                                    output.write(', ')
                                if _first_in_list:
                                    _first_in_list = False
                                    output.write(PIECE_COLORS[piece_color])
                                    output.write(PIECE_CHARACTERS[piece_type])
                                    if piece_rotation != PIECE_ROTATION_NORMAL:
                                        output.write(PIECE_ROTATIONS[piece_rotation - 1])
                                _write_field_coordinate(output, column, row)
        output.write('}')
    _write_after_command_text(problem, 'pieces', output, has_pieces)

def _write_field_coordinate(output, column, row):
    output.write(COLUMN_CHARACTERS[column])
    if row + 1 < 10:
        output.write(str(row + 1))
    else:
        output.write('{' + str(row + 1) + '}')

def _has_frame_check(field):
    return field.has_frame()

def _write_fieldframe(problem, output):
    _write_special(problem, output, 'fieldframe', _has_frame_check)

def _has_nofield_check(field):
    return field.is_nofield()

def _write_nofields(problem, output):
    _write_special(problem, output, 'nofields', _has_nofield_check)

def _has_specials(board, special_check):
    for row in range(board.rows):
        for column in range(board.columns):
            field = board.fields[row][column]
            if special_check(field):
                return True
    return False

def _piecedef_tostr(piecedef):
    return '{%s}{%s}{%s}' % (piecedef.colors, piecedef.piece_symbol, piecedef.name)

def _write_special(problem, output, latex_command, special_check):
    board = problem.board
    has_specials = _has_specials(board, special_check)
    if has_specials:
        output.write('\\')
        output.write(latex_command)
        output.write('{')
        _first = True
        for row in range(board.rows):
            for column in range(board.columns):
                field = board.fields[row][column]
                if special_check(field):
                    if _first:
                        _first = False
                    else:
                        output.write(', ')
                    _write_field_coordinate(output, column, row)

        output.write('}')
    _write_after_command_text(problem, 'fieldframe', output, has_specials)
                





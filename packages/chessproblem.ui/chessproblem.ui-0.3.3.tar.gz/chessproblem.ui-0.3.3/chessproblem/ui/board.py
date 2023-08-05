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


import Tkinter as tk

import chessproblem.model as model

from chessproblem.io import piece_type
from chessproblem.io import piece_rotation
from chessproblem.io import row
from chessproblem.io import column

from imageio import ChessImageRegistry

import logging

from chessproblem.config import DEFAULT_CONFIG

LOGGER = logging.getLogger('chessproblem.ui')


EXPECT_PIECE_OR_COLUMN = 0
EXPECT_ROTATION_OR_COLUMN = 1
EXPECT_ROW = 2
EXPECT_ROTATION_OR_COLUMN_OR_ROW = 3

PIECE_ONLY_CHARS = frozenset('ktls')
COLUMN_CHARS = frozenset('abcdefgh')
COLUMN_ONLY_CHARS = frozenset('acefgh')
PIECE_OR_COLUMN_CHARS = frozenset('bd')
ROW_CHARS = frozenset('12345678')
ROTATION_CHARS = frozenset('lru')


IMAGE_PIXEL_SIZE = DEFAULT_CONFIG.image_pixel_size
IMAGE_PIXEL_CENTER_OFFSET = (IMAGE_PIXEL_SIZE / 2)

EMPTY_BLACK_FIELD_INDEX = 144

PIECE_COLOR_OFFSETS = [0, 12, 6]
PIECE_ROTATION_OFFSETS = [0, 36, 72, 108]



def _piece_image_offset(piece):
    return _image_offset(piece.piece_type, piece.piece_color, piece.piece_rotation)

def _image_offset(piece_type, piece_color, piece_rotation):
    return piece_type + PIECE_COLOR_OFFSETS[piece_color] + PIECE_ROTATION_OFFSETS[piece_rotation]


class BoardCanvas(tk.Canvas):
    '''
    This class displays the chessboard.
    '''
    def on_board_change(self, sender, column, row):
        self.draw_field(column, row)

    def _on_click(self, event):
        column = event.x / IMAGE_PIXEL_SIZE
        row = 7 - (event.y / IMAGE_PIXEL_SIZE)
        self.board_edit_state.set_piece_to(self, column, row)

    def __init__(self, master, board, board_edit_state, chess_image_registry):
        tk.Canvas.__init__(self,master,width=IMAGE_PIXEL_SIZE*board.columns,height=IMAGE_PIXEL_SIZE*board.rows)
        self.chess_image_registry = chess_image_registry
        self.set_board(board)
        self.board_edit_state = board_edit_state
        self.board_edit_state.register_board_observer(self.on_board_change)
        self.bind('<Button-1>', self._on_click)

    def set_board(self, board):
        self.board = board
        self.draw_board()

    def draw_board(self):
        LOGGER.debug("BoardCanvas.draw_board")
        for row in range(self.board.rows):
            for column in range(self.board.columns):
                self.draw_field(column,row)

    def _x_y_from_column_row(self,column,row,offset=0):
        x = column * IMAGE_PIXEL_SIZE + offset
        y = (self.board.rows - 1 - row) * IMAGE_PIXEL_SIZE + offset
        return x, y
        
    def _clear_field(self,column,row):
        x, y = self._x_y_from_column_row(column,row)
        self.create_rectangle(x, y, x + IMAGE_PIXEL_SIZE, y + IMAGE_PIXEL_SIZE, fill='white', outline='')

    def draw_field(self,column,row):
        self._clear_field(column,row)
        piece = self.board.fields[row][column]
        if piece == None:
            self.draw_empty(column,row)
        else:
            self.draw_piece(piece,column,row)

    def _is_black_field(self,column,row):
        return (row + column) % 2 == 0

    def draw_piece(self,piece,column,row):
        x, y = self._x_y_from_column_row(column,row,IMAGE_PIXEL_CENTER_OFFSET)
        if self._is_black_field(column,row):
            piece_image_offset = _piece_image_offset(piece) + 18
        else:
            piece_image_offset = _piece_image_offset(piece)
        i = self.chess_image_registry.get_image(piece_image_offset)
        self.create_image(x, y, image=i, anchor=tk.CENTER)

    def draw_empty(self,column,row):
        x, y = self._x_y_from_column_row(column,row)
        if self._is_black_field(column,row):
            i = self.chess_image_registry.get_image(EMPTY_BLACK_FIELD_INDEX)
            self.create_image(x, y, image=i, anchor=tk.NW)


class PieceTypeCanvas(tk.Canvas):
    '''
    This canvas is used to display the different piece types to select one for next input operations.
    '''
    def _draw_image(self, piece_type):
        y = (5 - piece_type) * IMAGE_PIXEL_SIZE
        self.create_rectangle(0, y, IMAGE_PIXEL_SIZE, y + IMAGE_PIXEL_SIZE, fill='white')
        image_offset = _image_offset(piece_type, model.PIECE_COLOR_WHITE, model.PIECE_ROTATION_NORMAL)
        if piece_type == self.board_edit_state.piece_type:
            image_offset += 18
        img = self.chess_image_registry.get_image(image_offset)
        self.create_image(IMAGE_PIXEL_CENTER_OFFSET, y + IMAGE_PIXEL_CENTER_OFFSET, image=img, anchor=tk.CENTER)

    def redraw(self):
        for i in range(6):
            piece_type = 5 - i
            self._draw_image(piece_type)

    def _on_click(self, event):
        piece_type = 5 - (event.y / IMAGE_PIXEL_SIZE)
        self.board_edit_state.set_piece_type(piece_type, self)

    def _create_binding(self):
        self.bind('<Button-1>', self._on_click)

    def on_state_change(self, sender):
        self.redraw()

    def __init__(self, master, chess_image_registry, board_edit_state):
        tk.Canvas.__init__(self, master, width=IMAGE_PIXEL_SIZE, height=6 * IMAGE_PIXEL_SIZE)
        self.chess_image_registry = chess_image_registry
        self.board_edit_state = board_edit_state
        self.board_edit_state.register_state_observer(self.on_state_change)
        self.redraw()
        self._create_binding()


class PieceRotationCanvas(tk.Canvas):
    def redraw(self):
        piece_type = self.board_edit_state.piece_type
        self.create_rectangle(0, 0, IMAGE_PIXEL_SIZE, 4 * IMAGE_PIXEL_SIZE, fill='white')
        for piece_rotation in range(4):
            image_offset = _image_offset(piece_type, model.PIECE_COLOR_WHITE, piece_rotation)
            if piece_rotation == self.board_edit_state.piece_rotation:
                image_offset += 18
            img = self.chess_image_registry.get_image(image_offset)
            self.create_image(IMAGE_PIXEL_CENTER_OFFSET, piece_rotation * IMAGE_PIXEL_SIZE + IMAGE_PIXEL_CENTER_OFFSET, image=img, anchor=tk.CENTER)

    def _on_click(self, event):
        piece_rotation = (event.y / IMAGE_PIXEL_SIZE)
        self.board_edit_state.set_piece_rotation(piece_rotation, self)

    def _create_binding(self):
        self.bind('<Button-1>', self._on_click)

    def on_state_change(self, sender):
        self.redraw()

    def __init__(self, master, chess_image_registry, board_edit_state):
        tk.Canvas.__init__(self, master, width=IMAGE_PIXEL_SIZE, height=4 * IMAGE_PIXEL_SIZE)
        self.chess_image_registry = chess_image_registry
        self.board_edit_state = board_edit_state
        self.board_edit_state.register_state_observer(self.on_state_change)
        self.redraw()
        self._create_binding()



class PieceColorCanvas(tk.Canvas):
    def redraw(self):
        piece_type = self.board_edit_state.piece_type
        piece_rotation = self.board_edit_state.piece_rotation
        self.create_rectangle(0, 0, 3 * IMAGE_PIXEL_SIZE, IMAGE_PIXEL_SIZE, fill='white')
        for piece_color in range(3):
            image_offset = _image_offset(piece_type, piece_color, piece_rotation)
            if piece_color == self.board_edit_state.piece_color:
                image_offset += 18
            img = self.chess_image_registry.get_image(image_offset)
            self.create_image(piece_color * IMAGE_PIXEL_SIZE + IMAGE_PIXEL_CENTER_OFFSET, IMAGE_PIXEL_CENTER_OFFSET, image=img, anchor=tk.CENTER)

    def _on_click(self, event):
        piece_color = (event.x / IMAGE_PIXEL_SIZE)
        self.board_edit_state.set_piece_color(piece_color, self)

    def _create_binding(self):
        self.bind('<Button-1>', self._on_click)

    def on_state_change(self, sender):
        self.redraw()

    def __init__(self, master, chess_image_registry, board_edit_state):
        tk.Canvas.__init__(self, master, width=3 * IMAGE_PIXEL_SIZE, height=IMAGE_PIXEL_SIZE)
        self.chess_image_registry = chess_image_registry
        self.board_edit_state = board_edit_state
        self.board_edit_state.register_state_observer(self.on_state_change)
        self.redraw()
        self._create_binding()


class BoardEditState(object):
    '''
    Used to hold the current edit state of the board.
    '''
    def reset(self):
        self.is_clear_mode = False
        self.piece_color = model.PIECE_COLOR_WHITE
        self.piece_type = model.PIECE_TYPE_KING
        self.piece_rotation = model.PIECE_ROTATION_NORMAL
        self.on_state_change(None)

    def _set_piece_type(self, piece_type):
        self.is_clear_mode = False
        self.piece_type = piece_type
        self.piece_rotation = model.PIECE_ROTATION_NORMAL

    def set_piece_type(self, piece_type, sender=None):
        self._set_piece_type(piece_type)
        if sender != None:
            self.on_state_change(sender)

    def set_piece_type_rotation(self, piece_type, piece_rotation, sender=None):
        self.is_clear_mode = False
        self.piece_type = piece_type
        self.piece_rotation = piece_rotation
        if sender != None:
            self.on_state_change(sender)

    def set_piece_rotation(self, piece_rotation, sender=None):
        self.is_clear_mode = False
        self.piece_rotation = piece_rotation
        if sender != None:
            self.on_state_change(sender)

    def set_piece_color(self, piece_color, sender=None):
        self.is_clear_mode = False
        self.piece_color = piece_color
        if sender != None:
            self.on_state_change(sender)

    def set_board(self, board):
        self.board = board
        self.reset()

    def __init__(self, board):
        self._state_observers = []
        self._board_observers = []
        self.set_board(board)

    def register_state_observer(self, observer):
        self._state_observers.append(observer)

    def register_board_observer(self, observer):
        self._board_observers.append(observer)

    def on_state_change(self, sender):
        for observer in self._state_observers:
            observer(sender)

    def next_color(self, sender):
        self.is_clear_mode = False
        self.piece_color = (self.piece_color + 1) % model.PIECE_COLOR_COUNT
        self.on_state_change(sender)

    def clear_mode(self):
        self.reset()
        self.is_clear_mode = True

    def set_piece_to(self, sender, column, row):
        if self.is_clear_mode:
            self.board.fields[row][column] = None
        else:
            self.board.fields[row][column] = model.Piece(self.piece_color, self.piece_type, self.piece_rotation)
        for observer in self._board_observers:
            observer(sender, column, row)

class BoardEntry(tk.Entry):
    '''
    A specialized Entry instance for fast input of a chessposition to produce LaTeX chess diagrams.
    '''
    def _on_row_char(self, rowchar):
        _value = self.value.get()
        _columnchar = _value[len(_value)-1]
        _column = column(_columnchar)
        _row = row(rowchar)
        self.board_edit_state.set_piece_to(self,_column,_row)
        self.value.set('')
        self.state = EXPECT_PIECE_OR_COLUMN

    def _on_rotation_char(self, rotationchar):
        _piece_type = piece_type(self.value.get().upper())
        _piece_rotation = piece_rotation(rotationchar.upper())
        self.board_edit_state.set_piece_type_rotation(_piece_type, _piece_rotation, self)
        self.value.set('')
        self.state = EXPECT_PIECE_OR_COLUMN

    def _on_column_char(self, columnchar):
        _piece_char = self.value.get()
        _piece_type = piece_type(_piece_char.upper())
        self.board_edit_state.set_piece_type(_piece_type, self)
        self.value.set(columnchar)
        self.state = EXPECT_ROW


    def _on_key(self, event):
        ch = event.char
        if ch == '-':
            self.board_edit_state.clear_mode()
            return 'break'
        elif ch == ' ':
            self.board_edit_state.next_color(self)
            return 'break'
        elif ch.isupper():
            ch = ch.lower()
        if self.state == EXPECT_PIECE_OR_COLUMN:
            if ch in PIECE_ONLY_CHARS:
                self.value.set(ch)
                self.state = EXPECT_ROTATION_OR_COLUMN
            elif ch in COLUMN_ONLY_CHARS:
                self.value.set(ch)
                self.state = EXPECT_ROW
            elif ch in PIECE_OR_COLUMN_CHARS:
                self.value.set(ch)
                self.state = EXPECT_ROTATION_OR_COLUMN_OR_ROW
            else:
                return
        elif self.state == EXPECT_ROTATION_OR_COLUMN_OR_ROW:
            if ch in ROTATION_CHARS:
                self._on_rotation_char(ch)
            elif ch in COLUMN_CHARS:
                self._on_column_char(ch)
            elif ch in ROW_CHARS:
                self._on_row_char(ch)
            else:
                return
        elif self.state == EXPECT_ROW:
            if ch in ROW_CHARS:
                self._on_row_char(ch)
            else:
                return
        elif self.state == EXPECT_ROTATION_OR_COLUMN:
            if ch in ROTATION_CHARS:
                self._on_rotation_char(ch)
            elif ch in COLUMN_CHARS:
                self._on_column_char(ch)
            else:
                return
        return 'break'

    def on_state_change(self, sender):
        LOGGER.debug('BoardEntry.on_state_change - ignored')

    def __init__(self,master,state):
        tk.Entry.__init__(self,master)
        self.board_edit_state = state
        self.board_edit_state.register_state_observer(self.on_state_change)
        self.state = EXPECT_PIECE_OR_COLUMN
        self.value = tk.StringVar()
        self.config(textvariable=self.value)
        self.bind('<Key>', self._on_key)

class BoardFrame(tk.Frame):
    '''
    The layout container for all board (chess position) related ui elements.
    '''
    def __init__(self, master, board):
        tk.Frame.__init__(self, master)
        self.board_edit_state = BoardEditState(board)
        self.chess_image_registry = ChessImageRegistry(self. master)
        self.board_canvas = BoardCanvas(self, board, self.board_edit_state, self.chess_image_registry)
        self.board_canvas.grid(row=0, column=0, rowspan=2)
        self.board_entry = BoardEntry(self, self.board_edit_state)
        self.board_entry.grid(row=2, column=0, pady=8)
        self.piece_type_canvas = PieceTypeCanvas(self, self.chess_image_registry, self.board_edit_state)
        self.piece_type_canvas.grid(row=0, column=1, sticky=tk.NW, padx=IMAGE_PIXEL_CENTER_OFFSET)
        self.piece_rotation_canvas = PieceRotationCanvas(self, self.chess_image_registry, self.board_edit_state)
        self.piece_rotation_canvas.grid(row=0, column=3, sticky=tk.NW, pady=IMAGE_PIXEL_SIZE, padx=IMAGE_PIXEL_CENTER_OFFSET)
        self.piece_color_canvas = PieceColorCanvas(self, self.chess_image_registry, self.board_edit_state)
        self.piece_color_canvas.grid(row=1, column=1, columnspan=3, sticky=tk.S, padx=IMAGE_PIXEL_CENTER_OFFSET)

    def set_board(self, board):
        '''
        Used to switch the display to a different board.
        '''
        self.board_canvas.set_board(board)
        self.board_edit_state.set_board(board)


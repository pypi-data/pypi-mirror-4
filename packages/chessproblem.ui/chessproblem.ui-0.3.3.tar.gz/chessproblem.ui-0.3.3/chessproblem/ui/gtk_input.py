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
This module contains special input elements for our chess problem editor application.
'''

import gtk
import string

from chessproblem.model import PIECE_TYPE_CIRCLE, PIECE_TYPE_EQUIHOPPER

from chessproblem.config import DEFAULT_CONFIG

from image_files import create_chessimage_pixbuf, PIECE_COLOR_OFFSETS, PIECE_ROTATION_OFFSETS

import chessproblem.model as model

import logging
LOGGER = logging.getLogger('chessproblem.ui.gtk_input')

class BoardInputHandler(object):
    def __init__(self, chessproblem, board):
        self._board = board
        self.set_problem(chessproblem)
        self._piece_listeners = []

    def set_problem(self, chessproblem):
        self._chessproblem = chessproblem

    def set_piece(self, piece_color, piece_type, piece_rotation, row, column):
        oldpiece = self._chessproblem.board.fields[row][column].get_piece()
        if piece_type == None:
            newpiece = None
        else:
            newpiece = model.Piece(piece_color, piece_type, piece_rotation)
        self._chessproblem.board.fields[row][column].set_piece(newpiece)
        self._board.queue_draw()
        self._notify_listeners(oldpiece, newpiece)

    def add_piece_listener(self, listener):
        self._piece_listeners.append(listener)

    def _notify_listeners(self, oldpiece, newpiece):
        for listener in self._piece_listeners:
            listener(oldpiece, newpiece)

    def toggle_frame(self, row, column):
        field = self._chessproblem.board.fields[row][column]
        field.toggle_frame()
        self._board.queue_draw()

    def toggle_nofields(self, row, column):
        field = self._chessproblem.board.fields[row][column]
        field.toggle_nofield()
        if field.is_nofield():
            self.set_piece(None, None, None, row, column)
        else:
            self._board.queue_draw()
            

class BoardInputState(object):
    def __init__(self, board_input_handler):
        self.board_input_handler = board_input_handler
        self._piece_color_listeners = []
        self._piece_type_listeners = []
        self._piece_rotation_listeners = []
        self.reset()

    def reset(self):
        self._piece_color = model.PIECE_COLOR_WHITE
        self._piece_type = model.PIECE_TYPE_KING
        self._piece_rotation = model.PIECE_ROTATION_NORMAL
        self.mode_setpiece()

    def field_action(self, row, column):
        self._field_action(row, column)

    def set_current_piece_to(self, row, column):
        self.board_input_handler.set_piece(self._piece_color, self._piece_type, self._piece_rotation, row, column)

    def next_color(self):
        if self._field_action == self.set_current_piece_to:
            self._piece_color = (self._piece_color + 1) % model.PIECE_COLOR_COUNT
            self._on_piece_color_changed()
        else:
            self.reset()

    def set_piece_color(self, piece_color):
        if self._field_action != self.set_current_piece_to:
            self.reset()
        self._piece_color = piece_color
        self._on_piece_color_changed()

    def set_piece_type(self, piece_type):
        if self._field_action != self.set_current_piece_to:
            self.reset()
        self._piece_type = piece_type
        self._piece_rotation = model.PIECE_ROTATION_NORMAL
        self._on_piece_type_changed()
        self._on_piece_rotation_changed()
        self.mode_setpiece()

    def set_piece_rotation(self, piece_rotation):
        if self._field_action != self.set_current_piece_to:
            self.reset()
        if self._piece_type != model.PIECE_TYPE_CIRCLE:
            self._piece_rotation = piece_rotation
            self._on_piece_rotation_changed()

    def _on_piece_color_changed(self):
        for listener in self._piece_color_listeners:
            listener(self._piece_color)

    def _on_piece_type_changed(self):
        for listener in self._piece_type_listeners:
            listener(self._piece_type)

    def _on_piece_rotation_changed(self):
        for listener in self._piece_rotation_listeners:
            listener(self._piece_rotation)

    def add_piece_color_listener(self, listener):
        self._piece_color_listeners.append(listener)

    def add_piece_type_listener(self, listener):
        self._piece_type_listeners.append(listener)

    def add_piece_rotation_listener(self, listener):
        self._piece_rotation_listeners.append(listener)

    def mode_setpiece(self):
        self._field_action = self.set_current_piece_to

    def toggle_frame(self, row, column):
        self.board_input_handler.toggle_frame(row, column)

    def mode_fieldframe(self):
        self._field_action = self.toggle_frame
        self._mode_special()

    def _mode_special(self):
        self._piece_type = None
        self._piece_color = None
        self._piece_rotation = None
        self._on_piece_type_changed()
        self._on_piece_color_changed()
        self._on_piece_rotation_changed()

    def toggle_nofields(self, row, column):
        self.board_input_handler.toggle_nofields(row, column)

    def mode_nofields(self):
        self._field_action = self.toggle_nofields
        self._mode_special()

VALID_INPUT_CHARS='abcdefghktlrsu12345678- '

PIECE_TYPE_OFFSETS='bsltdkec'

class FastBoardEntry(gtk.Entry):
    '''
    A special entry field to allow fast input of a position.
    '''
    
    def __init__(self, board_input_state):
        gtk.Entry.__init__(self)
        self.board_input_state = board_input_state
        self.set_editable(False)
        self.set_width_chars(5)
        self.reset()
        self.connect('key_release_event', self.on_key)
        self.show()

    def on_key(self, widget, event, callback_data=None):
        '''
        Handles any keyboard input inside this widget.
        '''
        keyval = event.keyval
        if keyval >= 0 and keyval <= 255:
            ch = chr(keyval)
            if ch in string.ascii_uppercase:
                ch = chr(keyval - ord('A') + ord('a'))
            if ch in VALID_INPUT_CHARS:
                self.handle_char(ch)

    def handle_char(self, ch):
        if ch == ' ':
            self.board_input_state.next_color()
        elif self.input_state == 0:
            if ch == '-':
                LOGGER.debug('"-" -> set piece_type to None')
                self.set_text(ch)
                self.board_input_state.set_piece_type(None)
            elif ch in 'ktls':
                self.input_state = 1
                self.set_text(ch)
                piece_type = string.find(PIECE_TYPE_OFFSETS, ch)
                self.board_input_state.set_piece_type(piece_type)
            elif ch in 'bcde':
                self.input_state = 2
                self.set_text(ch)
            elif ch in 'afgh':
                self.input_state = 3
                self.set_text(ch)
        elif self.input_state == 1:
            if ch in 'lru':
                self._handle_rotation_char(ch)
            elif ch in 'abcdefgh':
                self._handle_column_char(ch)
        elif self.input_state == 2:
            if ch in 'lru':
                piece_char = self.get_text()[-1]
                piece_type = string.find(PIECE_TYPE_OFFSETS, piece_char)
                self.board_input_state.set_piece_type(piece_type)
                if piece_type == PIECE_TYPE_EQUIHOPPER:
                    # Due to the image of only a left turned equihopper is supported
                    if ch in 'lr':
                        self._handle_rotation_char('l')
                elif piece_type != PIECE_TYPE_CIRCLE:
                    # A circle has the same image for all rotations.
                    self._handle_rotation_char(ch)
            elif ch in 'abcdefgh':
                piece_char = self.get_text()[-1]
                piece_type = string.find(PIECE_TYPE_OFFSETS, piece_char)
                self.board_input_state.set_piece_type(piece_type)
                self._append_text(ch)
                self.input_state = 3
            else:
                self._handle_row_char(ch)
        elif self.input_state == 3:
            self._handle_row_char(ch)

    def _handle_column_char(self, ch):
        self._append_text(ch)
        self.input_state = 3

    def _handle_rotation_char(self, ch):
        piece_rotation = string.index('lru', ch) + 1
        self.board_input_state.set_piece_rotation(piece_rotation)
        self._append_text(ch)
        self.input_state = 0

    def _handle_row_char(self, ch):
        if ch in '12345678':
            column_char = self.get_text()[-1]
            column = string.index('abcdefgh', column_char)
            row = string.index('12345678', ch)
            self.board_input_state.field_action(row, column)
            self.set_text('')
            self.input_state = 0

    def _append_text(self, ch):
        text = self.get_text()
        text = text + ch
        self.set_text(text)


    def reset(self):
        self.input_state = 0
        self.set_text('')

class ChessImageSelector(gtk.DrawingArea):
    '''
    This special drawingarea is used to serve as a general selector for chess images.
    '''

    def __init__(self, image_indexes, selected=0, horizontal=True):
        '''
        '''
        gtk.DrawingArea.__init__(self)
        self._listener = None
        self._image_indexes = image_indexes
        self._current_selected = selected
        self._horizontal = horizontal
        if self._horizontal:
            self.set_size_request(len(image_indexes) * DEFAULT_CONFIG.image_pixel_size, DEFAULT_CONFIG.image_pixel_size)
        else:
            self.set_size_request(DEFAULT_CONFIG.image_pixel_size, len(image_indexes) * DEFAULT_CONFIG.image_pixel_size)
        self.connect('expose-event', self.on_expose_event)
        self.connect('button-release-event', self._on_button_release)
        # There seems to be a bug, so that we need to specify the button masks.
        self.set_events(gtk.gdk.EXPOSURE_MASK
                | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK )
        self.show()

    def set_selected_index(self, index):
        self._current_selected = index
        self.queue_draw()

    def set_image_indexes(self, image_indexes):
        self._image_indexes = image_indexes
        self.queue_draw()

    def on_expose_event(self, widget, event):
        '''
        Is registered to handle the expose event (which means redraw a specific region).
        In our case we just redraw all selection images.
        '''
        self._draw_image_selection()

    def _draw_image_selection(self):
        if self._horizontal:
            self.window.draw_rectangle(self.get_style().white_gc, True, 0, 0, len(self._image_indexes) * DEFAULT_CONFIG.image_pixel_size, DEFAULT_CONFIG.image_pixel_size)
        else:
            self.window.draw_rectangle(self.get_style().white_gc, True, 0, 0, DEFAULT_CONFIG.image_pixel_size, len(self._image_indexes) * DEFAULT_CONFIG.image_pixel_size)
        for i in range(len(self._image_indexes)):
            if i == self._current_selected:
                # for current selected we use the image on a black field
                image_index = self._image_indexes[i] + 18
            else:
                image_index = self._image_indexes[i]
            pixbuf = create_chessimage_pixbuf(image_index)
            (x, y) = self._x_y_from_index(i)
            if pixbuf.get_width() < DEFAULT_CONFIG.image_pixel_size:
                x = x + ((DEFAULT_CONFIG.image_pixel_size - pixbuf.get_width()) / 2)
            if pixbuf.get_height() < DEFAULT_CONFIG.image_pixel_size:
                y = y + ((DEFAULT_CONFIG.image_pixel_size - pixbuf.get_height()) / 2)
            LOGGER.debug('drawing image (%d) to (x, y): (%d, %d)' % (image_index, x, y))
            self.window.draw_pixbuf(self.get_style().white_gc, pixbuf, 0, 0, x, y, width=pixbuf.get_width(), height=pixbuf.get_height())

    def _x_y_from_index(self, index):
        if self._horizontal:
            x = index * DEFAULT_CONFIG.image_pixel_size
            y = 0
        else:
            x = 0
            y = index * DEFAULT_CONFIG.image_pixel_size
        return (x, y)

    def set_selection_listener(self, listener):
        self._listener = listener

    def _on_button_release(self, widget, event, data=None):
        if self._horizontal:
            selected_image_index = int(event.x) / DEFAULT_CONFIG.image_pixel_size
        else:
            selected_image_index = int(event.y) / DEFAULT_CONFIG.image_pixel_size
        if self._listener != None:
            self._listener(selected_image_index)

class SpecialFieldSelector(gtk.DrawingArea):
    '''
    This special drawingarea should be drived to display special field buttons.
    '''
    def __init__(self):
        '''
        '''
        gtk.DrawingArea.__init__(self)
        self._listener = None
        self.set_size_request(DEFAULT_CONFIG.image_pixel_size, DEFAULT_CONFIG.image_pixel_size)
        self.connect('expose-event', self.on_expose_event)
        self.connect('button-release-event', self._on_button_release)
        # There seems to be a bug, so that we need to specify the button masks.
        self.set_events(gtk.gdk.EXPOSURE_MASK
                | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK )

    def on_expose_event(self, widget, event):
        '''
        Is registered to handle the expose event (which means redraw a specific region).
        In our case we just redraw the empty field.
        '''
        self._draw()

    def set_listener(self, listener):
        '''
        This listener is fired when the image is clicked.
        '''
        self._listener = listener

    def _on_button_release(self, widget, event, data=None):
        '''
        This method is called, when the image is clicked.
        We just fire the listener, if one is registered.
        '''
        if self._listener != None:
            self._listener()

    def _draw(self):
        '''
        This method is used to display the visible area of this special selector.
        Derived classes should implement displaying some useful stuff.
        '''
        pass

class ClearFieldSelector(SpecialFieldSelector):
    '''
    This special drawingarea is used to display an empty field - half white and half black - to be able to remove pieces from the board.
    '''
    def __init__(self):
        SpecialFieldSelector.__init__(self)

    def _draw(self):
        self.window.draw_rectangle(self.get_style().white_gc, True, 0, 0, DEFAULT_CONFIG.image_pixel_size, DEFAULT_CONFIG.image_pixel_size)
        pixbuf = create_chessimage_pixbuf(144)
        self.window.draw_pixbuf(self.get_style().white_gc, pixbuf, 0, 0, DEFAULT_CONFIG.image_pixel_size / 2, 0, width=DEFAULT_CONFIG.image_pixel_size / 2, height=DEFAULT_CONFIG.image_pixel_size / 2)
        self.window.draw_pixbuf(self.get_style().white_gc, pixbuf, 0, 0, 0, DEFAULT_CONFIG.image_pixel_size / 2, width=DEFAULT_CONFIG.image_pixel_size / 2, height=DEFAULT_CONFIG.image_pixel_size / 2)


class FieldframeSelector(SpecialFieldSelector):
    '''
    This special drawingarea is used to display enter field frames.
    '''
    def __init__(self):
        SpecialFieldSelector.__init__(self)

    def _draw(self):
        '''
        This _draw method draws a black field with a frame around and some of the black and white fields around it.
        '''
        self.window.draw_rectangle(self.get_style().white_gc, True, 0, 0, DEFAULT_CONFIG.image_pixel_size, DEFAULT_CONFIG.image_pixel_size)
        pixbuf = create_chessimage_pixbuf(144)
        _pos0 = 0
        _pos1 = DEFAULT_CONFIG.image_pixel_size / 4
        _pos2 = DEFAULT_CONFIG.image_pixel_size / 2
        _pos3 = DEFAULT_CONFIG.image_pixel_size / 2 + DEFAULT_CONFIG.image_pixel_size / 4
        _pos4 = DEFAULT_CONFIG.image_pixel_size
        self.window.draw_pixbuf(self.get_style().white_gc, pixbuf, 0, 0, _pos0, _pos0, width=_pos1, height=_pos1)
        self.window.draw_pixbuf(self.get_style().white_gc, pixbuf, 0, 0, _pos0, _pos3, width=_pos1, height=_pos1)
        self.window.draw_pixbuf(self.get_style().white_gc, pixbuf, 0, 0, _pos3, _pos0, width=_pos1, height=_pos1)
        self.window.draw_pixbuf(self.get_style().white_gc, pixbuf, 0, 0, _pos3, _pos3, width=_pos1, height=_pos1)
        self.window.draw_pixbuf(self.get_style().white_gc, pixbuf, 0, 0, _pos1, _pos1, width=_pos2, height=_pos2)
        self.window.draw_rectangle(self.get_style().black_gc, False, _pos1, _pos1, _pos2, _pos2)

class NoFieldSelector(SpecialFieldSelector):
    '''
    This special drawingarea is used to display enter field frames.
    '''
    def __init__(self):
        SpecialFieldSelector.__init__(self)

    def _draw(self):
        '''
        This _draw method draws a black field with a frame around and some of the black and white fields around it.
        '''
        self.window.draw_rectangle(self.get_style().white_gc, True, 0, 0, DEFAULT_CONFIG.image_pixel_size, DEFAULT_CONFIG.image_pixel_size)
        pixbuf = create_chessimage_pixbuf(144)
        _pos0 = 0
        _pos1 = DEFAULT_CONFIG.image_pixel_size / 4
        _pos3 = DEFAULT_CONFIG.image_pixel_size / 2 + DEFAULT_CONFIG.image_pixel_size / 4
        _pos4 = DEFAULT_CONFIG.image_pixel_size
        self.window.draw_pixbuf(self.get_style().white_gc, pixbuf, 0, 0, _pos0, _pos0, width=_pos1, height=_pos1)
        self.window.draw_pixbuf(self.get_style().white_gc, pixbuf, 0, 0, _pos0, _pos3, width=_pos1, height=_pos1)
        self.window.draw_pixbuf(self.get_style().white_gc, pixbuf, 0, 0, _pos3, _pos0, width=_pos1, height=_pos1)
        self.window.draw_pixbuf(self.get_style().white_gc, pixbuf, 0, 0, _pos3, _pos3, width=_pos1, height=_pos1)


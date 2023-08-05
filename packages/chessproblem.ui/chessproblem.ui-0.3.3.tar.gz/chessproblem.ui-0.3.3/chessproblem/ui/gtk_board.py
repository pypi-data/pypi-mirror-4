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
This module contains the following classes:
-   Board:
        displays a chess board
-   RowLegend:
        displays the row legend of a board (the numbers of the rows)
-   ColumnLegend:
        displays the column legend of a board (characters below the columns)
-   BoardSizeDialog: 
        used to change board size (for larger and smaller fairy boards)
-   PieceCountPanel:
        used to display the number of pieces within the statusbar
'''

import gtk
import pango
from gtk.gdk import pixmap_create_from_xpm


from chessproblem.config import DEFAULT_CONFIG

from image_files import image_offset, create_chessimage_pixbuf, PIECE_COLOR_OFFSETS, PIECE_TYPE_OFFSETS, PIECE_ROTATION_OFFSETS

import logging
LOGGER = logging.getLogger('chessproblem.ui.gtk_board')

EMPTY_BLACK_FIELD_INDEX = 144

BOARD_BORDER_WIDTH = 6

from chessproblem.model import PIECE_COLOR_WHITE, PIECE_COLOR_BLACK, PIECE_COLOR_NEUTRAL

def _piece_image_offset(piece):
    '''
    Calculates the image offset for the given piece.
    '''
    return image_offset(piece.piece_type, piece.piece_color, piece.piece_rotation)

class Board(gtk.DrawingArea):
    '''
    A window used to display a chess board.
    '''
    def __init__(self, chessproblem):
        '''
        '''
        gtk.DrawingArea.__init__(self)
        self._listener = None
        self.image_pixel_size = DEFAULT_CONFIG.image_pixel_size
        self.show()
        self.connect('expose-event', self.on_expose_event)
        self.connect('button-release-event', self._on_button_release)
        # There seems to be a bug, so that we need to specify the button masks.
        self.set_events(gtk.gdk.EXPOSURE_MASK
                | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK )
        self.set_chessproblem(chessproblem)

    def set_chessproblem(self, chessproblem):
        '''
        Registers the given chessproblem and calculates the size of the visual chess board.
        '''
        self.chessproblem = chessproblem
        self.board_pixel_width = self.chessproblem.board.columns * self.image_pixel_size + 2 * BOARD_BORDER_WIDTH
        self.board_pixel_height = self.chessproblem.board.rows * self.image_pixel_size + 2 * BOARD_BORDER_WIDTH
        LOGGER.debug('set_chessproblem(...) - (columns, rows, width, height): (%d, %d, %d, %d)' % (self.chessproblem.board.columns, self.chessproblem.board.rows, self.board_pixel_width, self.board_pixel_height))
        self.set_size_request(self.board_pixel_width, self.board_pixel_height)
        self.queue_draw()

    def on_expose_event(self, area, event):
        '''
        Is registered to handle the expose event (which means redraw a specific region).
        In our case we just redraw the complete board.
        '''
        self.draw_board()

    def draw_board(self):
        '''
        Redraw the complete chessboard.
        '''
        self.window.draw_rectangle(self.get_style().white_gc, True, 0, 0, self.board_pixel_width, self.board_pixel_height)
        self._draw_border()
        for row in range(self.chessproblem.board.rows):
            for column in range(self.chessproblem.board.columns):
                self.draw_field(row, column)
        self._draw_field_borders()
        self._draw_grid()

    def _draw_border(self):
        '''
        Draws an outer and an inner boarder around the board.
        Parts or the complete inner boarder may be left out, when horizontalzylinder, verticalcylinder or noframe is used.
        '''
        self.window.draw_rectangle(self.get_style().black_gc, False, 0, 0, self.board_pixel_width - 1, self.board_pixel_height - 1)
        if not self.chessproblem.noframe:
            if not self.chessproblem.horizontalcylinder:
                self.window.draw_line(self.get_style().black_gc, BOARD_BORDER_WIDTH - 1, BOARD_BORDER_WIDTH - 1, self.board_pixel_width - BOARD_BORDER_WIDTH + 1, BOARD_BORDER_WIDTH - 1)
                self.window.draw_line(self.get_style().black_gc, (BOARD_BORDER_WIDTH - 1), self.board_pixel_height - (BOARD_BORDER_WIDTH - 1), self.board_pixel_width - (BOARD_BORDER_WIDTH - 1), self.board_pixel_height - (BOARD_BORDER_WIDTH - 1))
            if not self.chessproblem.verticalcylinder:
                self.window.draw_line(self.get_style().black_gc, (BOARD_BORDER_WIDTH - 1), (BOARD_BORDER_WIDTH - 1), (BOARD_BORDER_WIDTH - 1), self.board_pixel_height - (BOARD_BORDER_WIDTH - 1))
                self.window.draw_line(self.get_style().black_gc, self.board_pixel_width - (BOARD_BORDER_WIDTH - 1), (BOARD_BORDER_WIDTH - 1), self.board_pixel_width - (BOARD_BORDER_WIDTH - 1), self.board_pixel_height - (BOARD_BORDER_WIDTH - 1))

    def _draw_grid(self):
        '''
        Draws lines for a gridchess board.
        '''
        if self.chessproblem.gridchess:
            for gridline in range(3):
                self.window.draw_line(self.get_style().black_gc,
                        BOARD_BORDER_WIDTH + (self.image_pixel_size * ((2 * gridline) + 2)), BOARD_BORDER_WIDTH,
                        BOARD_BORDER_WIDTH + (self.image_pixel_size * ((2 * gridline) + 2)), self.board_pixel_height - BOARD_BORDER_WIDTH)
                self.window.draw_line(self.get_style().black_gc,
                        BOARD_BORDER_WIDTH, BOARD_BORDER_WIDTH + (self.image_pixel_size * ((2 * gridline) + 2)),
                        self.board_pixel_width - BOARD_BORDER_WIDTH, BOARD_BORDER_WIDTH + (self.image_pixel_size * ((2 * gridline) + 2)))

    def _draw_field_borders(self):
        '''
        In case of an 'allwhite' problem, draws dotted lines between fields.
        '''
        if self.chessproblem.allwhite:
            gc = self.window.new_gc()
            gc.line_style = gtk.gdk.LINE_ON_OFF_DASH

            for border in range(self.chessproblem.board.columns - 1):
                self.window.draw_line(gc,
                        BOARD_BORDER_WIDTH + (self.image_pixel_size * (border+1)), BOARD_BORDER_WIDTH,
                        BOARD_BORDER_WIDTH + (self.image_pixel_size * (border+1)), self.board_pixel_height - BOARD_BORDER_WIDTH)
                self.window.draw_line(gc,
                        BOARD_BORDER_WIDTH, BOARD_BORDER_WIDTH + (self.image_pixel_size * (border+1)),
                        self.board_pixel_height - BOARD_BORDER_WIDTH, BOARD_BORDER_WIDTH + (self.image_pixel_size * (border+1)))


    def draw_field(self, row, column):
        '''
        Redraw a single field on the chessboard.
        The coordinates of the chessboard are given as row and column.
        Both values are 0 based.
        '''
        self._clear_field(row, column)
        field = self.chessproblem.board.fields[row][column]
        if not field.is_nofield():
            piece = field.get_piece()
            if piece == None:
                self.draw_empty(row, column)
            else:
                self.draw_piece(piece, row, column)
        if field.has_frame():
            self.draw_field_frame(row, column)

    def draw_piece(self, piece, row, column):
        (x, y) = self._x_y_from_row_column(row, column)
        if self._is_black_field(column,row):
            piece_image_offset = _piece_image_offset(piece) + 18
        else:
            piece_image_offset = _piece_image_offset(piece)
        pixbuf = create_chessimage_pixbuf(piece_image_offset)
        LOGGER.debug('Drawing piece image %d at (row, column) (%d, %d)' % (piece_image_offset, row, column))
        if pixbuf.get_width() < self.image_pixel_size:
            x = x + ((self.image_pixel_size - pixbuf.get_width()) / 2)
        if pixbuf.get_height() < self.image_pixel_size:
            y = y + ((self.image_pixel_size - pixbuf.get_height()) / 2)
        self.window.draw_pixbuf(self.get_style().white_gc, pixbuf, 0, 0, x, y, width=pixbuf.get_width(), height=pixbuf.get_height())

    def draw_empty(self, row, column):
        if self._is_black_field(row, column):
            (x, y) = self._x_y_from_row_column(row, column)
            pixbuf = create_chessimage_pixbuf(144)
            self.window.draw_pixbuf(self.get_style().white_gc, pixbuf, 0, 0, x, y, width=self.image_pixel_size, height=self.image_pixel_size)

    def draw_field_frame(self, row, column):
        rows = self.chessproblem.board.rows
        self.window.draw_line(self.get_style().black_gc,
                BOARD_BORDER_WIDTH + (self.image_pixel_size * column), BOARD_BORDER_WIDTH + (self.image_pixel_size * (rows - row - 1)),
                BOARD_BORDER_WIDTH + (self.image_pixel_size * (column + 1)) - 1, BOARD_BORDER_WIDTH + (self.image_pixel_size * (rows - row - 1)))
        self.window.draw_line(self.get_style().black_gc,
                BOARD_BORDER_WIDTH + (self.image_pixel_size * column), BOARD_BORDER_WIDTH + (self.image_pixel_size * (rows - row)),
                BOARD_BORDER_WIDTH + (self.image_pixel_size * (column + 1)) - 1, BOARD_BORDER_WIDTH + (self.image_pixel_size * (rows - row)))
        self.window.draw_line(self.get_style().black_gc,
                BOARD_BORDER_WIDTH + (self.image_pixel_size * column), BOARD_BORDER_WIDTH + (self.image_pixel_size * (rows - row - 1)),
                BOARD_BORDER_WIDTH + (self.image_pixel_size * column), BOARD_BORDER_WIDTH + (self.image_pixel_size * (rows - row)))
        self.window.draw_line(self.get_style().black_gc,
                BOARD_BORDER_WIDTH + (self.image_pixel_size * (column + 1)) - 1, BOARD_BORDER_WIDTH + (self.image_pixel_size * (rows - row - 1)),
                BOARD_BORDER_WIDTH + (self.image_pixel_size * (column + 1)) - 1, BOARD_BORDER_WIDTH + (self.image_pixel_size * (rows - row)))

    def _clear_field(self, row, column):
        (x, y) = self._x_y_from_row_column(row, column)
        self.window.draw_rectangle(self.get_style().white_gc, True, x, y, self.image_pixel_size, self.image_pixel_size)

    def _is_black_field(self,column,row):
        if self.chessproblem.allwhite:
            return False
        if self.chessproblem.switchcolors:
            return (row + column) % 2 == 1
        else:
            return (row + column) % 2 == 0

    def _x_y_from_row_column(self, row, column):
        x = column * self.image_pixel_size
        y = (self.chessproblem.board.rows - 1 - row) * self.image_pixel_size
        return (x + BOARD_BORDER_WIDTH, y + BOARD_BORDER_WIDTH)

    def set_click_listener(self, listener):
        self._listener = listener

    def _on_button_release(self, widget, event, data=None):
        LOGGER.debug('_on_button_release(...) (x, y): (%d, %d)' % (event.x, event.y))
        if (event.x >= BOARD_BORDER_WIDTH) and (event.y >= BOARD_BORDER_WIDTH):
            row = self.chessproblem.board.rows - 1 - (int(event.y - BOARD_BORDER_WIDTH) / DEFAULT_CONFIG.image_pixel_size)
            column = int(event.x - BOARD_BORDER_WIDTH) / DEFAULT_CONFIG.image_pixel_size
            if self._listener != None:
                self._listener(row, column)

def legend_strategy_always(scrollbar, legend):
    '''
    A strategy for a legend, to make it visible always.
    '''
    legend.show()

def legend_strategy_never(scrollbar, legend):
    '''
    A strategy for a legend, to make it visible never.
    '''
    legend.hide()

def legend_strategy_automatic(scrollbar, legend):
    '''
    A strategy for a legend, to make it visible when the given scrollbar is visible.
    '''
    if scrollbar.get_property('visible'):
        legend.show()
    else:
        legend.hide()

def get_legend_strategy(name):
    if name == 'automatic':
        return legend_strategy_automatic
    elif name == 'never':
        return legend_strategy_never
    else:
        return legend_strategy_always

class RowLegend(gtk.DrawingArea):
    '''
    Used to display the row-legend of a board.
    '''
    def __init__(self, rows):
        '''
        Creates the instances with the given initial number of rows.
        '''
        gtk.DrawingArea.__init__(self)
        self.connect('expose-event', self._on_expose_event)
        self._rows = -1
        self.set_rows(rows)

    def set_rows(self, rows):
        '''
        Change the display to the given number of rows.
        '''
        if rows != self._rows:
            self._rows = rows
            # We calculate the width depending on the width of the font
            layout = pango.Layout(self.get_pango_context())
            layout.set_text('%d' % 8)
            (width, height) = layout.get_pixel_size() 
            self._character_width = width
            self._width = 3 * self._character_width
            self._height = rows * DEFAULT_CONFIG.image_pixel_size + 2 * BOARD_BORDER_WIDTH + 4
            self.set_size_request(self._width, self._height)
            self.queue_draw()

    def get_width(self):
        '''
        Returns the width of this RowLegend.
        '''
        return self._width

    def get_height(self):
        '''
        Returns the height of this RowLegend.
        '''
        return self._height

    def _on_expose_event(self, area, event):
        '''
        Is registered to be called when this RowLegend needs to be redrawn.
        '''
        self._draw_legend()

    def _draw_legend(self):
        '''
        Draws the row numbers for according to the current 'rows' value.
        '''
        layout = pango.Layout(self.get_pango_context())
        for row in range(self._rows):
            layout.set_text('%2d' % (row + 1))
            self.window.draw_layout(self.get_style().black_gc, 2, self._height - 4 - ((row + 1) * DEFAULT_CONFIG.image_pixel_size), layout)

        
class ColumnLegend(gtk.DrawingArea):
    '''
    Used to display the column-legend of a board.
    '''
    def __init__(self, columns):
        '''
        Creates the instances with the given initial number of columns.
        '''
        gtk.DrawingArea.__init__(self)
        self.connect('expose-event', self._on_expose_event)
        self._columns = -1
        self.set_columns(columns)

    def set_columns(self, columns):
        '''
        Change the display to the given number of columns.
        '''
        if columns != self._columns:
            self._columns = columns
            # We calculate the width depending on the width of the font
            layout = pango.Layout(self.get_pango_context())
            layout.set_text('J')
            (width, height) = layout.get_pixel_size() 
            self._width = columns * DEFAULT_CONFIG.image_pixel_size + 2 * BOARD_BORDER_WIDTH + 4
            self._yoffset = 2
            self._height = height + 4 * self._yoffset
            self._xoffset = (BOARD_BORDER_WIDTH + DEFAULT_CONFIG.image_pixel_size - width) / 2
            self.set_size_request(self._width, self._height)
            self.queue_draw()

    def get_width(self):
        '''
        Returns the width of this ColumnLegend.
        '''
        return self._width

    def get_height(self):
        '''
        Returns the height of this ColumnLegend.
        '''
        return self._height

    def _on_expose_event(self, area, event):
        '''
        Is registered to be called when this ColumnLegend needs to be redrawn.
        '''
        self._draw_legend()

    def _draw_legend(self):
        '''
        Draws the column characters for according to the current 'columns' value.
        '''
        layout = pango.Layout(self.get_pango_context())
        for column in range(self._columns):
            layout.set_text(chr(97 + column))
            self.window.draw_layout(self.get_style().black_gc, self._xoffset + (column * DEFAULT_CONFIG.image_pixel_size), self._yoffset, layout)

        
class BoardSizeDialog(gtk.Dialog):
    '''
    This dialog is used to edit the size of the board.
    '''
    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns
        gtk.Dialog.__init__(self, title='edit board size',
                flags=gtk.DIALOG_MODAL,
                buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self.table = gtk.Table(rows=2, columns=2)
        self.table.show()
        self.get_content_area().pack_start(self.table)
        self.label_rows = gtk.Label('rows')
        self.label_rows.show()
        self.table.attach(self.label_rows, 0, 1, 0, 1)
        self.adjustment_rows = gtk.Adjustment(value = rows, lower=1, upper=26, step_incr=1)
        self.spin_rows = gtk.SpinButton(self.adjustment_rows)
        self.spin_rows.show()
        self.table.attach(self.spin_rows, 1, 2, 0, 1)
        self.label_columns = gtk.Label('columns')
        self.label_columns.show()
        self.table.attach(self.label_columns, 0, 1, 1, 2)
        self.adjustment_columns = gtk.Adjustment(value = columns, lower=1, upper=26, step_incr=1)
        self.spin_columns = gtk.SpinButton(self.adjustment_columns)
        self.spin_columns.show()
        self.table.attach(self.spin_columns, 1, 2, 1, 2)

    def get_rows(self):
        '''
        Returns the selected rows value.
        '''
        return int(self.adjustment_rows.get_value())

    def get_columns(self):
        '''
        Returns the selected columns value.
        '''
        return int(self.adjustment_columns.get_value())

class PieceCountPanel(gtk.HBox):
    '''
    This panel us used to edit the piece counter to verify the board input.
    In addition to the verifying values (control counters), the instances stores the current counters.
    '''
    def __init__(self):
        gtk.HBox.__init__(self, False, 0)
        self._create_adjustment_and_pack_spinbutton('white')
        self._create_adjustment_and_pack_spinbutton('black')
        self._create_adjustment_and_pack_spinbutton('neutral')
        self.current_white = 0
        self.current_black = 0
        self.current_neutral = 0
        self._current_value_change_listeners = []

    def _create_adjustment_and_pack_spinbutton(self, color):
        adjustment = gtk.Adjustment(value = 0, lower=0, upper=99, step_incr=1)
        adjustment.connect('value-changed', self._on_control_value_changed, color)
        spinbutton = gtk.SpinButton(adjustment)
        spinbutton.set_width_chars(2)
        spinbutton.show()
        self.pack_start(spinbutton, False, False, 2)
        setattr(self, 'adjustment_' + color, adjustment)
        setattr(self, 'spinbutton_' + color, spinbutton)

    def adjust_current_value(self, color, adjustment):
        value = getattr(self, 'current_' + color)
        value += adjustment
        setattr(self, 'current_' + color, value)
        self._on_current_value_changed(color)

    def set_current_values(self, white, black, neutral):
        '''
        Set the current piece count values.
        '''
        self.current_white = white
        self.current_black = black
        self.current_neutral = neutral
        self._on_current_values_changed()

    def set_control_counters(self, white, black, neutral):
        '''
        Display the given piece counter values inside the user interface elements.
        '''
        self.adjustment_white.set_value(white)
        self.adjustment_black.set_value(black)
        self.adjustment_neutral.set_value(neutral)

    def get_control_counters(self):
        '''
        Retrieve eht piece counters from the user interface elements.
        '''
        white = int(self.adjustment_white.get_value())
        black = int(self.adjustment_black.get_value())
        neutral = int(self.adjustment_neutral.get_value())
        return (white, black, neutral)

    def _get_control_counter(self, color):
        adjustment = getattr(self, 'adjustment_' + color)
        return int(adjustment.get_value())

    def _get_current_counter(self, color):
        return getattr(self, 'current_' + color)

    def _notify_listeners(self):
        for listener in self._current_value_change_listeners:
            listener(self.current_white, self.current_black, self.current_neutral)

    def _on_current_values_changed(self):
        '''
        Will be called, current piece counters change.
        '''
        for color in ['white', 'black', 'neutral']:
            self._on_current_value_changed(color, False)
        self._notify_listeners()

    def _on_control_value_changed(self, widget, color):
        self._adjust_color(color)

    def _on_current_value_changed(self, color, notify_listeners=True):
        '''
        '''
        self._adjust_color(color)
        if notify_listeners:
            self._notify_listeners()

    def add_current_listener(self, listener):
        self._current_value_change_listeners.append(listener)

    def piece_listener(self, oldpiece, newpiece):
        if oldpiece != None:
            if oldpiece.piece_color == PIECE_COLOR_WHITE:
                self.adjust_current_value('white', -1)
            elif oldpiece.piece_color == PIECE_COLOR_BLACK:
                self.adjust_current_value('black', -1)
            elif oldpiece.piece_color == PIECE_COLOR_NEUTRAL:
                self.adjust_current_value('neutral', -1)
        if newpiece != None:
            if newpiece.piece_color == PIECE_COLOR_WHITE:
                self.adjust_current_value('white', 1)
            elif newpiece.piece_color == PIECE_COLOR_BLACK:
                self.adjust_current_value('black', 1)
            elif newpiece.piece_color == PIECE_COLOR_NEUTRAL:
                self.adjust_current_value('neutral', 1)


    def _adjust_color(self, color):
        '''
        '''
        LOGGER.debug('PieceCountPanel._adjust_color(' + color + ')')
        spinbutton = getattr(self, 'spinbutton_' + color)
        if self._get_control_counter(color) == self._get_current_counter(color):
            spinbutton.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('black'))
        else:
            spinbutton.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('red'))


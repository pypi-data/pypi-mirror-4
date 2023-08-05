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
This module contains the gtk implementation classes of the ChessProblemEditor.
'''
import pygtk
pygtk.require("2.0")
import gtk, gtk.gdk
import pango
import sys

from gtk_model import ChessProblemModel
from gtk_board import Board, ColumnLegend, RowLegend, get_legend_strategy, BoardSizeDialog, PieceCountPanel
from gtk_display import AuthorsDisplay, InfoArea
from gtk_input import FastBoardEntry, BoardInputState, BoardInputHandler, ChessImageSelector, ClearFieldSelector, FieldframeSelector, NoFieldSelector
from gtk_help import AboutDialog
from chessproblem.io import ChessProblemLatexParser, write_latex

from image_files import PIECE_TYPE_OFFSETS, PIECE_COLOR_OFFSETS, PIECE_ROTATION_OFFSETS

import chessproblem.model as model
import chessproblem.model.db as db

import logging

from chessproblem.config import DEFAULT_CONFIG, CONFIGDIR
from os.path import join
from threading import Thread

LOGGER = logging.getLogger('chessproblem.ui')

WINDOW_WIDTH=800
WINDOW_HEIGHT=600

from chessproblem.tools.latex import DialinesTemplate


class MainFrame(object):
    '''
    The main frame of the ChessProblemEditor application.
    '''
    def __init__(self, filename=None):
        '''
        Initializes the instance.
        If a filename is given, the problems are automatically read from the given file.
        '''
        self.db_service = db.DbService(DEFAULT_CONFIG.database_url)
        #
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('ChessProblemEditor')
        self.window.connect("delete_event", self.on_delete)
        self.window.connect("destroy", self.on_destroy)
        self.window_area = gtk.VBox(False, 0)
        self.window_area.show()
        self.window.add(self.window_area)
        self._create_menu()
        self.model = ChessProblemModel()
        self.model.add_observer(self._on_current_problem_change)
        self.base_area = gtk.HBox(False, 0)
        self.base_area.show()
        self.window_area.pack_start(self.base_area, True, True, 0)
        self._create_display_area()
        self.base_area.pack_start(self.display_area, True, True, 0)
        self._create_edit_area()
        self.base_area.pack_start(self.edit_area, True, True, 0)
        self.window.show()
        if filename == None:
            self.filename = None
            self._on_current_problem_change()
        else:
            self._open_file(filename)

    def show_error(self, message, details):
        '''
        Used to display an error message and its details.
        '''
        dialog = gtk.MessageDialog(flags=gtk.DIALOG_MODAL,
                type=gtk.MESSAGE_ERROR,
                buttons=gtk.BUTTONS_OK,
                message_format=message)
        dialog.set_size_request(500, 500)
        scrolledwindow_details = gtk.ScrolledWindow()
        scrolledwindow_details.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolledwindow_details.show()
        textbuffer_details = gtk.TextBuffer()
        textbuffer_details.set_text(details)
        textview_details = gtk.TextView(textbuffer_details)
        textview_details.show()
        scrolledwindow_details.add(textview_details)
        dialog.get_content_area().pack_start(scrolledwindow_details)
        dialog.run()
        dialog.destroy()


    def _create_display_area(self):
        '''
        This method creates the area (a VBox), which is used to display all problem information.
        '''
        self.display_area = gtk.VBox(False, 0)
        self.display_area.show()
        self.board_area = gtk.Table(rows=3, columns=3, homogeneous=False)
        self.board_area.show()
        self.display_area.pack_start(self.board_area, True, True, 5)
        self.board_display = Board(self.model.current_problem())
        self.board_display.show()
        self.board_display.set_click_listener(self._on_board_clicked)
        self.board_window = gtk.Viewport()
        # self.board_window.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_ALWAYS)
        _SCROLLED_WINDOW_EXTEND = 4
        self.board_window.add(self.board_display)
        self.board_window.set_size_request(
            self.board_display.board_pixel_width + _SCROLLED_WINDOW_EXTEND,
            self.board_display.board_pixel_height + _SCROLLED_WINDOW_EXTEND)
        self.board_window.show()
        self.board_area.attach(self.board_window, 0, 1, 0, 1, xoptions=0, yoptions=0)
        # Scrollbars
        self.row_scrollbar = gtk.VScrollbar(self.board_window.get_vadjustment())
        self.row_scrollbar.set_size_request(-1, self.board_display.board_pixel_width + _SCROLLED_WINDOW_EXTEND)
        # self.row_scrollbar.show()
        self.board_area.attach(self.row_scrollbar, 2, 3, 0, 1, xoptions=0, yoptions=0)
        self.column_scrollbar = gtk.HScrollbar(self.board_window.get_hadjustment())
        self.column_scrollbar.set_size_request(self.board_display.board_pixel_width + _SCROLLED_WINDOW_EXTEND, -1)
        # self.column_scrollbar.show()
        self.board_area.attach(self.column_scrollbar, 0, 1, 2, 3, xoptions=0, yoptions=0)
        # Viewports to display our legend
        self.legend_strategy = get_legend_strategy(DEFAULT_CONFIG.legend_display)
        self.row_legend_viewport = gtk.Viewport(vadjustment=self.board_window.get_vadjustment())
        self.row_legend = RowLegend(8)
        self.row_legend.show()
        self.row_legend_viewport.add(self.row_legend)
        self.row_legend_viewport.set_size_request(self.row_legend.get_width(), self.row_legend.get_height())
        self.row_legend_viewport.show()
        self.board_area.attach(self.row_legend_viewport, 1, 2, 0, 1, xoptions=0, yoptions=0)
        self.column_legend_viewport = gtk.Viewport(hadjustment=self.board_window.get_hadjustment())
        self.column_legend = ColumnLegend(8)
        self.column_legend.show()
        self.column_legend_viewport.add(self.column_legend)
        self.column_legend_viewport.set_size_request(self.column_legend.get_width(), self.column_legend.get_height())
        self.column_legend_viewport.show()
        self.board_area.attach(self.column_legend_viewport, 0, 1, 1, 2, xoptions=0, yoptions=0)
        # Our position input elements
        self.board_input_hbox = gtk.HBox()
        self.board_input_hbox.show()
        self.display_area.pack_start(self.board_input_hbox, False, False, 5)
        self.board_input_label = gtk.Label('position')
        self.board_input_label.show()
        self.board_input_hbox.pack_start(self.board_input_label, False, False, 8)
        self.board_input_handler = BoardInputHandler(self.model.current_problem(), self.board_display)
        self.board_input_state = BoardInputState(self.board_input_handler)
        self.board_fast_input = FastBoardEntry(self.board_input_state)
        self.board_input_hbox.pack_start(self.board_fast_input, False, False, 8)
        self.board_piece_count_panel = PieceCountPanel()
        self.board_piece_count_panel.show()
        self.board_input_hbox.pack_end(self.board_piece_count_panel, False, False, 8)
        self.board_piece_count_panel.add_current_listener(self._on_piece_count_changed)
        self.board_input_handler.add_piece_listener(self.board_piece_count_panel.piece_listener)
        self.board_input_state.add_piece_color_listener(self._on_piece_color_changed)
        self.board_input_state.add_piece_type_listener(self._on_piece_type_changed)
        self.board_input_state.add_piece_rotation_listener(self._on_piece_rotation_changed)
        input_hbox_1 = gtk.HBox()
        input_hbox_1.show()
        self.display_area.pack_start(input_hbox_1, False, False, 5)
        self.piece_color_selector = ChessImageSelector(
                image_indexes=[(PIECE_TYPE_OFFSETS[model.PIECE_TYPE_KING] + PIECE_COLOR_OFFSETS[color]) for color in range(model.PIECE_COLOR_COUNT)], horizontal=True)
        self.piece_color_selector.set_selection_listener(self._on_piece_color_selected)
        input_hbox_1.pack_start(self.piece_color_selector, False, False, 0)

        self.piece_rotation_selector = ChessImageSelector(
                image_indexes=[(PIECE_TYPE_OFFSETS[model.PIECE_TYPE_KING] + PIECE_ROTATION_OFFSETS[piece_rotation]) for piece_rotation in range(model.PIECE_ROTATION_COUNT)], horizontal=True)
        self.piece_rotation_selector.set_selection_listener(self._on_piece_rotation_selected)
        input_hbox_1.pack_end(self.piece_rotation_selector, False, False, 0)

        input_hbox_2 = gtk.HBox()
        input_hbox_2.show()
        self.display_area.pack_start(input_hbox_2, False, False, 5)
        self.piece_type_selector = ChessImageSelector(
                image_indexes=[PIECE_TYPE_OFFSETS[piece_type] for piece_type in range(model.PIECE_TYPE_COUNT)],
                horizontal=True, selected=5)
        self.piece_type_selector.set_selection_listener(self._on_piece_type_selected)
        input_hbox_2.pack_start(self.piece_type_selector, False, False, 0)
        # Another horizontal box for input of empty, framed and missing fields
        input_hbox_3 = gtk.HBox()
        input_hbox_3.show()
        self.display_area.pack_start(input_hbox_3, False, False, 5)
        self.clear_field_selector = ClearFieldSelector()
        self.clear_field_selector.set_listener(self._on_clear_field)
        self.clear_field_selector.show()
        input_hbox_3.pack_start(self.clear_field_selector, False, False, 0)
        self.label_clear_field = gtk.Label('clear (-)')
        self.label_clear_field.show()
        input_hbox_3.pack_start(self.label_clear_field, False, False, 5)
        self.fieldframe_selector = FieldframeSelector()
        self.fieldframe_selector.set_listener(self._on_fieldframe)
        self.fieldframe_selector.show()
        input_hbox_3.pack_start(self.fieldframe_selector, False, False, 5)
        self.label_fieldframe = gtk.Label('fieldframe')
        self.label_fieldframe.show()
        input_hbox_3.pack_start(self.label_fieldframe, False, False, 5)
        self.nofield_selector = NoFieldSelector()
        self.nofield_selector.set_listener(self._on_nofield)
        self.nofield_selector.show()
        input_hbox_3.pack_start(self.nofield_selector, False, False, 5)
        self.label_nofield = gtk.Label('nofield')
        self.label_nofield.show()
        input_hbox_3.pack_start(self.label_nofield, False, False, 5)

    def _on_clear_field(self):
        self.board_input_state.set_piece_type(None)

    def _on_fieldframe(self):
        self.board_input_state.mode_fieldframe()

    def _on_nofield(self):
        self.board_input_state.mode_nofields()

    def _create_display_entry(self, width, tooltiptext=None):
        result = gtk.Entry()
        result.set_size_request(width, -1)
        result.set_editable(False)
        if tooltiptext != None:
            result.set_tooltip_text(tooltiptext)
        result.show()
        return result

    def _create_edit_area(self):
        '''
        This method creates the area (a VBox), which contains the widget to edit the problem information.
        '''
        self.edit_area = gtk.VBox(False, 2)
        # self.edit_area.set_size_request(WINDOW_WIDTH - 10 * DEFAULT_CONFIG.image_pixel_size, -1)
        self.edit_area.show()
        self.info_area = InfoArea(self.db_service)
        self.info_area.show()
        self.info_area.set_visual_change_listener(self._edit_area_visual_change_listener)
        self.edit_area.pack_start(self.info_area, False, False, 0)

    def _edit_area_visual_change_listener(self):
        '''
        Used to handle events e.g. from checkboxes, which should result in a changed board display.
        '''
        self.board_display.draw_board()

    def _on_board_clicked(self, row, column):
        self.board_input_state.field_action(row, column)
        self.board_fast_input.reset()

    def _on_piece_color_selected(self, piece_color):
        self.board_input_state.set_piece_color(piece_color)

    def _on_piece_type_selected(self, piece_type):
        self.board_input_state.set_piece_type(piece_type)

    def _on_piece_rotation_selected(self, piece_rotation):
        self.board_input_state.set_piece_rotation(piece_rotation)

    def _on_piece_color_changed(self, piece_color):
        self.piece_color_selector.set_selected_index(piece_color)

    def _on_piece_type_changed(self, piece_type):
        self.piece_type_selector.set_selected_index(piece_type)

    def _on_piece_rotation_changed(self, piece_rotation):
        self.piece_rotation_selector.set_selected_index(piece_rotation)

    def _on_piece_count_changed(self, white, black, neutral):
        '''
        Called when the number of pieces on the board has changed.
        We need to change the status bar containing a display for this value.
        '''
        if neutral == 0:
            piece_count_value = '(' + str(white) + '+' + str(black) + ')'
        else:
            piece_count_value = '(' + str(white) + '+' + str(black) + '+' + str(neutral) + 'n)'
        self.piece_count_status_bar.remove_message(self.piece_count_context_id, self.piece_count_message_id)
        self.piece_count_status_bar.push(self.piece_count_context_id, piece_count_value)


    def _create_menu(self):
        '''
        Creates our applications main menu.
        '''
        self.menu_bar = gtk.MenuBar()
        accel_group = gtk.AccelGroup()
        self.window.add_accel_group(accel_group)

        # Our file menu
        self.file_menu_item = gtk.MenuItem("File")
        self.file_menu_item.show()
        self.file_menu = gtk.Menu()
        self.file_menu_item.set_submenu(self.file_menu)
        # file menu items
        self.file_new_item = self._add_menu_item_with_accelerator(
                self.file_menu, 'New', self.on_file_new, accel_group, ord('N'), gtk.gdk.CONTROL_MASK)
        self.file_open_item = self._add_menu_item_with_accelerator(
                self.file_menu, 'Open', self.on_file_open, accel_group, ord('O'), gtk.gdk.CONTROL_MASK)
        self.file_save_item = self._add_menu_item_with_accelerator(
                self.file_menu, 'Save', self.on_file_save, accel_group, ord('S'), gtk.gdk.CONTROL_MASK)
        self.file_save_item.set_sensitive(False)
        self.file_save_as_item = self._add_menu_item_with_accelerator(
                self.file_menu, 'Save As', self.on_file_save_as, accel_group, ord('A'), gtk.gdk.CONTROL_MASK)
        sep = gtk.SeparatorMenuItem()
        sep.show()
        self.file_menu.append(sep)
        self.file_exit_item = self._add_menu_item_with_accelerator(
                self.file_menu, 'Exit', self.on_file_exit, accel_group, ord('Q'), gtk.gdk.CONTROL_MASK)
        self.menu_bar.append(self.file_menu_item)

        # Our problems menu
        self.problems_menu_item = gtk.MenuItem("Problems")
        self.problems_menu_item.show()
        self.problems_menu = gtk.Menu()
        self.problems_menu_item.set_submenu(self.problems_menu)
        # problems menu items
        self.problems_first_item = self._add_menu_item_with_accelerator(
                self.problems_menu, 'First', self.on_problems_first, accel_group, 65360)
        self.problems_previous_item = self._add_menu_item_with_accelerator(
                self.problems_menu, 'Previous', self.on_problems_previous, accel_group, 65365)
        self.problems_previous_item.set_sensitive(False)
        self.problems_next_item = self._add_menu_item_with_accelerator(
                self.problems_menu, 'Next', self.on_problems_next, accel_group, 65366)
        self.problems_next_item.set_sensitive(False)
        self.problems_last = self._add_menu_item_with_accelerator(
                self.problems_menu, 'Last', self.on_problems_last, accel_group, 65367)
        sep = gtk.SeparatorMenuItem()
        sep.show()
        self.problems_menu.append(sep)
        self.problems_insert_item = self._add_menu_item_with_accelerator(
                self.problems_menu, 'Insert', self.on_problems_insert, accel_group, 65379, gtk.gdk.SHIFT_MASK)
        self.problems_append_item = self._add_menu_item_with_accelerator(
                self.problems_menu, 'Append', self.on_problems_append, accel_group, 65293, gtk.gdk.SHIFT_MASK)
        self.problems_delete_item = self._add_menu_item_with_accelerator(
                self.problems_menu, 'Delete', self.on_problems_delete, accel_group, 65535, gtk.gdk.SHIFT_MASK)
        self.menu_bar.append(self.problems_menu_item)
        sep = gtk.SeparatorMenuItem()
        sep.show()
        self.problems_menu.append(sep)
        self.problems_change_boardsize_item = self._add_menu_item_with_accelerator(
                self.problems_menu, 'Change board size', self.on_change_boardsize, accel_group, ord('B'), gtk.gdk.CONTROL_MASK)

        self.menu_bar.show()
        # The tools menu
        if len(DEFAULT_CONFIG.compile_menu_actions) > 0:
            self.compile_menu_item = gtk.MenuItem('Compile')
            self.compile_menu_item.show()
            self.compile_menu = gtk.Menu()
            self.compile_menu_item.set_submenu(self.compile_menu)
            for values in DEFAULT_CONFIG.compile_menu_actions:
                (menu_label, workdir, template_file, include_file, target_file) = values
                menu_item = gtk.MenuItem(menu_label)
                menu_item.show()
                menu_item.connect('activate', self._on_compile_menu,
                    DialinesTemplate(workdir, template_file, include_file, target_file, self.show_error).execute)
                self.compile_menu.append(menu_item)
            self.menu_bar.append(self.compile_menu_item)
        # The help menu
        self.help_menu_item = gtk.MenuItem('Help')
        self.help_menu_item.show()
        self.help_menu = gtk.Menu()
        self.help_menu_item.set_submenu(self.help_menu)
        self.help_about_item = gtk.MenuItem('About')
        self.help_about_item.show()
        self.help_about_item.connect('activate', self._on_help_about)
        self.help_menu.append(self.help_about_item)
        self.menu_bar.append(self.help_menu_item)
        # Add the menu bar to the window
        self.window_area.pack_start(self.menu_bar, False, False, 0)

        # Add a status bar
        self.status_box = gtk.HBox()
        self.status_box.show()
        self.window_area.pack_end(self.status_box, False, False, 0)
        self.problem_index_status_bar = gtk.Statusbar()
        self.problem_index_status_bar.set_has_resize_grip(False)
        self.problem_index_status_bar.set_size_request(120, -1)
        self.problem_index_status_bar.show()
        self.status_box.pack_start(self.problem_index_status_bar, False, False, 0)
        self.problem_position_context_id = self.problem_index_status_bar.get_context_id('problem_position')
        self.problem_position_message_id = self.problem_index_status_bar.push(self.problem_position_context_id, 'Problem 1 of 1')
        self.piece_count_status_bar = gtk.Statusbar()
        self.piece_count_status_bar.show()
        self.status_box.pack_start(self.piece_count_status_bar, True, True, 0)
        self.piece_count_context_id = self.piece_count_status_bar.get_context_id('piece_count')
        self.piece_count_message_id = self.piece_count_status_bar.push(self.piece_count_context_id, '(0+0)')


    def _add_menu_item_with_accelerator(self, menu, label, handler, accel_group, accel_char, key_modifier=0):
        result = self._add_menu_item(menu, label, handler)
        result.add_accelerator('activate', accel_group, accel_char, key_modifier, gtk.ACCEL_VISIBLE)
        return result

    def _add_menu_item(self, menu, label, handler):
        result = gtk.MenuItem(label)
        result.show()
        result.connect('activate', handler, None)
        menu.append(result)
        return result

    def _store_changes_to_problem(self):
        '''
        This method needs to be called to transfer input data to the current problem.
        '''
        self.info_area.save_to_problem()
        (white, black, neutral) = self.board_piece_count_panel.get_control_counters()
        if (white, black, neutral) != (0, 0, 0):
            piece_counter = model.PieceCounter(white, black, neutral)
        else:
            piece_counter = None
        self.model.current_problem().pieces_control = piece_counter

    def on_problems_first(self, widget, event, data=None):
        '''
        Called when user wants to switch to the first problem.
        '''
        self._store_changes_to_problem()
        self.model.first_problem()

    def on_problems_previous(self, widget, event, data=None):
        '''
        Called when user wants to switch to the previous problem.
        '''
        self._store_changes_to_problem()
        self.model.previous_problem()

    def on_problems_next(self, widget, event, data=None):
        '''
        Called when user wants to switch to the next problem.
        '''
        self._store_changes_to_problem()
        self.model.next_problem()

    def on_problems_last(self, widget, event, data=None):
        '''
        Called when user wants to switch to the last problem.
        '''
        self._store_changes_to_problem()
        self.model.last_problem()

    def on_problems_insert(self, widget, event, data=None):
        '''
        Called when the user wants to insert a new problem before the current one.
        '''
        self._store_changes_to_problem()
        self.model.insert_problem()

    def on_problems_append(self, widget, event, data=None):
        '''
        Called when the user wants to insert a new problem after the current one.
        '''
        self._store_changes_to_problem()
        self.model.append_problem()

    def on_problems_delete(self, widget, event, data=None):
        '''
        Called when the user wants to delete the current problem.
        '''
        dialog = gtk.MessageDialog(
                flags=gtk.DIALOG_MODAL,
                type=gtk.MESSAGE_QUESTION,
                buttons=gtk.BUTTONS_YES_NO,
                message_format='Are you sure to delete the problem?')
        response = dialog.run()
        if response == gtk.RESPONSE_YES:
            self.model.delete_problem()
        dialog.destroy()

    def on_change_boardsize(self, widget, event, data=None):
        '''
        Called when the user selects the menu entry "change board size".
        '''
        board = self.model.current_problem().board
        dialog = BoardSizeDialog(board.rows, board.columns)
        response = dialog.run()
        if response == gtk.RESPONSE_ACCEPT:
            board.resize(dialog.get_rows(), dialog.get_columns())
            self._on_current_problem_change()
        dialog.destroy()

    def _on_compile_menu(self, widget, data=None):
        '''
        Called when one of the (document) tools menu items is selected.
        The 'data' parameter contains the document method to be called.
        '''
        self._store_changes_to_problem()
        Thread(target=data(self.model.get_document())).run()


    def on_file_new(self, widget, event, data=None):
        '''
        Event handler for menu entry File / New.
        '''
        self.filename = None
        self.model.set_document(model.ChessproblemDocument())

    def _open_file(self, filename):
        '''
        Registers the given filename and reads the problems from this file.
        '''
        self.filename = filename
        self.file_save_item.set_sensitive(True)
        with open(filename, 'r') as f:
            s = f.read()
            parser = ChessProblemLatexParser()
            document = parser.parse_latex_str(s)
            self.model.set_document(document)


    def on_file_open(self, widget, event, data=None):
        '''
        Event handler for menu entry File / Open.
        '''
        dialog = gtk.FileChooserDialog(
                title='Open file', action=gtk.FILE_CHOOSER_ACTION_OPEN,
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
            self._open_file(filename)
        else:
            LOGGER.info('on_file_open: No files selected')
        dialog.destroy()

    def on_file_save(self, widget, event, data=None):
        '''
        Event handler for menu entry File / Save.
        '''
        if self.filename != None:
            self._save_file()
        else:
            LOGGER.warn('on_file_save called without a registered filename.')

    def on_file_save_as(self, widget, event, data=None):
        '''
        Event handler for menu entry File / Save As.
        '''
        dialog = gtk.FileChooserDialog(
                title='Save as ...',
                action=gtk.FILE_CHOOSER_ACTION_SAVE,
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
            if filename != None:
                self.filename = filename
                self.file_save_item.set_sensitive(True)
                self._save_file()
        else:
            LOGGER.info('on_file_open: No files selected')
        dialog.destroy()

    def _save_file(self):
        '''
        Saves the current problemlist into the file with the registered filename.
        '''
        self._store_changes_to_problem()
        with open(self.filename, 'w') as f:
            write_latex(self.model.get_document(), f)

    def on_file_exit(self, widget, event, data=None):
        '''
        Event handler for menu entry File / Exit.
        '''
        self.quit()


    def on_delete(self, widget, event, data=None):
        '''
        Called when the application should be closed.
        '''
        return False

    def on_destroy(self, widget, data=None):
        '''
        Called when the destroy_event occurs.
        '''
        self.quit()

    def _on_current_problem_change(self):
        '''
        This method is registered as observer to changes to the current selected problem within the list of problems.
        It is used change the display and adjust the statusbar accordingly.
        '''
        current_problem = self.model.current_problem()
        if current_problem.board.rows <= 8:
            self.row_scrollbar.hide()
        else:
            self.row_scrollbar.show()
        self.legend_strategy(self.row_scrollbar, self.row_legend_viewport)
        self.row_legend.set_rows(current_problem.board.rows)
        if current_problem.board.columns <= 8:
            self.column_scrollbar.hide()
        else:
            self.column_scrollbar.show()
        self.legend_strategy(self.column_scrollbar, self.column_legend_viewport)
        self.column_legend.set_columns(current_problem.board.columns)
        self.board_input_handler.set_problem(current_problem)
        self.info_area.set_problem(current_problem)
        self.board_display.set_chessproblem(current_problem)
        if current_problem.pieces_control != None:
            self.board_piece_count_panel.set_control_counters(
                    current_problem.pieces_control.count_white, 
                    current_problem.pieces_control.count_black, 
                    current_problem.pieces_control.count_neutral)
        else:
            self.board_piece_count_panel.set_control_counters(0, 0, 0)
        (white, black, neutral) = current_problem.board.get_pieces_count()
        self.board_piece_count_panel.set_current_values(white, black, neutral)
        # Adjust Statusbar
        self.problem_index_status_bar.remove_message(
                self.problem_position_context_id,
                self.problem_position_message_id)
        self.problem_position_message_id = self.problem_index_status_bar.push(
                self.problem_position_context_id,
                'problem %d of %d' % (self.model.current_problem_index + 1, self.model.get_problem_count()))
        # Adjust enabled/disabled navigation menus
        self.problems_previous_item.set_sensitive(not self.model.is_first_problem())
        self.problems_next_item.set_sensitive(not self.model.is_last_problem())

    def _on_help_about(self, widget, data=None):
        dialog = AboutDialog()
        dialog.run()
        dialog.destroy()

    def quit(self):
        gtk.main_quit()
        sys.exit(0)

    def main(self):
        gtk.main()


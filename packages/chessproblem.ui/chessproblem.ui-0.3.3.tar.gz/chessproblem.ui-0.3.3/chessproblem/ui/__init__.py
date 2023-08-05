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
This package contains the classes which make up the chessproblem editor user interface.
'''

import Tkinter as tk
import tkFileDialog
import tkMessageBox

import chessproblem.model as model
import chessproblem.model.db as db

import os.path

from chessproblem.io import ChessProblemLatexParser
from chessproblem.io import write_latex

from board import BoardFrame

from info import InfoFrame
from info import AuthorDatabaseDialog

from chessproblem.config import CONFIGDIR, ensure_config_dir, load_logging_config

import logging

LOGGER = logging.getLogger('chessproblem.ui')

DATABASE='sqlite:///' + os.path.join(CONFIGDIR, 'cpe.db')

class MainFrame(tk.Frame):
    '''
    The mainframe of the chessproblem editor application.
    '''
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.latex_parser = ChessProblemLatexParser()
        self.grid()
        self._create_data()
        self._create_menu()
        self._create_ui()
        self._create_bindings()
        self._on_current_problem_change()

    def _on_current_problem_change(self):
        problem = self._current_problem()
        self.board_frame.set_board(problem.board)
        self.info_frame.set_problem(problem)
        if self.current_problem_index > 0:
            self.problemmenu.entryconfig(0, state=tk.NORMAL)
            self.problemmenu.entryconfig(1, state=tk.NORMAL)
        else:
            self.problemmenu.entryconfig(0, state=tk.DISABLED)
            self.problemmenu.entryconfig(1, state=tk.DISABLED)
        if self.current_problem_index < len(self.problems) - 1:
            self.problemmenu.entryconfig(2, state=tk.NORMAL)
            self.problemmenu.entryconfig(3, state=tk.NORMAL)
        else:
            self.problemmenu.entryconfig(2, state=tk.DISABLED)
            self.problemmenu.entryconfig(3, state=tk.DISABLED)

    def _on_filename_set(self):
        self.filemenu.entryconfig(1, state=tk.NORMAL)


    def _open(self, event=None):
        '''
        Read problems from a file.
        '''
        LOGGER.debug("MainFrame._open()")
        filename = tkFileDialog.askopenfilename()
        if filename:
            self.filename = filename
            with open(filename) as f:
                self.problems = self.latex_parser.parse_latex_str(f.read())
                self.current_problem_index = 0
                self._on_current_problem_change()
            self._on_filename_set()

    def _store_changes(self):
        self.info_frame.store_changes()

    def _save(self, event=None):
        LOGGER.debug("MainFrame._save()")
        self._store_changes()
        if self.filename != '':
            with open(self.filename, 'w') as f:
                write_latex(self.problems, f)
            self._on_filename_set()

    def _save_as(self, event=None):
        '''
        Write problems to a file.
        '''
        LOGGER.debug("MainFrame._save_as()")
        filename = tkFileDialog.asksaveasfilename()
        if filename:
            self.filename = filename
            self._save()

    def _quit(self, event=None):
        LOGGER.debug("MainFrame._quit()")
        quit()

    def _firstproblem(self, event=None):
        if self.current_problem_index != 0:
            self._store_changes()
            self.current_problem_index = 0
            self._on_current_problem_change()

    def _previousproblem(self, event=None):
        if self.current_problem_index != 0:
            self._store_changes()
            self.current_problem_index = self.current_problem_index-1
            self._on_current_problem_change()

    def _nextproblem(self, event=None):
        if self.current_problem_index < len(self.problems)-1:
            self._store_changes()
            self.current_problem_index = self.current_problem_index+1
            self._on_current_problem_change()

    def _lastproblem(self, event=None):
        if self.current_problem_index < len(self.problems)-1:
            self._store_changes()
            self.current_problem_index = len(self.problems)-1
            self._on_current_problem_change()

    def _append_problem(self, event=None):
        self._store_changes()
        self.current_problem_index += 1
        self.problems.insert(self.current_problem_index, model.Chessproblem())
        self._on_current_problem_change()

    def _insert_problem(self, event=None):
        self._store_changes()
        self.problems.insert(self.current_problem_index, model.Chessproblem())
        self._on_current_problem_change()

    def _delete_problem(self, event=None):
        if tkMessageBox.askyesno(message='Are you sure to delete the problem?'):
            if len(self.problems) == 1:
                self.problems[0] = model.Chessproblem()
            else:
                self.problems.pop(self.current_problem_index)
                if self.current_problem_index == len(self.problems):
                    self.current_problem_index -= 1
            self._on_current_problem_change()

    def _authors_database(self):
        LOGGER.debug('MainFrame._authors_database(self) ...')
        dialog = AuthorDatabaseDialog(self, self.db_service)
        LOGGER.debug('MainFrame._authors_database(self) ... done.')


    def _create_menu(self):
        self.menubar = tk.Menu(self.master)
        # Create the file menu
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label='Open', accelerator='Ctrl-o', command=self._open)
        self.filemenu.add_command(label='Save', accelerator='Ctrl-S', command=self._save)
        self.filemenu.entryconfig(1, state=tk.DISABLED)
        self.filemenu.add_command(label='Save as', accelerator='Ctrl-Shift-S', command=self._save_as)
        self.filemenu.add_command(label='Quit', accelerator='Ctrl-Q', command=self._quit)
        self.menubar.add_cascade(label='File', menu=self.filemenu)
        # Create the menu use to navigate through the problems
        self.problemmenu = tk.Menu(self.menubar, tearoff=0)
        self.problemmenu.add_command(label='First', accelerator='Home', command=self._firstproblem)
        self.problemmenu.add_command(label='Previous', accelerator='PgUp', command=self._previousproblem)
        self.problemmenu.add_command(label='Next', accelerator='PgDn', command=self._nextproblem)
        self.problemmenu.add_command(label='Last', accelerator='End', command=self._lastproblem)
        self.problemmenu.add_separator()
        self.problemmenu.add_command(label='Insert problem', accelerator='Shift-Insert', command=self._insert_problem)
        self.problemmenu.add_command(label='Append problem', accelerator='Shift-Return', command=self._append_problem)
        self.problemmenu.add_command(label='Delete problem', accelerator='Shift-Delete', command=self._delete_problem)
        self.menubar.add_cascade(label='Problems', menu=self.problemmenu)
        # Create the menu to edit the base data (stored inside the database).
        self.basedata_menu = tk.Menu(self.menubar, tearoff=0)
        self.basedata_menu.add_command(label='Authors', command=self._authors_database)
        self.problemmenu.add_separator()
        self.menubar.add_cascade(label='Basedata', menu=self.basedata_menu)
        # Activate the menu
        self.master.configure(menu=self.menubar)

    def _create_data(self):
        ensure_config_dir()
        load_logging_config()
        self.db_service = db.DbService(DATABASE)
        self.problems = [model.Chessproblem()]
        self.current_problem_index = 0
        self.filename = ''

    def _current_problem(self):
        return self.problems[self.current_problem_index]

    def _create_ui(self):
        problem = self._current_problem()
        self.info_frame = InfoFrame(self, problem, self.db_service)
        self.info_frame.grid(row=0, column=0, padx=5, sticky=tk.N)
        self.board_frame = BoardFrame(self, problem.board)
        self.board_frame.grid(row=0, column=1, padx=5, sticky=tk.N)

    def _create_bindings(self):
        self.bind_all('<Home>', self._firstproblem)
        self.bind_all('<Prior>', self._previousproblem)
        self.bind_all('<Next>', self._nextproblem)
        self.bind_all('<End>', self._lastproblem)
        self.bind_all('<Shift-Return>', self._append_problem)
        self.bind_all('<Shift-Insert>', self._insert_problem)
        self.bind_all('<Shift-Delete>', self._delete_problem)
        self.bind_all('<Control-o>', self._open)
        self.bind_all('<Control-s>', self._save)
        self.bind_all('<Control-Shift-s>', self._save_as)
        self.bind_all('<Control-q>', self._quit)


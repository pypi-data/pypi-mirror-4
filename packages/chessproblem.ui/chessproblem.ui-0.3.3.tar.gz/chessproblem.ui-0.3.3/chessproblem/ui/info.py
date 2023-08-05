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
This module contains classes which are used to collect textual information about a chessproblem.
'''

import Tkinter as tk

import tkFileDialog
import ScrolledText as st
from tkSimpleDialog import Dialog

from chessproblem.model import Author

from common import ScrollableListbox
from common import SearchEntry
from common import ListEditDialog

import logging

LOGGER = logging.getLogger('chessproblem.ui')

class AuthorDatabaseDialog(Dialog):
    '''
    A dialog to edit, add and delete authors.
    '''
    def __init__(self, master, db_service):
        LOGGER.info('AuthorDatabaseDialog.__init__(self, master, db_service)')
        self.master = master
        self.db_service = db_service
        self.latex_parser = master.latex_parser
        self.author = None
        Dialog.__init__(self, master, title='authors database')

    def search_authors(self, text):
        authors = self.db_service.search_authors(text)
        self.author_listbox.set_objects(authors)

    def _new_author(self):
        LOGGER.debug('AuthorDatabaseDialog._new_author(self)')
        self.author = Author()
        self.lastname.set('')
        self.firstname.set('')
        self._enable_edit_mode()

    def _enable_edit_mode(self):
        self.search_entry.config(state=tk.DISABLED)
        self.author_listbox.enable(False)
        self.lastname_entry.config(state=tk.NORMAL)
        self.firstname_entry.config(state=tk.NORMAL)
        self.new_button.config(state=tk.DISABLED)
        self.edit_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.NORMAL)

    def _edit_author(self):
        LOGGER.debug('AuthorDatabaseDialog._edit_author(self)')
        authors = self.author_listbox.get_selected_objects()
        if len(authors) == 1:
            self.author = authors[0]
            self._enable_edit_mode()

    def _on_selection_change(self):
        authors = self.author_listbox.get_selected_objects()
        if len(authors) == 1:
            author = authors[0]
            self.lastname.set(author.lastname)
            self.firstname.set(author.firstname)

    def _enable_search_mode(self):
        self.search_entry.config(state=tk.NORMAL)
        self.author_listbox.enable(True)
        self.lastname_entry.config(state='readonly')
        self.firstname_entry.config(state='readonly')
        self.new_button.config(state=tk.NORMAL)
        self.edit_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)

    def _save(self):
        self.author.lastname = self.lastname.get()
        self.author.firstname = self.firstname.get()
        self.db_service.store_author(self.author)
        self.author = None
        self._enable_search_mode()
        self.search_authors(self.search_entry.get())

    def _cancel(self):
        self.author = None
        self._on_selection_change()
        self._enable_search_mode()

    def body(self, master):
        LOGGER.debug('AuthorDatabaseDialog.body(self, master)')
        # The frame containing the search entry and the listbox
        search_frame = tk.Frame(master)
        search_frame.grid(row=0, column=0, padx=5, pady=5)
        self.search_label = tk.Label(search_frame, text='Search')
        self.search_label.grid(row=0, column=0)
        self.search_entry = SearchEntry(search_frame, self.search_authors)
        self.search_entry.grid(row=0, column=1)
        self.author_listbox = ScrollableListbox(search_frame, width=30)
        self.author_listbox.grid(row=1, column=0, rowspan=3, columnspan=2, pady=5, sticky=tk.E+tk.W)
        self.author_listbox.selection_change_listeners.append(self._on_selection_change)
        self.search_authors('')
        # The frame containing the buttons
        button_frame = tk.Frame(master)
        button_frame.grid(row=0, column=1, padx=5, pady=5)
        self.new_button = tk.Button(button_frame, text='New', command=self._new_author)
        self.new_button.grid(row=0, pady=10)
        self.edit_button = tk.Button(button_frame, text='Edit', command=self._edit_author)
        self.edit_button.grid(row=1, pady=10)
        # The frame containing the edit form.
        form_frame = tk.Frame(master)
        form_frame.grid(row=0, column=2, padx=5, pady=5)
        self.lastname_label = tk.Label(form_frame, text='Lastname: ')
        self.lastname_label.grid(row=0, column=0)
        self.lastname = tk.StringVar()
        self.lastname_entry = tk.Entry(form_frame, textvariable=self.lastname)
        self.lastname_entry.config(state='readonly')
        self.lastname_entry.grid(row=0, column=1)
        self.firstname_label = tk.Label(form_frame, text='Firstname: ')
        self.firstname_label.grid(row=1, column=0)
        self.firstname = tk.StringVar()
        self.firstname_entry = tk.Entry(form_frame, textvariable=self.firstname)
        self.firstname_entry.config(state='readonly')
        self.firstname_entry.grid(row=1, column=1)
        form_button_frame = tk.Frame(form_frame)
        form_button_frame.grid(row=2, column=0, columnspan=2, pady=8)
        self.save_button = tk.Button(form_button_frame, text='Save', command=self._save)
        self.save_button.config(state=tk.DISABLED)
        self.save_button.grid(row=0, column=0, padx=5)
        self.cancel_button = tk.Button(form_button_frame, text='Cancel', command=self._cancel)
        self.cancel_button.config(state=tk.DISABLED)
        self.cancel_button.grid(row=0, column=1, padx=5)
        return self.search_entry

    def buttonbox(self):
        box = tk.Frame(self)
        finish_button = tk.Button(box, text="Finish", width=20, command=self.cancel)
        finish_button.grid(row=0, column=0, padx=25)
        import_button = tk.Button(box, text="Import authors", width=20, command=self.import_authors)
        import_button.grid(row=0, column=1, padx=25)
        box.pack(pady=5)

    def import_authors(self):
        LOGGER.debug("AuthorDatabaseDialog.import_authors() ...")
        filename = tkFileDialog.askopenfilename()
        if filename != '':
            LOGGER.debug('AuthorDatabaseDialog.import_authors() from file: ' + filename)
            with open(filename) as f:
                imported_problems = self.latex_parser.parse_latex_str(f.read())
            imported_authors = []
            for problem in imported_problems:
                if len(problem.cities) > 0:
                    if len(problem.cities) == len(problem.authors):
                        for index in range(len(problem.authors)):
                            imported_authors.append(ImportAuthor(problem.authors[index], problem.cities[index]))
                    else:
                        LOGGER.error('No. of cities does not match no. of authors, will ignore cities.')
                        imported_authors.extend([ImportAuthor(author) for author in problem.authors])
                else:
                    imported_authors.extend([ImportAuthor(author) for author in problem.authors])
            self.db_service.store_import_authors(imported_authors)
            dialog = AuthorImportDialog(self, self.db_service)
        LOGGER.debug("AuthorDatabaseDialog.import_authors() ... done.")


class AuthorEditDialog(Dialog):
    '''
    A dialog to edit author information.
    '''
    def __init__(self, master, db_service, author=None):
        LOGGER.info('AuthorEditDialog.__init__(self, master, db_service, author)')
        self.db_service = db_service
        if author == None:
            self.author = Author()
        else:
            self.author = author
        Dialog.__init__(self, master, title='Edit author')

    def body(self, master):
        self.lastname_label = tk.Label(master, text='Lastname: ')
        self.lastname_label.grid(row=0, column=0)
        self.lastname_entry = tk.Entry(master)
        self.lastname = tk.StringVar(value=self.author.lastname)
        self.lastname_entry.config(textvariable=self.lastname)
        self.lastname_entry.grid(row=0, column=1)
        self.firstname_label = tk.Label(master, text='Firstname: ')
        self.firstname_label.grid(row=1, column=0)
        self.firstname_entry = tk.Entry(master)
        self.firstname = tk.StringVar(value=self.author.firstname)
        self.firstname_entry.config(textvariable=self.firstname)
        self.firstname_entry.grid(row=1, column=1)
        return self.lastname_entry

    def apply(self):
        self.author.lastname = self.lastname.get()
        self.author.firstname = self.firstname.get()
        self.db_service.store_authors([self.author])

class AuthorSearchDialog(Dialog):
    '''
    A dialog to search for authors.
    '''
    def __init__(self, master, db_service, problem):
        LOGGER.info('AuthorSearchDialog.__init__(self, master, db_service, problem)')
        self.master = master
        self.db_service = db_service
        self.problem = problem
        Dialog.__init__(self, master, title='Edit authors')

    def search(self, text):
        '''
        Automatically called by SearchEntry when a user releases a key.
        '''
        LOGGER.debug('AuthorSearchDialog.search(' + text + ')')
        authors = self.db_service.search_authors(text)
        self.authorsearchbox.set_objects(authors)

    def _add_selected(self):
        new_selected_authors = self.authorsearchbox.get_selected_objects()
        self.authorlistbox.add_objects(new_selected_authors)

    def _remove_selected(self):
        self.authorlistbox.remove_selected_objects()

    def _new_author(self):
        dialog = AuthorEditDialog(self, self.db_service)


    def body(self, master):
        '''
        Creates the ui elements of this dialog.
        '''
        LOGGER.info('AuthorSearchDialog.body(...) ...')
        self.searchlabel = tk.Label(master, text='Search: ')
        self.searchlabel.grid(row=0, column=0)
        self.searchentry = SearchEntry(master, self.search)
        self.searchentry.grid(row=0, column=1)
        self.authorsearchbox = ScrollableListbox(master)
        self.authorsearchbox.grid(row=1, column=0, columnspan=2, pady=4, sticky=tk.E+tk.W)
        self.search('')
        self.add_selected_button = tk.Button(master, text='>>', command=self._add_selected)
        self.add_selected_button.grid(row=1, column=2, padx=4)
        self.remove_selected_button = tk.Button(master, text='remove', command=self._remove_selected)
        self.remove_selected_button.grid(row=0, column=3, padx=4, sticky=tk.E+tk.W)
        self.new_author_button = tk.Button(master, text='new', command=self._new_author)
        self.new_author_button.grid(row=0, column=4, padx=4, sticky=tk.E+tk.W)
        self.authorlistbox = ScrollableListbox(master)
        self.authorlistbox.set_objects(self.problem.authors)
        self.authorlistbox.grid(row=1, column=3, columnspan=2, pady=4, sticky=tk.E+tk.W)
        LOGGER.info('AuthorSearchDialog.body(...) ... done.')
        return self.searchentry

    def apply(self):
        self.problem.authors = self.authorlistbox.get_objects()
        self.master.on_authors_changed()

class AuthorImportDialog(Dialog):
    def __init__(self, master, db_service):
        LOGGER.info('AuthorImportDialog.__init__(self, master)')
        self.db_service = db_service
        self.state == 0
        Dialog.__init__(self, master, title='Import authors')

    def _remove_known_authors(self):
        remove_ids = (set([author.id for author in self.author_listbox.get_objects()])
                - set([author.id for author in self.author_listbox.get_selected_objects()]))
        if len(remove_ids) > 0:
            self.db_service.remove_import_authors(remove_ids)
        self.list_label.config(text='Already known authors (exact search match)')
        self.action_button.config(command=self._remove_known_search_authors)
        self.author_listbox.set_objects(self.db_service.known_search_import_authors())

    def _remove_known_search_authors(self):
        remove_ids = (set([author.id for author in self.author_listbox.get_objects()])
                - set([author.id for author in self.author_listbox.get_selected_objects()]))
        if len(remove_ids) > 0:
            self.db_service.remove_import_authors(remove_ids)
        # For now we will import the remaining authors
        self.import_remaining_authors()
        self.action_button.config(state=tk.DISABLED)


    def import_remaining_authors(self):
        authors_to_import = [Author(import_author.lastname, import_author.firstname) for import_author in self.db_service.import_authors()]
        self.db_service.store_authors(authors_to_import)


    def body(self, master):
        '''
        Create the ui elements inside the AuthorImportDialog.
        '''
        LOGGER.info('AuthorImportDialog(self, master) ...')
        self.list_label = tk.Label(master, text='Already known authors (exact match)')
        self.list_label.grid(row=0, column=0)
        self.author_listbox = ScrollableListbox(master, selectmode=tk.EXTENDED)
        self.author_listbox.grid(row=1, column=0)
        self.author_listbox.set_objects(self.db_service.known_import_authors())
        self.action_label = tk.Label(master, text='Leave marked to be imported ...')
        self.action_label.grid(row=2, column=0)
        self.action_button = tk.Button(master, text='proceed', command=self._remove_known_authors)
        self.action_button.grid(row=3, column=0)
        LOGGER.info('AuthorImportDialog(self, master) ... done.')
        return self.author_listbox




_INFOFRAME_ENTRIES =['specialdiagnum', 'stipulation', 'dedication', 'remark', 'sourcenr', 'source', 'issue', 'pages', 'day', 'month', 'year', 'tournament', 'award']


class InfoFrame(tk.Frame):
    '''
    The layout container for all informational related ui elements like authors, stipulation, etc.
    '''
    def _edit_authors(self):
        LOGGER.debug('InfoFrame._edit_authors')
        dialog = AuthorSearchDialog(self, self.db_service, self.problem)

    def _get_entry(self, name):
        entry_name = name + '_entry'
        entry = getattr(self, entry_name)
        value = entry.get()
        if value == '':
            value = None
        setattr(self.problem, name, value)

    def store_changes(self):
        for name in _INFOFRAME_ENTRIES:
            self._get_entry(name)
        solution = self.solution_text.get(1.0, tk.END)
        if solution == '':
            solution = None
        self.problem.solution = solution.strip()
        comment = self.comment_text.get(1.0, tk.END)
        if comment == '':
            comment = None
        self.problem.comment = comment.strip()


    def on_authors_changed(self):
        self.authors_listbox.set_objects(self.problem.authors)

    def on_twins_changed(self):
        self.twins_listbox.set_objects(self.problem.twins)

    def on_conditions_changed(self):
        self.condition_listbox.set_objects(self.problem.conditions)

    def on_themes_changed(self):
        self.themes_listbox.set_objects(self.problem.themes)

    def on_cities_changed(self):
        self.cities_listbox.set_objects(self.problem.cities)

    def _set_entry(self, name):
        entry_name = name + '_entry'
        entry = getattr(self, entry_name)
        entry.delete(0, tk.END)
        value = getattr(self.problem, name)
        if value != None:
            entry.insert(0, value)

    def set_problem(self, problem):
        LOGGER.debug('InfoFrame.set_problem')
        self.problem = problem
        self.on_authors_changed()
        for name in _INFOFRAME_ENTRIES:
            self._set_entry(name)
        self.on_conditions_changed()
        self.on_twins_changed()
        self.on_themes_changed()
        self.on_cities_changed()
        self.solution_text.delete(1.0, tk.END)
        if self.problem.solution != None:
            self.solution_text.insert(tk.END, self.problem.solution)
        self.comment_text.delete(1.0, tk.END)
        if self.problem.comment != None:
            self.comment_text.insert(tk.END, self.problem.comment)

    def _edit_conditions(self):
        LOGGER.debug('InfoFrame._edit_conditions')
        dialog = ListEditDialog(self, self.problem, title='Edit conditions', attribute='conditions', label_text='Conditions')
        self.on_conditions_changed()

    def _edit_twins(self):
        LOGGER.debug('InfoFrame._edit_twins')
        dialog = ListEditDialog(self, self.problem, title='Edit twins', attribute='twins', label_text='Twins')
        self.on_twins_changed()

    def _edit_themes(self):
        LOGGER.debug('InfoFrame._edit_themes')
        dialog = ListEditDialog(self, self.problem, title='Edit themes', attribute='themes', label_text='Themes')
        self.on_themes_changed()

    def _edit_cities(self):
        LOGGER.debug('InfoFrame._edit_cities')
        dialog = ListEditDialog(self, self.problem, title='Edit cities', attribute='cities', label_text='Cities')
        self.on_cities_changed()


    def __init__(self, master, problem, db_service):
        LOGGER.info('InfoFrame.__init__')
        tk.Frame.__init__(self, master)
        self.db_service = db_service
        # Authors
        self.authors_label = tk.Label(self, text='Authors')
        self.authors_label.grid(row=0, column=0, padx=5, sticky=tk.N)
        self.authors_listbox = ScrollableListbox(self, height=5, width=30)
        self.authors_listbox.grid(row=0, column=1, padx=5, rowspan=3, sticky=tk.W)
        self.authors_button_edit = tk.Button(self, text='edit list', command=self._edit_authors)
        self.authors_button_edit.grid(row=1, column=0, padx=5, sticky=tk.W+tk.E+tk.N)
        # Cities
        self.cities_label = tk.Label(self, text='Cities')
        self.cities_label.grid(row=0, column=2, padx=5, sticky=tk.N)
        self.cities_listbox = ScrollableListbox(self, height=5, width=30)
        self.cities_listbox.grid(row=0, column=3, padx=5, rowspan=3, sticky=tk.W)
        self.cities_button_edit = tk.Button(self, text='edit list', command=self._edit_cities)
        self.cities_button_edit.grid(row=1, column=2, padx=5, sticky=tk.W+tk.E+tk.N)
        # Dedication
        self.dedication_label = tk.Label(self, text='Dedication')
        self.dedication_label.grid(row=3, column=0, padx=5, sticky=tk.N)
        self.dedication_entry = tk.Entry(self, width=30)
        self.dedication_entry.grid(row=3, column=1, columnspan=2, padx=5, sticky=tk.N+tk.W)
        # Stipulation
        self.stipulation_label = tk.Label(self, text='Stipulation')
        self.stipulation_label.grid(row=4, column=0, padx=5, sticky=tk.N)
        self.stipulation_entry = tk.Entry(self, width=30)
        self.stipulation_entry.grid(row=4, column=1, columnspan=2, padx=5, sticky=tk.N+tk.W)
        # Remark
        self.remark_label = tk.Label(self, text='Remark')
        self.remark_label.grid(row=4, column=2, padx=5, sticky=tk.N)
        self.remark_entry = tk.Entry(self, width=30)
        self.remark_entry.grid(row=4, column=3, columnspan=2, padx=5, sticky=tk.N+tk.W)
        # Condition
        self.condition_label = tk.Label(self, text='Conditions')
        self.condition_label.grid(row=5, column=0, sticky=tk.N)
        self.condition_listbox = ScrollableListbox(self, height=4, width=30)
        self.condition_listbox.grid(row=5, column=1, padx=5, rowspan=2, sticky=tk.N+tk.W)
        self.condition_button = tk.Button(self, text='edit list', command=self._edit_conditions)
        self.condition_button.grid(row=6, column=0, sticky=tk.N+tk.W+tk.E)
        # Twins
        self.twins_label = tk.Label(self, text='Twins')
        self.twins_label.grid(row=5, column=2, sticky=tk.N)
        self.twins_listbox = ScrollableListbox(self, height=4, width=30)
        self.twins_listbox.grid(row=5, column=3, padx=5, rowspan=2, sticky=tk.N+tk.W)
        self.twins_button = tk.Button(self, text='edit list', command=self._edit_twins)
        self.twins_button.grid(row=6, column=2, sticky=tk.N+tk.W+tk.E)
        # Solution
        self.solution_label = tk.Label(self, text='Solution')
        self.solution_label.grid(row=7, column=0, sticky=tk.N)
        self.solution_text = st.ScrolledText(self)
        self.solution_text.config(height=8)
        self.solution_text.grid(row=7, column=1, columnspan=3, padx=5, sticky=tk.N+tk.S+tk.W+tk.E)
        # Specialdiagnum
        self.specialdiagnum_label = tk.Label(self, text='specialdiagnum')
        self.specialdiagnum_label.grid(row=8, column=0, sticky=tk.W)
        self.specialdiagnum_entry = tk.Entry(self, width=10)
        self.specialdiagnum_entry.grid(row=8, column=1, columnspan=5, padx=5, sticky=tk.W)
        #   sourcenr
        self.sourcenr_label = tk.Label(self, text='sourcenr')
        self.sourcenr_label.grid(row=9, column=0, sticky=tk.W)
        self.sourcenr_entry = tk.Entry(self, width=10)
        self.sourcenr_entry.grid(row=9, column=1, columnspan=5, padx=5, sticky=tk.W)
        #   source
        self.source_label = tk.Label(self, text='source')
        self.source_label.grid(row=10, column=0, sticky=tk.W)
        self.source_entry = tk.Entry(self, width=30)
        self.source_entry.grid(row=10, column=1, columnspan=5, padx=5, sticky=tk.W)
        #   issue
        self.issue_label = tk.Label(self, text='issue')
        self.issue_label.grid(row=11, column=0, sticky=tk.W)
        # issue frame for issue and pages
        self.issue_frame = tk.Frame(self)
        self.issue_frame.grid(row=11, column=1, padx=5, sticky=tk.W)
        self.issue_entry = tk.Entry(self.issue_frame, width=10)
        self.issue_entry.grid(row=0, column=0, sticky=tk.W)
        self.pages_label = tk.Label(self.issue_frame, text='pages')
        self.pages_label.grid(row=0, column=1, padx=5, sticky=tk.W)
        self.pages_entry = tk.Entry(self.issue_frame, width=10)
        self.pages_entry.grid(row=0, column=2, padx=5, sticky=tk.W)
        # frame for day, month year
        self.date_frame = tk.Frame(self)
        self.date_frame.grid(row=12, column=1, padx=5, ipadx=0, sticky=tk.W)
        #   day
        self.day_label = tk.Label(self, text='day')
        self.day_label.grid(row=12, column=0, sticky=tk.W)
        self.day_entry = tk.Entry(self.date_frame, width=2)
        self.day_entry.grid(row=0, column=0, sticky=tk.W)
        #   month
        self.month_label = tk.Label(self.date_frame, text='month(s)')
        self.month_label.grid(row=0, column=1, padx=5)
        self.month_entry = tk.Entry(self.date_frame, width=5)
        self.month_entry.grid(row=0, column=2, padx=5)
        #   year
        self.year_label = tk.Label(self.date_frame, text='year')
        self.year_label.grid(row=0, column=3, padx=5)
        self.year_entry = tk.Entry(self.date_frame, width=4)
        self.year_entry.grid(row=0, column=4, sticky=tk.E)
        # themes
        self.themes_label = tk.Label(self, text='themes')
        self.themes_label.grid(row=8, column=2, padx=5, sticky=tk.W)
        self.themes_listbox = ScrollableListbox(self, height=4, width=30)
        self.themes_listbox.grid(row=8, column=3, padx=5, rowspan=3, sticky=tk.N+tk.W)
        self.themes_button = tk.Button(self, text='edit list', command=self._edit_themes)
        self.themes_button.grid(row=9, column=2, sticky=tk.N+tk.W+tk.E)
        # comment
        self.comment_label = tk.Label(self, text='comment')
        self.comment_label.grid(row=11, column=2, padx=5, sticky=tk.W)
        self.comment_text = st.ScrolledText(self, height=4, width=30)
        self.comment_text.grid(row=11, column=3, padx=5, rowspan=4, sticky=tk.N+tk.S+tk.W+tk.E)
        # tournament
        self.tournament_label = tk.Label(self, text='tournament')
        self.tournament_label.grid(row=13, column=0, sticky=tk.W)
        self.tournament_entry = tk.Entry(self, width=40)
        self.tournament_entry.grid(row=13, column=1, columnspan=2, padx=5, sticky=tk.W)
        # award
        self.award_label = tk.Label(self, text='award')
        self.award_label.grid(row=14, column=0, sticky=tk.W)
        self.award_entry = tk.Entry(self, width=20)
        self.award_entry.grid(row=14, column=1, padx=5, sticky=tk.W)
        #
        # when finished, may provide the values
        #
        self.set_problem(problem)
        


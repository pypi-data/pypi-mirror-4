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
'''

from chessproblem.model import Chessproblem, ChessproblemDocument

class ChessProblemModel(object):
    '''
    This class defines the model, where the user interface communicates with.
    '''

    def __init__(self):
        '''
        Initializes our model.
        '''
        self._document = ChessproblemDocument()
        self.current_problem_index = 0
        self._observers = []

    def get_document(self):
        return self._document

    def add_observer(self, observer):
        self._observers.append(observer)

    def set_document(self, document):
        if document.get_problem_count() > 0:
            self._document = document
        else:
            self._document = ChessproblemDocument()
        self.current_problem_index = 0
        self._on_current_problem_changed()

    def get_problem_count(self):
        return self._document.get_problem_count()

    def current_problem(self):
        return self._document.get_problem(self.current_problem_index)

    def first_problem(self):
        if self.current_problem_index > 0:
            self.current_problem_index = 0
            self._on_current_problem_changed()

    def previous_problem(self):
        if self.current_problem_index > 0:
            self.current_problem_index = self.current_problem_index - 1
            self._on_current_problem_changed()

    def next_problem(self):
        if self.current_problem_index < self._document.get_problem_count() - 1:
            self.current_problem_index = self.current_problem_index + 1
            self._on_current_problem_changed()

    def last_problem(self):
        if self.current_problem_index < self._document.get_problem_count() - 1:
            self.current_problem_index = self._document.get_problem_count() - 1
            self._on_current_problem_changed()

    def append_problem(self):
        self.current_problem_index += 1
        self._document.insert_problem(self.current_problem_index, Chessproblem())
        self._on_current_problem_changed()

    def insert_problem(self):
        self._document.insert_problem(self.current_problem_index, Chessproblem())
        self._on_current_problem_changed()

    def delete_problem(self):
        if self._document.get_problem_count() == 1:
            self._document.set_problem(0, Chessproblem())
        else:
            self._document.delete_problem(self.current_problem_index)
            if self.current_problem_index == self._document.get_problem_count():
                self.current_problem_index -= 1
        self._on_current_problem_changed()

    def is_first_problem(self):
        return self.current_problem_index == 0

    def is_last_problem(self):
        return self.current_problem_index == self._document.get_problem_count() - 1

    def _on_current_problem_changed(self):
        for observer in self._observers:
            observer()


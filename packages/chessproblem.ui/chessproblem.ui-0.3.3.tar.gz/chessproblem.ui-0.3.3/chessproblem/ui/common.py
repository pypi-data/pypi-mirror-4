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
This module contains common or generic classes used inside the user interface.
'''


import Tkinter as tk

from tkSimpleDialog import Dialog

import logging

LOGGER = logging.getLogger('chessproblem.ui')


class ScrollableListbox(tk.Frame):
    '''
    This class combines a listbox with a scrollbar.
    '''
    def __init__(self, master, selectmode=tk.SINGLE, display=str, width=20, height=10):
        tk.Frame.__init__(self, master)
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(self, selectmode=selectmode, yscrollcommand=self.scrollbar.set, height=height, width=width)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.display = display
        self.objects = []
        self.selection_change_listeners = []
        self.listbox.bind('<ButtonRelease-1>', self._on_selection_changed)
        self.listbox.bind('<KeyRelease-space>', self._on_selection_changed)

    def enable(self, enable):
        if (enable):
            self.listbox.config(state=tk.NORMAL)
        else:
            self.listbox.config(state=tk.DISABLED)

    def _on_selection_changed(self, event=None):
        for listener in self.selection_change_listeners:
            listener()

    def _on_objects_changed(self):
        self.listbox.delete(0, self.listbox.size())
        for obj in self.objects:
            self.listbox.insert(tk.END, self.display(obj))

    def set_objects(self, objects):
        self.objects = objects[:]
        self._on_objects_changed()

    def add_objects(self, objects):
        self.objects.extend(objects)
        self._on_objects_changed()

    def selection_set(self, index):
        self.listbox.selection_set(index)

    def replace_object(self, index, new):
        previous = self.objects[index]
        self.objects[index] = new
        LOGGER.debug('Changed entry at index ' + str(index) + ' from "' + str(previous) + '" to "' + str(new) + '"')
        self._on_objects_changed()

    def get_selected_indices(self):
        '''
        Return a list with the selected indices.
        '''
        return map(int, self.listbox.curselection())


    def get_selected_objects(self):
        selection = map(int, self.listbox.curselection())
        return [self.objects[index] for index in selection]

    def get_objects(self):
        return self.objects

    def remove_selected_objects(self):
        selection = map(int, self.listbox.curselection())
        remaining = set(range(self.listbox.size())) - set(selection)
        self.objects = [self.objects[index] for index in remaining]
        self._on_objects_changed()



class SearchEntry(tk.Entry):
    '''
    A specialized entry class to use for search dialogs, which allows an action while typing.
    '''
    def __init__(self, master, keyhandler):
        tk.Entry.__init__(self, master)
        self.keyhandler = keyhandler
        self.bind('<KeyRelease>', self._on_key)

    def _on_key(self, event):
        self.keyhandler(self.get())

class ListEditDialog(Dialog):
    '''
    Dialog to edit a string list property of a problem.
    '''
    def __init__(self, master, problem, title, attribute, label_text):
        LOGGER.info('ConditionsEditDialog.__init__(self, master, problem)')
        self.problem = problem
        self.attribute = attribute
        self.label_text = label_text
        Dialog.__init__(self, master, title=title)

    def _on_selection_changed(self):
        values = self.listbox.get_selected_objects()
        if len(values) == 1:
            self.value.set(values[0])
        else:
            self.value.set('')

    def _save(self):
        self.listbox.enable(True)
        value = self.value.get()
        if self.index == -1:
            LOGGER.debug('New value: ' + value)
            self.listbox.add_objects([value])
        else:
            LOGGER.debug('Changed value: ' + value)
            self.listbox.replace_object(self.index, value)
            self.listbox.selection_set(self.index)
        self._disable_edit_mode()
        self._on_selection_changed()

    def _cancel(self):
        self.listbox.enable(True)
        self._disable_edit_mode()
        self._on_selection_changed()

    def _new(self):
        self.value.set('')
        self.index = -1
        self._enable_edit_mode()

    def _enable_edit_mode(self):
        self.listbox.enable(False)
        self.new_button.config(state=tk.DISABLED)
        self.edit_button.config(state=tk.DISABLED)
        self.entry.config(state=tk.NORMAL)
        self.save_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.NORMAL)

    def _disable_edit_mode(self):
        self.new_button.config(state=tk.NORMAL)
        self.edit_button.config(state=tk.NORMAL)
        self.entry.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)

    def _edit(self):
        selection = self.listbox.get_selected_indices()
        if len(selection) == 1:
            self.index = selection[0]
            self._enable_edit_mode()

    def _remove_selected(self):
        self.listbox.remove_selected_objects()
        self.value.set('')

    def body(self, master):
        self.left_frame = tk.Frame(master)
        self.left_frame.grid(row=0, column=0)
        self.listbox = ScrollableListbox(self.left_frame)
        self.listbox.grid(row=0, column=0, rowspan=3)
        self.listbox.selection_change_listeners.append(self._on_selection_changed)
        self.listbox.set_objects(getattr(self.problem, self.attribute))
        self.remove_button = tk.Button(self.left_frame, text='remove selected', command=self._remove_selected)
        self.remove_button.grid(row=4, column=0)
        self.button_frame = tk.Frame(master)
        self.button_frame.grid(row=0, column=1, padx=10)
        self.new_button = tk.Button(self.button_frame, text='new', command=self._new)
        self.new_button.grid(row=1, column=1)
        self.edit_button = tk.Button(self.button_frame, text='edit', command=self._edit)
        self.edit_button.grid(row=2, column=1)
        self.form_frame = tk.Frame(master)
        self.form_frame.grid(row=0, column=2)
        self.label = tk.Label(self.form_frame, text=self.label_text)
        self.label.grid(row=0, column=2, sticky=tk.N+tk.W)
        self.value = tk.StringVar()
        self.entry = tk.Entry(self.form_frame, width=30, textvariable=self.value)
        self.entry.config(state=tk.DISABLED)
        self.entry.grid(row=1, column=2, columnspan=2, sticky=tk.N+tk.W)
        self.save_button = tk.Button(self.form_frame, text='Save', command=self._save)
        self.save_button.config(state=tk.DISABLED)
        self.save_button.grid(row=2, column=2)
        self.cancel_button = tk.Button(self.form_frame, text='Cancel', command=self._cancel)
        self.cancel_button.config(state=tk.DISABLED)
        self.cancel_button.grid(row=2, column=3)
        return self.listbox

    def apply(self):
        setattr(self.problem, self.attribute, self.listbox.get_objects())




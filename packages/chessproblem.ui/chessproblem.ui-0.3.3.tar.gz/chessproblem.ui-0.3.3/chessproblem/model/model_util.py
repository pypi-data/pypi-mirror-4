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
This module contains utility functions for the model classes.
In detail these are the normalization methods for names.
'''

import string

def _handle_command(command):
    if command == 'i':
        return 'i'
    elif command == 'j':
        return 'j'
    elif command == 'o' or command == 'O':
        return 'o'
    elif command == 'l' or command == 'L':
        return 'l'
    elif command == 'AA' or command == 'aa':
        return 'a'
    elif command == 'AE' or command == 'ae':
        return 'ae'
    elif command == 'OE' or command == 'oe':
        return 'oe'
    elif command == 'ss':
        return 'ss'
    else:
        return ''

def un_latex_string(s):
    '''
    This method is used to remove latex encodings from a string (e.g. a name).

    For special TeX codings like \\i it creates an i. Most other latex codes and macros are simply removed.
    '''
    result = ''
    command = ''
    i = iter(s)
    state = 0
    try:
        while True:
            c = i.next()
            if state == 0:
                if c in string.ascii_letters:
                    result = result + c.lower()
                elif c == '\\':
                    state = 1
                    command = ''
            elif state == 1:
                if c in string.ascii_letters:
                    command = command + c
                    state = 2
                elif c == '3':
                    result = result + 'ss'
                    state = 0
                else:
                    # Ignore this latex command
                    state = 0
            elif state == 2:
                if c in string.ascii_letters:
                    command = command + c
                else:
                    result = result + _handle_command(command)
                    command = ''
                    if c == '\\':
                        state = 1
                    else:
                        state = 0
    except StopIteration:
        if state == 2:
            result = result + _handle_command(command)
    return result


def normalize_string(s):
    '''
    This methos is used to normalize names.
    '''
    return un_latex_string(s)

def normalize_author_name(lastname, firstname):
    return normalize_string(lastname) + ', ' + normalize_string(firstname)


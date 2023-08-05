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
This module provides the SchwalbeUrdrucke class, which allows to set common values,
to all diagrams.
'''

class SchwalbeUrdrucke(object):
    def __init__(self, issue, month, year, start_sourcenr):
        self.issue = issue
        self.month = month
        self.year = year
        if start_sourcenr != None:
            self.sourcenr = int(start_sourcenr)
        else:
            self.sourcenr = None

    def execute(self, chessproblem):
        if len(chessproblem.authors) > 0:
            if chessproblem.source == None:
                chessproblem.source = 'Die Schwalbe'
            if self.issue != None and chessproblem.issue == None:
                chessproblem.issue = self.issue
            if self.month != None and chessproblem.month == None:
                chessproblem.month = self.month
            if self.year != None and chessproblem.year == None:
                chessproblem.year = self.year
            if self.sourcenr != None and chessproblem.sourcenr == None:
                chessproblem.sourcenr = str(self.sourcenr)
                self.sourcenr = self.sourcenr + 1


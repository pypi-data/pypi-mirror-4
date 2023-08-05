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


import pygtk
pygtk.require("2.0")
import gtk, gtk.gdk

import os.path

from chessproblem import cpe_version

from chessproblem.model import Chessproblem
from chessproblem.io import ChessProblemLatexParser

from gtk_board import Board

CPE_BOARD_TEX = '''
%
\\begin{diagram}[9x5]
\\pieces{wBb5, wSa4, wLa3, wTa2, wDb1, wKc1, wEc5, sBe5, sSd5, sLd4, sTd3, sDd2, sKd1, sEf4, sCe3, nBh5, nSg4, nLh3, nTg2, nDh1, nKi1, nEi5}
\\end{diagram}
%
'''

class AboutDialog(gtk.Dialog):
    '''
    This dialog is used to implemenent the 'Help/About' menu entry within the ChessProblemEditor application.
    '''
    def __init__(self):
        gtk.Dialog.__init__(self, title='About chess problem editor', flags=gtk.DIALOG_MODAL, buttons=(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        parser = ChessProblemLatexParser()
        document = parser.parse_latex_str(CPE_BOARD_TEX)
        chessproblem = document.get_problem(0)
        board = Board(chessproblem)
        board.show()
        self.get_content_area().pack_start(board, False, False, 10)
        name_label = gtk.Label('Chess Problem Editor - Version %s' % (cpe_version()))
        name_label.show()
        self.get_content_area().pack_start(name_label, False, False, 10)
        copyright_label = gtk.Label('Copyright 2012 Stefan Hoening')
        copyright_label.show()
        self.get_content_area().pack_start(copyright_label, False, False, 10)
        license_label = gtk.Label()
        license_label.set_markup('<a href="http://www.gnu.org/licenses/gpl.html">Published under GPL</a>')
        license_label.show()
        self.get_content_area().pack_start(license_label, False, False, 10)



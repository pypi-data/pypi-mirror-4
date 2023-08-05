#!/usr/bin/env python

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



from chessproblem.tools import handle_document
from chessproblem.tools.schwalbe import SchwalbeUrdrucke
from chessproblem.io import ChessProblemLatexParser, write_latex

from chessproblem.config import CONFIGDIR, ensure_config_dir, load_logging_config

ensure_config_dir()
load_logging_config()

from optparse import OptionParser

usage = '''
%prog [options] filename

This script may be used to add common entries to all diagrams in the given file.
The resulting diagrams are written to a new file with the extension ".new" appended.
'''
option_parser = OptionParser()

option_parser.add_option('-i', '--issue', dest='issue', default=None, help='die heft nummer')
option_parser.add_option('-m', '--month', dest='month', default=None, help='der monat des erscheinens')
option_parser.add_option('-y', '--year', dest='year', default=None, help='das erscheinungsjahr')
option_parser.add_option('-s', '--start_sourcenr', dest='start_sourcenr', default=None, help='die start problemnummer des urdruckteils')

(options, args) = option_parser.parse_args()

if len(args) == 1:
    filename = args[0]
    handler = SchwalbeUrdrucke(options.issue, options.month, options.year, options.start_sourcenr)
    parser = ChessProblemLatexParser()
    with open(filename) as f:
        document = parser.parse_latex_str(f.read())
        handle_document(document, handler)
        outputfile = filename + '.new'
        with open(outputfile, 'w') as f:
            write_latex(document, f)
else:
    option_parser.print_help()


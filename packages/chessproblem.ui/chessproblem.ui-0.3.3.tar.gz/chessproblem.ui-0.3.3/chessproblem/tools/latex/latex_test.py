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


import unittest

from tempfile import gettempdir

from chessproblem.model import ChessproblemDocument
from chessproblem.tools.latex import latex, DialinesTemplate, LatexCompilerException

from os import remove
from os.path import join, exists

import logging
LOGGER = logging.getLogger('chessproblem.tools.latex')
LOGGER.setLevel(logging.DEBUG)
filehandler = logging.FileHandler('latex_test.log')
LOGGER.addHandler(filehandler)

from chessproblem.config import DEFAULT_CONFIG

def _create_sample_file(dir, filename, text):
    absolute_filename = join(dir, filename)
    if exists(absolute_filename):
        remove(absolute_filename)
    with open(absolute_filename, 'w') as f:
        f.write(text)

class LatexCompilerTest(unittest.TestCase):
    def setUp(self):
        DEFAULT_CONFIG.compiled_latex_viewer = None
        self.dir = gettempdir()
        self.valid_filename = 'valid.tex'
        _create_sample_file(self.dir, self.valid_filename,
            '''
            \\documentclass{article}
            \\begin{document}
            This is a test.
            \\end{document}
            ''')

        self.invalid_filename = 'invalid.tex'
        _create_sample_file(self.dir, self.invalid_filename,
                '''
            \\documentclass{article}
            \\begin{document}
            Unknown command \\rb should produce a failure.
            \\end{document}
                ''')
        self.template_filename = 'template.tex'
        _create_sample_file(self.dir, self.template_filename,
            '''
            \\documentclass{article}
            \\begin{document}
            This is the template file. Now the include.

            \\input{include}

            Now we are back in the template file.
            \\end{document}
            ''')
        self.compiled_filename = 'template.dvi'
        self.include_filename = 'include.tex'
        _create_sample_file(self.dir, self.include_filename,
            'This is included from our template file.')

    def test_valid_latex(self):
        latex(self.valid_filename, workdir=self.dir)

    def test_invalid_latex(self):
        try:
            latex(self.invalid_filename, workdir=self.dir)
            self.assertTrue(False)
        except LatexCompilerException, e:
            self.assertTrue(e.returncode != 0)
            self.assertTrue(e.log != None)
            print e.log
        
    def test_DialinesTemplate(self):
        template = DialinesTemplate(self.dir, self.template_filename, self.include_filename, self.compiled_filename)
        template.execute(ChessproblemDocument([]))

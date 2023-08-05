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
This problem contains functions and classes to run LaTeX from within the chess
problem editor application.
'''

from subprocess import Popen, PIPE, STDOUT

from os.path import join, splitext

from chessproblem.config import DEFAULT_CONFIG
from chessproblem.io import write_latex

import logging

LOGGER = logging.getLogger('chessproblem.tools.latex')

class LatexCompilerException(Exception):
    '''
    Used to indicate an error during a latex compilation.
    '''
    def __init__(self, returncode, log):
        self.returncode = returncode
        self.log = log

def latex(filename, workdir=None, compiler=None):
    '''
    Compile the given file using the given compiler.
    If no compiler is given, the configuration CpeConfig is checked for a parameter 'latex_compiler'.
    If this is also not given, we use the command 'latex'.
    '''
    if compiler == None:
        try:
            compiler = getattr(DEFAULT_CONFIG, 'latex_compiler')
        except AttributeError:
            pass
        if compiler == None:
            compiler = 'latex'
    if workdir != None:
        stdout_filename = join(workdir, filename + '.stdout')
    else:
        stdout_filename = filename + '.stdout'
    returncode = 0
    with open(stdout_filename, 'w') as f:
        process = Popen([compiler, '\\batchmode \\input ' + filename], stdout=f, stderr=STDOUT, cwd=workdir)
        process.communicate()
        if process.returncode == 1:
            returncode = 1
    if returncode == 1:
        (base_filename, extension) = splitext(filename)
        log_filename = base_filename + '.log'
        if workdir != None:
            log_filename = join(workdir, log_filename)
        with open(log_filename, 'r') as f:
            compiler_output = f.read()
            raise LatexCompilerException(returncode, compiler_output)

class DialinesTemplate(object):
    '''
    This class allows the execute method to be used as document handler.
    '''
    def __init__(self, workdir, template_filename, include_filename, compiled_filename, error_handler=None):
        self.template_filename = template_filename
        self.include_filename = include_filename
        self.workdir = workdir
        self.compiled_filename = compiled_filename
        self.error_handler = error_handler
        self.viewer_process = None

    def execute(self, document):
        try:
            self.dialines_template(document, self.template_filename, self.include_filename, self.compiled_filename, self.workdir)
        except LatexCompilerException, e:
            if self.error_handler != None:
                self.error_handler('There was an error compiling the latex file.', e.log)
            else:
                print e.log

    def dialines_template(self, document, template_filename, include_filename, compiled_filename, workdir):
        '''
        Writes the problems contained in the given document to the file with name include_filename and
        then compiles the file with the given template_filename. Both template_filename and include_filename
        will be inside workdir.
        '''
        include_file = join(workdir, include_filename)
        with open(include_file, 'w') as f:
            write_latex(document, f, problems_only=True)
        latex(template_filename, workdir=workdir)
        if DEFAULT_CONFIG.compiled_latex_viewer != None:
            if self.viewer_process == None or self.viewer_process.poll() != None:
                self.viewer_process = Popen([DEFAULT_CONFIG.compiled_latex_viewer, self.compiled_filename], cwd=self.workdir)


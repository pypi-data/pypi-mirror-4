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


from setuptools import setup, find_packages


execfile('chessproblem/version.py')

setup(name='chessproblem.ui',
      version=VERSION,
      description='The user interface to edit chessproblems for tex files using the chess-problem-diagrams latex style.',
      long_description="""\
              This package contains the chess-problem-editor application and some utilities around editing chess problems.
              The intention of this application is to have a visual editor application for chess problems written using the LaTeX-style
              named chess-problem-diagrams (diagram.sty).

              There is also an application to maintain a simple author-database (the authors of the chess problems), so one may select
              authors from this database when entering new problems.
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python :: 2.7",
        "Topic :: Games/Entertainment :: Board Games",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        ],
      keywords='chess problem user interface classes',
      author='Stefan Hoening',
      author_email='Stefan.Hoening@web.de',
      url='http://sourceforge.net/projects/chessproblemed/',
      download_url='http://pypi.python.org/packages/source/c/chessproblem.ui/chessproblem.ui-' + VERSION + '.tar.gz',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      scripts=['bin/cpe.py', 'bin/cpdb.py', 'bin/schwalbe_urdrucke.py', 'bin/import_countries.py', 'bin/import_cities.py', 'bin/import_authors.py', 'bin/import_check.py', 'bin/import_sources.py'],
      package_data = {
          'chessproblem.ui': [
              'images/32/*.xbm', 'images/36/*.xbm', 'images/40/*.xbm', 'images/44/*.xbm', 'images/48/*.xbm',
              'images/32/*.png', 'images/36/*.png', 'images/40/*.png', 'images/44/*.png', 'images/48/*.png' ],
      },
      test_suite='nose.collector',
      # test_requires=['nose'],  
      zip_safe=False,
      # py_modules=['distribute_setup'],
      install_requires=[
          'sqlalchemy==0.7.3',
          'Pygments==1.4',
          'kph==0.1',
          # 'python-Levenshtein==0.10.2',
          # 'jellyfish=0.2.0',
          # 'Fuzzy=1.0',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

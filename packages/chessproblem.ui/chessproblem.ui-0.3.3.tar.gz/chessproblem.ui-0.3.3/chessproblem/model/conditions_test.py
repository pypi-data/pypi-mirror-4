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

from conditions import CONDITION_SERVICE

import unittest

import logging

LOGGER = logging.getLogger('chessproblem.model.conditions')
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(logging.FileHandler('conditions.log'))

class ConditionsTestCase(unittest.TestCase):
        
    def test_get_all_conditions(self):
        conditions = CONDITION_SERVICE.get_all_conditions()
        self.assertTrue(conditions != None)
        self.assertTrue(len(conditions) > 0)
        for condition in conditions:
            LOGGER.info('%s - %s - %s - %s' % (condition.get_name(), condition.get_popeye_name(), condition.get_search(), condition.get_kph()))

    def test_filter_circe_conditions(self):
        conditions = CONDITION_SERVICE.filter_conditions_by_name('circ')
        self.assertTrue(conditions != None)
        self.assertEqual(37, len(conditions))
        LOGGER.info('Circe conditions:')
        for condition in conditions:
            LOGGER.info('%s - %s - %s - %s' % (condition.get_name(), condition.get_popeye_name(), condition.get_search(), condition.get_kph()))
        LOGGER.info('--- End of Circe conditions ---')


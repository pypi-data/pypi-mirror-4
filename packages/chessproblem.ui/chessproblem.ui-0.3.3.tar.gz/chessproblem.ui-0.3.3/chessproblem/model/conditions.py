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
This module contains the model classes for conditions, which may be selected
within the user interface.
'''

from model_util import normalize_string

from db_util import before_persist_object_listener

import sqlalchemy as sa
import sqlalchemy.orm as orm

import kph

import logging

LOGGER = logging.getLogger('chessproblem.model.conditions')

class Condition(object):
    '''
    Stores a fairy condition.
    Each fairy condition consists of:
    -   a name (which is the LaTeX encoded text used in documents)
    -   an optional keyword to use with popeye
    -   an optional problem_action, which allows e.g. to automatically set
        gridchess to 'True'. This must be a method, which expects a single 'Chessproblem'
        instances as parameter.
    '''
    def __init__(self, name, popeye_name=None, problem_action=None):
        '''
        Creates a fairy condition with the given 'name'.
        '''
        self._name = name
        self._popeye_name = popeye_name
        self._problem_action = problem_action

    def get_name(self):
        '''
        Retrieve the 'name' of the condition.
        '''
        return self._name

    def get_popeye_name(self):
        return self._popeye_name

    def get_search(self):
        return self._search

    def get_kph(self):
        return self._kph

    def execute_problem_action(self, chessproblem):
        '''
        Executes the registered '_problem_action'.
        '''
        if self._problem_action != None:
            self._problem_action(chessproblem)

    def on_persist(self):
        self._search = normalize_string(self._name)
        self._kph = kph.encode(self._search)

    def __str__(self):
        return self._name

def set_boolean_problem_action(chessproblem, member, value=True):
    setattr(chessproblem, member, value)

def gridchess_problem_action(chessproblem):
    set_boolean_problem_action(chessproblem, 'gridchess')

def verticalcylinder_problem_action(chessproblem):
    set_boolean_problem_action(chessproblem, 'verticalcylinder')

def horizontalcylinder_problem_action(chessproblem):
    set_boolean_problem_action(chessproblem, 'horizontalcylinder')

class ConditionService(object):
    '''
    A utility class, which puts given conditions into an in-memory database
    to be implement a search mask.
    '''
    def __init__(self, url):
        self._metadata = ConditionService._create_metadata()
        self._session_factory = ConditionService._create_session_factory(url, self._metadata)
        self._session = None

    def _get_session(self):
        if self._session == None:
            self._session = self._session_factory()
        return self._session

    @classmethod
    def _create_metadata(cls):
        metadata = sa.MetaData()
        # Map our Country class to the countries table
        conditions_table = sa.Table('conditions', metadata,
                sa.Column('id', sa.Integer, primary_key=True),
                sa.Column('_name', sa.String),
                sa.Column('_popeye', sa.String),
                sa.Column('_search', sa.String, index=True),
                sa.Column('_kph', sa.String, index=True))
        orm.mapper(Condition, conditions_table)
        sa.event.listen(Condition, 'before_insert', before_persist_object_listener)
        sa.event.listen(Condition, 'before_update', before_persist_object_listener)
        return metadata

    @classmethod
    def _create_session_factory(cls, url, metadata):
        engine = sa.create_engine(url)
        metadata.create_all(engine)
        session = orm.sessionmaker(bind=engine)
        return session

    def store_condition(self, condition):
        store_conditions([condition])

    def store_conditions(self, conditions):
        session = self._get_session()
        session.add_all(conditions)
        session.commit()

    def get_all_conditions(self):
        session = self._get_session()
        conditions = session.query(Condition).order_by(Condition._search).all()
        return conditions

    def filter_conditions_by_name(self, name):
        if name == None or len(name) == 0:
            return self.get_all_conditions()
        else:
            search = normalize_string(name)
            session = self._get_session()
            conditions = (session.query(Condition)
                .filter(sa.or_(Condition._search.like('%' + search + '%'), Condition._kph == kph.encode(search)))
                .order_by(Condition._search).all())
            return conditions

    def get_condition_by_name(self, name):
        '''
        This method may be used as factory method for conditions while reading problems from files.
        We first tries to find an exact matching condition.
        If none is found, we try to find a condition with a matching search string.
        If this not found either, we return a new condition with the given name.
        '''
        if name == None or len(name) == 0:
            return None
        else:
            session = self._get_session()
            conditions = (session.query(Condition).filter(Condition._name == name).all())
            if len(conditions) == 1:
                LOGGER.debug('condition with name %s found' % (name))
                return conditions[0]
            search = normalize_string(name)
            conditions = (session.query(Condition).filter(Condition._search == search).all())
            if len(conditions) == 1:
                LOGGER.debug('condition with search %s for name %s found' % (search, name))
                return conditions[0]
            LOGGER.info('no condition found for name %s with search %s - creating new one' % (name, search))
            return Condition(name)

CONDITION_SERVICE = ConditionService('sqlite://')

from os.path import realpath, dirname, join, exists
from chessproblem.config import DEFAULT_CONFIG, CONFIGDIR
import shutil

_CONDITION_CONFIG_TEMPLATE = join(dirname(realpath(__file__)), 'condition_config_template.py')

_CONDITION_CONFIG = join(CONFIGDIR, 'condition_config.py')

if not exists(_CONDITION_CONFIG):
    shutil.copy(_CONDITION_CONFIG_TEMPLATE, _CONDITION_CONFIG)

execfile(_CONDITION_CONFIG)

CONDITION_SERVICE.store_conditions(CONDITIONS)



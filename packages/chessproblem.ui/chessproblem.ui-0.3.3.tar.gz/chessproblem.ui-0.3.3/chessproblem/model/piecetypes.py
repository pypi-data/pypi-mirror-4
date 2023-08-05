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
This module contains the model classes for piecetypes, which may be selected
within the user interface.
'''

from model_util import normalize_string

from db_util import before_persist_object_listener

import sqlalchemy as sa
import sqlalchemy.orm as orm

import kph

import logging

LOGGER = logging.getLogger('chessproblem.model.piecetypes')

class PieceType(object):
    '''
    A piecetype specifies a fairy piece type.
    The type consists of a name and the short form used within popeye.
    '''
    def __init__(self, name, popeye_name):
        self._name = name
        self._popeye_name = popeye_name

    def get_name(self):
        return self._name

    def get_popeye_name(self):
        return self._popeye_name

    def on_persist(self):
        self._search = normalize_string(self._name)
        self._kph = kph.encode(self._search)

    def __str__(self):
        return self._name


    def get_search(self):
        return self._search

    def get_kph(self):
        return self._kph

class PieceTypeService(object):
    '''
    A utility class, which puts given piecetypes into an in-memory database
    to be implement a search mask.
    '''
    def __init__(self, url):
        self._metadata = PieceTypeService._create_metadata()
        self._session_factory = PieceTypeService._create_session_factory(url, self._metadata)
        self._session = None

    def _get_session(self):
        if self._session == None:
            self._session = self._session_factory()
        return self._session

    @classmethod
    def _create_metadata(cls):
        metadata = sa.MetaData()
        # Map our Country class to the countries table
        piecetypes_table = sa.Table('piecetypes', metadata,
                sa.Column('id', sa.Integer, primary_key=True),
                sa.Column('_name', sa.String),
                sa.Column('_popeye', sa.String),
                sa.Column('_search', sa.String, index=True),
                sa.Column('_kph', sa.String, index=True))
        orm.mapper(PieceType, piecetypes_table)
        sa.event.listen(PieceType, 'before_insert', before_persist_object_listener)
        sa.event.listen(PieceType, 'before_update', before_persist_object_listener)
        return metadata

    @classmethod
    def _create_session_factory(cls, url, metadata):
        engine = sa.create_engine(url)
        metadata.create_all(engine)
        session = orm.sessionmaker(bind=engine)
        return session

    def store_piecetype(self, piecetype):
        store_piecetypes([piecetype])

    def store_piecetypes(self, piecetypes):
        session = self._get_session()
        session.add_all(piecetypes)
        session.commit()

    def get_all_piecetypes(self):
        session = self._get_session()
        return session.query(PieceType).order_by(PieceType._search).all()

    def filter_piecetypes_by_name(self, name):
        if name == None or len(name) == 0:
            return self.get_all_piecetypes()
        else:
            search = normalize_string(name)
            session = self._get_session()
            piecetypes = (session.query(PieceType)
                .filter(sa.or_(PieceType._search.like('%' + search + '%'), PieceType._kph == kph.encode(search)))
                .order_by(PieceType._search).all())
            return piecetypes

    def get_piecetype_by_name(self, name):
        '''
        This method may be used as factory method for piecetypes while reading problems from files.
        We first tries to find an exact matching piecetype.
        If none is found, we try to find a piecetype with a matching search string.
        If this not found either, we return a new piecetype with the given name.
        '''
        if name == None or len(name) == 0:
            return None
        else:
            session = self._get_session()
            piecetypes = (session.query(PieceType).filter(PieceType._name == name).all())
            if len(piecetypes) == 1:
                LOGGER.debug('piecetype with name %s found' % (name))
                return piecetypes[0]
            search = normalize_string(name)
            piecetypes = (session.query(PieceType).filter(PieceType._search == search).all())
            if len(piecetypes) == 1:
                LOGGER.debug('piecetype with search %s for name %s found' % (search, name))
                return piecetypes[0]
            LOGGER.info('no piecetype found for name %s with search %s - creating new one' % (name, search))
            return PieceType(name)

PIECETYPE_SERVICE = PieceTypeService('sqlite://')

from os.path import realpath, dirname, join, exists
from chessproblem.config import DEFAULT_CONFIG, CONFIGDIR
import shutil

_PIECETYPE_CONFIG_TEMPLATE = join(dirname(realpath(__file__)), 'piecetypes_config_template.py')

_PIECETYPE_CONFIG = join(CONFIGDIR, 'piecetype_config.py')

if not exists(_PIECETYPE_CONFIG):
    shutil.copy(_PIECETYPE_CONFIG_TEMPLATE, _PIECETYPE_CONFIG)

execfile(_PIECETYPE_CONFIG)

PIECETYPE_SERVICE.store_piecetypes(PIECETYPES)




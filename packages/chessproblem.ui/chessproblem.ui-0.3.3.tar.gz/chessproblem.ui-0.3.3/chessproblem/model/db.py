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
This module contains the database abstraction layer of the chessproblem editor application.
'''
import sqlalchemy as sa
import sqlalchemy.orm as orm

import kph

from model_util import normalize_string
from model_util import normalize_author_name

from db_util import before_persist_object_listener

from . import Country, City, Author, Source
from . import ChessProblemModelFactory

import logging

LOGGER = logging.getLogger('chessproblem.model')
IMPORT_LOGGER = logging.getLogger('chessproblem.model.db.import')


def normalized_kph(s):
    return kph.encode(normalize_string(s))

class InconsistentData(Exception):
    def __init__(self, class_name, member_name, value1, value2=None):
        self.class_name = class_name
        self.member_name = member_name
        self.value1 = value1
        self.value2 = value2

class DbService(object):
    def __init__(self, url):
        LOGGER.info('Opening database: ' + url)
        self.metadata = self._create_metadata()
        self.session_factory = self._create_session_factory(url, self.metadata)
        self.session = None
        LOGGER.info('DbService initialized.')

    def _get_session(self):
        if self.session == None:
            self.session = self.session_factory()
        return self.session


    def _query(self, query):
        session = self._get_session()
        con = session.connection().connection
        cur = con.cursor()
        cur.execute(query)
        return [row for row in cur]

    def _count(self, _type):
        '''
        Returns the overall count of objects of the given type.
        '''
        session = self._get_session()
        return session.query(_type).count()
        
    def count_countries(self):
        '''
        Returns the overall count of countries.
        '''
        return self._count(Country)
        
    def count_cities(self):
        '''
        Returns the overall count of cities.
        '''
        return self._count(City)
        
    def count_authors(self):
        '''
        Returns the overall count of authors.
        '''
        return self._count(Author)
        
    def count_sources(self):
        '''
        Returns the overall count of sources.
        '''
        return self._count(Source)
        
    def reindex_authors(self):
        session = self._get_session()
        con = session.connection().connection
        con.create_function('normalize_author_name', 2, normalize_author_name)
        session.execute("UPDATE authors SET search=normalize_author_name(lastname, firstname)")
        con.create_function('normalized_kph', 1, normalized_kph)
        session.execute("UPDATE authors SET lastname_kph=normalized_kph(lastname), firstname_kph=normalized_kph(firstname)")
        session.commit()

    def reindex_cities(self):
        session = self._get_session()
        con = session.connection().connection
        con.create_function('normalize_string', 1, normalize_string)
        session.execute("UPDATE cities SET search=normalize_string(name)")
        con.create_function('kph_encode', 1, kph.encode)
        session.execute("UPDATE cities SET kph=kph_encode(search)")
        session.commit()

    def store_object(self, o):
        session = self._get_session()
        session.add(o)
        session.commit()

    def find_country_by_code(self, country_code):
        '''
        Search for the given country_code.
        Per default we search for the car_code. If there is no country with the given code as car_code
        we try with the code as iso 2- or 3-letter code (depending on it size).
        '''
        if country_code == None or len(country_code) == 0:
            return None
        session = self._get_session()
        try:
            country = session.query(Country).filter_by(car_code=country_code).one()
        except orm.exc.NoResultFound, e:
            if len(country_code) == 2:
                try:
                    country = session.query(Country).filter_by(iso_3166_2=country_code).one()
                except orm.exc.NoResultFound, e:
                    return None
            elif len(country_code) == 3:
                try:
                    country = session.query(Country).filter_by(iso_3166_3=country_code).one()
                except orm.exc.NoResultFound, e:
                    return None
            else:
                return None
        return country

    def find_countries_by_search(self, expr):
        session = self._get_session()
        return session.query(Country).filter(Country.search.like('%' + expr + '%')).order_by(Country.search).all()


    def store_country(self, country):
        self.store_object(country)

    def find_city_by_name(self, city_name):
        assert city_name != None
        session = self._get_session()
        cities = session.query(City).filter(City.name == city_name).all()
        if len(cities) == 1:
            city = cities[0]
            return city
        elif len(cities) == 0:
            cities = session.query(City).filter(City.search == normalize_string(city_name)).all()
            if len(cities) == 0:
                LOGGER.debug('find_city_by_name(' + city_name + ') - not found.')
                return None
            elif len(cities) == 1:
                city = cities[0]
                return city
            else:
                LOGGER.debug('find_city_by_name(' + city_name + ') - not unique.')
                return None
        else:
            LOGGER.debug('find_city_by_name(' + city_name + ') - not unique.')
            return None

    def find_city_by_name_and_country(self, city_name, country):
        assert city_name != None
        assert country != None
        session = self._get_session()
        cities = session.query(City).filter(City.search == normalize_string(city_name)).filter(City.country_id == country.id).all()
        if len(cities) == 0:
            LOGGER.debug('City ' + city_name + ' not found.')
            return None
        elif len(cities) == 1:
            city = cities[0]
            return city
        else:
            for city in cities:
                if city.name == city_name:
                    return city
            raise InconsistentData('City', 'country', city.country.car_code, country.car_code)

    def find_cities_by_search(self, search):
        session = self._get_session()
        if search == None:
            return session.query(City).all()
        else:
            normalized = normalize_string(search)
            return session.query(City).filter(sa.or_(City.search.like('%' + normalized + '%'), City.kph == kph.encode(normalized))).order_by(City.search).all()


    def store_city(self, city):
        '''
        Stores the given city instance inside the database.
        '''
        self.store_object(city)

    def find_author_by_lastname_firstname(self, lastname, firstname):
        assert lastname != None
        assert firstname != None
        session = self._get_session()
        authors = session.query(Author).filter(Author.search.like('%' + normalize_author_name(lastname, firstname) + '%')).all()
        if len(authors) == 0:
            return None
        elif len(authors) == 1:
            return authors[0]
        else:
            LOGGER.warn('Multiple authors found for ' + lastname + ', ' + firstname)
            return None


    def find_author_by_lastname_firstname_city(self, city, lastname, firstname):
        assert city != None
        assert lastname != None
        assert firstname != None
        session = self._get_session()
        authors = session.query(Author).filter_by(search=normalize_author_name(lastname, firstname)).all()
        if len(authors) == 0:
            return None
        elif len(authors) == 1:
            author = authors[0]
            if author.city != None and city.id != author.city.id:
                LOGGER.error('Found author with same name ' + lastname + ', ' + firstname + ' ' + str(city) + ' in different city ' + str(author.city))
                raise InconsistentData('Author', 'city', author.city.id, city.id)
            return author
        else:
            if city != None:
                for author in authors:
                    if author.city != None and author.city.id == city.id:
                        return author
            LOGGER.warn('Multiple authors found can.')
            return None

    def find_authors_by_search(self, search_filter):
        session = self._get_session()
        if search_filter == None:
            return session.query(Author).all()
        else:
            return session.query(Author).filter(Author.search.like('%' + normalize_string(search_filter) + '%')).order_by(Author.search).all()


    def store_author(self, author):
        self.store_object(author)

    def store_authors(self, authors):
        '''
        Stores the given list of authors.

        In addition to each author the generic author search object is stored.
        '''
        for author in authors:
            try:
                self.store([author])
            except sa.exc.SQLAlchemyError:
                LOGGER.info('Author ' + author.lastname + ' is already available')

    def find_sources_by_search(self, search):
        session = self._get_session()
        if search == None:
            return session.query(Source).all()
        else:
            return session.query(Source).filter(Source.search.like('%' + normalize_string(search) + '%')).order_by(Source.search).all()

    def store(self, objects):
        session = self._get_session()
        session.add_all(objects)
        session.commit()

    def delete(self, object_to_delete):
        session = self._get_session()
        session.delete(object_to_delete)
        session.commit()

    def _create_metadata(self):
        metadata = sa.MetaData()
        # Map our Country class to the countries table
        countries_table = sa.Table('countries', metadata,
                sa.Column('id', sa.Integer, primary_key=True),
                sa.Column('car_code', sa.String, index=True, unique=True),
                sa.Column('name', sa.String),
                sa.Column('iso_3166_2', sa.String, index=True, unique=True),
                sa.Column('iso_3166_3', sa.String, index=True, unique=True),
                sa.Column('iso_3166_n', sa.String, index=True, unique=True),
                sa.Column('search', sa.String, index=True))
        orm.mapper(Country, countries_table)
        sa.event.listen(Country, 'before_insert', before_persist_object_listener)
        sa.event.listen(Country, 'before_update', before_persist_object_listener)
        # Map our City class to the cities table
        cities_table = sa.Table('cities', metadata,
                sa.Column('id', sa.Integer, primary_key=True),
                sa.Column('name', sa.String, nullable=False),
                sa.Column('search', sa.String, nullable=False, index=True),
                sa.Column('country_id', sa.String, sa.ForeignKey('countries.id')),
                sa.Column('kph', sa.String, nullable=False, index=True))
        orm.mapper(City, cities_table, properties = {
            'country' : orm.relationship(Country)
            })
        sa.event.listen(City, 'before_insert', before_persist_object_listener)
        sa.event.listen(City, 'before_update', before_persist_object_listener)
        # Map our Author class to the authors table
        authors_table = sa.Table('authors', metadata,
                sa.Column('id', sa.Integer, primary_key=True),
                sa.Column('lastname', sa.String, nullable=False),
                sa.Column('firstname', sa.String, nullable=False),
                sa.Column('search', sa.String, nullable=False, index=True),
                sa.Column('lastname_kph', sa.String, index=True, nullable=False),
                sa.Column('firstname_kph', sa.String, index=True, nullable=False),
                sa.Column('city_id', sa.Integer, sa.ForeignKey('cities.id')))
        authors_mapper = orm.mapper(Author, authors_table, properties = {
            'city' : orm.relationship(City)
            })
        sa.event.listen(Author, 'before_insert', before_persist_object_listener)
        sa.event.listen(Author, 'before_update', before_persist_object_listener)
        # Map our Sources class to the sources table
        sources_table = sa.Table('sources', metadata,
                sa.Column('id', sa.Integer, primary_key=True),
                sa.Column('name', sa.String, nullable=False),
                sa.Column('search', sa.String, nullable=False, index=True),
                sa.Column('kph', sa.String, index=True, nullable=False))
        sources_mapper = orm.mapper(Source, sources_table)
        sa.event.listen(Source, 'before_insert', before_persist_object_listener)
        sa.event.listen(Source, 'before_update', before_persist_object_listener)
        return metadata

    def _create_session_factory(self, url, metadata):
        engine = sa.create_engine(url)
        metadata.create_all(engine)
        session = orm.sessionmaker(bind=engine)
        return session


class DatabaseChessProblemModelFactory(ChessProblemModelFactory):
    def __init__(self, db_service):
        self.db_service = db_service

    def create_country(self, car_code, name=None):
        country = self.db_service.find_country_by_code(car_code)
        if country != None:
            if name != None and country.name != name:
                LOGGER.warn('Found country for code ' + car_code + ' and name ' + name + ' with different name: ' + country.name)
            return country
        country = ChessProblemModelFactory.create_country(self, car_code, name)
        try:
            self.db_service.store_country(country)
            IMPORT_LOGGER.info('Importing country: ' + car_code + ' / ' + str(name))
        except sa.exc.SQLAlchemyError:
            LOGGER.warn('Country ' + country.car_code + ' is already available.')
        return country

    def create_city(self, country, city_name):
        city = self.db_service.find_city_by_name_and_country(city_name, country)
        if city != None:
            return city
        else:
            city = ChessProblemModelFactory.create_city(self, country, city_name)
            try:
                self.db_service.store_city(city)
                IMPORT_LOGGER.info('Importing city: ' + country.car_code + '--' + city_name)
            except sa.exc.SQLAlchemyError, e:
                LOGGER.warn('Could not persist city ' + str(city) + ' - reason: ' + str(e))
            return city

    def create_author(self, city, lastname, firstname):
        author = self.db_service.find_author_by_lastname_firstname_city(city, lastname, firstname)
        if author != None:
            return author
        else:
            author = ChessProblemModelFactory.create_author(self, city, lastname, firstname)
            try:
                self.db_service.store_author(author)
                IMPORT_LOGGER.info('Importing author: ' + lastname + ', ' + firstname + ' [' + str(city) + ']')
            except sa.exc.SQLAlchemyError, e:
                LOGGER.warn('Could not persist author ')
            return author




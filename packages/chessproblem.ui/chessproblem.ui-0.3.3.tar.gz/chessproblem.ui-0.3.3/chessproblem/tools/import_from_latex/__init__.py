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


import string

from chessproblem.config import DEFAULT_CONFIG
from chessproblem.model import Country
from chessproblem.model.db import DbService

def import_countries(filename, database_url=DEFAULT_CONFIG.database_url):
    '''
    This method is used to import countries from a file using the following format into our database:
    Each line contains two columns separated by a semicolon. The first column contains the car code,
    the second column contains the name of the country.
    
    A file which is provided in this format can e.g. be downloaded at
    http://www.kfz-auskunft.de/autokennzeichen/laenderkennzeichen.html.

    The file contains some entries, which should be igored (CC, CD, O)
    '''
    db_service = DbService(database_url)
    with open(filename, 'r') as f:
        for line in f:
            if line[-1] == '\n':
                line = line[:-1]
            fields = line.split(';')
            if len(fields) == 5:
                country_name = fields[0].strip()
                car_code = _country_code(fields[1])
                iso_3166_2 = _country_code(fields[2])
                iso_3166_3 = _country_code(fields[3])
                iso_3166_n = _country_code(fields[4])
                country = Country(car_code, name=country_name, iso_3166_2=iso_3166_2, iso_3166_3=iso_3166_3, iso_3166_n=iso_3166_n)
                db_service.store_country(country)

def _country_code(value):
    value = value.strip()
    if len(value) == 0:
        return None
    else:
        return value

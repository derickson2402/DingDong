#!/usr/local/bin/python
"""#############################################################################

Date
	19 February 2023
 
Author(s)
	Dan Erickson (dan@danerick.com)

Description
	Handle PostgreSQL connection for DingDong API backend.

Project URL
	https://github.com/derickson2402/DingDong.git
 
License
	GNU GPLv3

	Copyright (C) 2023 Dan Erickson

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <https://www.gnu.org/licenses/>.

#############################################################################"""

import psycopg2

TABLE_CONFIG = 'config'
TABLE_CONFIG_COLUMN_VALUE = 'ConfigValue'
TABLE_CONFIG_COLUMN_KEY = 'ConfigName'
TABLE_CONFIG_VALID_KEYS = ['CurrentSound', 'MaxSoundLength', 'Volume']

class DingDongDB:
	"""Database connector class to make backend connections nicer"""
	def __init__(self, host, password, port=5432, user="dingdong",
			database="dingdong"):
		"""Open up a connection to the backend database"""
		self.db = psycopg2.connect(
			host=host,
			password=password,
			port=port,
			user=user,
			dbname=database
		)

	def getConfigValue(self, key) -> int:
		"""Get a config value"""
		if key not in TABLE_CONFIG_VALID_KEYS:
			raise KeyError(f'{key} is not a valid key')
		sql = f'SELECT {TABLE_CONFIG_COLUMN_VALUE} FROM {TABLE_CONFIG} WHERE ' \
				f'{TABLE_CONFIG_COLUMN_KEY} = (%s)'
		cur = self.db.cursor()
		rtrn = None
		try:
			cur.execute(sql, key)
			rtrn = cur.fetchone()
			if rtrn is None or len(rtrn) < 1:
				raise Exception(f'db did not return anything for config {key}')
			rtrn = rtrn[0]
		except Exception as e:
			rtrn = None
			raise
		finally:
			cur.close()
			return rtrn

	def setConfigValue(self, key, val):
		"""Update a config value. Make sure you are passing in a valid value"""
		if key not in TABLE_CONFIG_VALID_KEYS:
			raise KeyError(f'{key} is not a valid key')
		sql = f'UPDATE {TABLE_CONFIG} ' \
				f'SET {TABLE_CONFIG_COLUMN_VALUE} = (%s) ' \
				f'WHERE {TABLE_CONFIG_COLUMN_KEY} = "(%s)";'
		cur = self.db.cursor()
		try:
			cur.execute(sql, (val,key))
			self.db.commit()
		except Exception as e:
			raise
		finally:
			cur.close()

	def getConfigDict(self) -> dict:
		"""Get all configuration options as a dictionary"""
		sql = f'SELECT {TABLE_CONFIG_COLUMN_KEY}, ' \
				f'{TABLE_CONFIG_COLUMN_VALUE} ' \
				f'FROM {TABLE_CONFIG} ' \
				f'ORDER BY {TABLE_CONFIG_COLUMN_KEY} ASC'
		cur = self.db.cursor()
		rtrn = { }
		try:
			cur.execute(sql)
			for record in cur:
				rtrn[record[0]] = record[1]
		except Exception as e:
			rtrn = None
			raise
		finally:
			cur.close()
		return rtrn

if __name__ == '__main__':
	print("Use this package as a library only")
	exit(1)

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
TABLE_CONFIG_VALID_KEYS = ['Volume', 'CurrentSound', 'MaxSoundLength']

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

	def __getConfigValue(self, key):
		"""Base getConfig method for getting config values"""
		if key not in TABLE_CONFIG_VALID_KEYS:
			raise KeyError(f'{key} is not a valid key')
		sql = f'SELECT {TABLE_CONFIG_COLUMN_VALUE} FROM {TABLE_CONFIG} WHERE ' \
				f'{TABLE_CONFIG_COLUMN_KEY} = (%s)'
		cur = self.db.cursor()
		try:
			cur.execute(sql, key)
			data = cur.fetchone()
			return data[0]
		except Exception as e:
			raise
		finally:
			cur.close()

	def __setConfigValue(self, key, val):
		"""Base setConfig method for updating values"""
		if key not in TABLE_CONFIG_VALID_KEYS:
			raise KeyError(f'{key} is not a valid key')
		sql = f'UPDATE {TABLE_CONFIG} SET {TABLE_CONFIG_COLUMN_VALUE} = (%s) ' \
				f'WHERE {TABLE_CONFIG_COLUMN_KEY} = "(%s)";'
		cur = self.db.cursor()
		try:
			cur.execute(sql, (val,key))
			self.db.commit()
		except Exception as e:
			raise
		finally:
			cur.close()

	def getVolume(self):
		"""Get the volume level as percent [0,100]"""
		val = self.__getConfigValue('Volume')
		return int(val)

	def getCurrentSound(self):
		"""Get the ID of the current sound effect"""
		val = self.__getConfigValue('CurrentSound')
		return int(val)

	def getMaxSoundLength(self):
		"""Get the maximum length, in seconds, a sound can play for"""
		val = self.__getConfigValue('MaxSoundLength')
		return int(val)

	def setVolume(self, volume):
		"""Update the volume level to percent [0,100]"""
		if volume > 100 or volume < 0:
			raise ValueError(f'{volume} not in range [0,100]')
		else:
			self.__setConfigValue('Volume', volume)

	def setCurrentSound(self, soundID):
		"""Update the current sound effect"""
		self.__setConfigValue('CurrentSound', soundID)

	def setMaxSoundLength(self, soundLength):
		"""Update the maximum length, in seconds, a sound can play for"""
		if soundLength < 0:
			raise ValueError(f'{soundLength} is not positive time length')
		else:
			self.__setConfigValue('MaxSoundLength', soundLength)

if __name__ == '__main__':
	print("Use this package as a library only")
	exit(1)

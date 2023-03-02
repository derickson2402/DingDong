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
from pydub import AudioSegment
from pathlib import Path
from os import remove

TBL_CONFIG = 'ConfigTbl'
TBL_CONFIG_VALUE = 'configValue'
TBL_CONFIG_KEY = 'configName'
TBL_CONFIG_VALID_KEYS = ['CurrentSound', 'MaxSoundLength', 'Volume']
TBL_LIBRARY = 'SoundLibraryTbl'
TBL_LIBRARY_ID = 'soundID'
TBL_LIBRARY_NAME = 'name'
TBL_LIBRARY_DESC = 'description'
TBL_LIBRARY_LENGTH = 'length'
TBL_LIBRARY_DATA = 'filePath'
TBL_LIBRARY_TIME = 'uploadTime'

def soundToMP3(path: Path) -> Path:
	"""Convert the sound file to mp3 format, returns the name of the new file"""
	outPath = path.with_suffix('.mp3')
	inSound = AudioSegment(path)
	outSound = inSound.set_channels(1)
	outSound.export(outPath, format="mp3")
	return outPath

class DingDongDB:
	"""Database connector class to make backend connections nicer"""
	def __init__(self, config: dict):
		"""Open up a connection to the backend database"""
		self.cfg = config

	def __open(self) -> None:
		self.conn = psycopg2.connect(
			host=self.cfg['host'],
			password=self.cfg['password'],
			port=self.cfg['port'],
			user=self.cfg['user'],
			dbname=self.cfg['database']
		)

	def __close(self) -> None:
		self.conn.close()

	def testConnection(self):
		"""Throw an exception if the database cannot be connected to"""
		try:
			self.__open()
		except:
			raise ConnectionError
		else:
			self.__close()

	def getConfigValue(self, key) -> int:
		"""Get a config value"""
		if key not in TBL_CONFIG_VALID_KEYS:
			raise KeyError(f'{key} is not a valid key')
		sql = f'SELECT {TBL_CONFIG_VALUE} FROM {TBL_CONFIG} WHERE ' \
				f'{TBL_CONFIG_KEY} = %s'
		rtrn = None
		try:
			self.__open()
			with self.conn.cursor() as cur:
				cur.execute(sql, key)
				rtrn = cur.fetchone()
		except Exception as e:
			self.__close()
			raise e
		if rtrn is None:
			raise Exception(f'db did not return anything for config {key}')
		elif not len(rtrn) == 1:
			raise Exception(f'db did not return anything for config {key}')
		return rtrn[0]

	def setConfigValue(self, key, val):
		"""Update a config value. Throws exception if key is invalid, but does
		not check for valid values"""
		if key not in TBL_CONFIG_VALID_KEYS:
			raise KeyError(f'{key} is not a valid key')
		sql = f'UPDATE {TBL_CONFIG} ' \
				f'SET {TBL_CONFIG_VALUE} = %s ' \
				f'WHERE {TBL_CONFIG_KEY} = %s;'
		try:
			self.__open()
			with self.conn.cursor() as cur:
				cur.execute(sql, (val,key))
				self.conn.commit()
		except Exception as e:
			self.__close()
			raise e


	def getConfigDict(self) -> dict:
		"""Get all configuration options as a dictionary"""
		sql = f'SELECT {TBL_CONFIG_KEY}, ' \
				f'{TBL_CONFIG_VALUE} ' \
				f'FROM {TBL_CONFIG} ' \
				f'ORDER BY {TBL_CONFIG_KEY} ASC'
		rtrn = { }
		try:
			self.__open()
			with self.conn.cursor() as cur:
				cur.execute(sql)
				for record in cur:
					rtrn[record[0]] = record[1]
		except Exception as e:
			self.__close()
			raise e
		return rtrn

	def getLibraryList(self, start=0, limit=10) -> list:
		"""Get list of songs in the sound library"""
		if start < 0 or limit < 1:
			raise ValueError('Must give start>0 and limit>1')
		sql = f'SELECT {TBL_LIBRARY_ID}, {TBL_LIBRARY_NAME}, ' \
				f'{TBL_LIBRARY_LENGTH}, {TBL_LIBRARY_TIME} ' \
				f'FROM {TBL_LIBRARY} ' \
				f'ORDER BY {TBL_LIBRARY_NAME} ASC ' \
				f'LIMIT {limit} OFFSET {start}'
		rtrn = [ ]
		try:
			self.__open()
			with self.conn.cursor() as cur:
				cur.execute(sql)
				rtrn = cur.fetchall()
		except Exception as e:
			self.__close()
			raise e
		return rtrn

	def addToLibrary(self, name: str, desc: str, soundFile: Path) -> int:
		"""Convert a song to mp3 and add it to the db library"""
		sql = f'INSERT INTO {TBL_LIBRARY}({TBL_LIBRARY_NAME}, ' \
				f'{TBL_LIBRARY_DESC}, {TBL_LIBRARY_DATA}) ' \
				f'VALUES (%s, %s, %s)'
		mp3File = soundToMP3(soundFile)
		try:
			self.__open()
			with self.conn.cursor() as cur, open(mp3File) as f:
				cur.execute(sql, (name, desc, f.read()))
			if mp3File is not None:
				remove(mp3File)
		except Exception as e:
			self.__close()
			raise e
		# TODO: get the id from new song in library and return it to user
		raise NotImplementedError('Added song to library, but currently cannot return ID')

if __name__ == '__main__':
	print("Use this package as a library only")
	exit(1)

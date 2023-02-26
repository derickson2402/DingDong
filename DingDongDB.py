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
TBL_CONFIG_COL_VALUE = 'ConfigValue'
TBL_CONFIG_KEY = 'ConfigName'
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
		if key not in TBL_CONFIG_VALID_KEYS:
			raise KeyError(f'{key} is not a valid key')
		sql = f'SELECT {TBL_CONFIG_COL_VALUE} FROM {TBL_CONFIG} WHERE ' \
				f'{TBL_CONFIG_KEY} = %s'
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
		if key not in TBL_CONFIG_VALID_KEYS:
			raise KeyError(f'{key} is not a valid key')
		sql = f'UPDATE {TBL_CONFIG} ' \
				f'SET {TBL_CONFIG_COL_VALUE} = %s ' \
				f'WHERE {TBL_CONFIG_KEY} = "%s";'
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
		sql = f'SELECT {TBL_CONFIG_KEY}, ' \
				f'{TBL_CONFIG_COL_VALUE} ' \
				f'FROM {TBL_CONFIG} ' \
				f'ORDER BY {TBL_CONFIG_KEY} ASC'
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

	def getLibraryList(self, start=0, limit=10) -> list:
		"""Get list of songs in the sound library"""
		if start < 0 or limit < 1:
			raise ValueError('Must give start>0 and limit>1')
		sql = f'SELECT {TBL_LIBRARY_ID}, {TBL_LIBRARY_NAME}, ' \
				f'{TBL_LIBRARY_LENGTH}, {TBL_LIBRARY_TIME} ' \
				f'FROM {TBL_LIBRARY} ' \
				f'ORDER BY {TBL_LIBRARY_NAME} ASC ' \
				f'LIMIT {limit} OFFSET {start}'
		cur = self.db.cursor()
		rtrn = [ ]
		try:
			cur.execute(sql)
			rtrn = cur.fetchall()
		except Exception as e:
			rtrn = None
			raise
		finally:
			cur.close()
		return rtrn

	def addToLibrary(self, name: str, desc: str, soundFile: Path) -> int:
		"""Convert a song to mp3 and add it to the db library"""
		sql = f'INSERT INTO {TBL_LIBRARY}({TBL_LIBRARY_NAME}, ' \
				f'{TBL_LIBRARY_DESC}, {TBL_LIBRARY_DATA}) ' \
				f'VALUES (%s, %s, %s)'
		mp3File = soundToMP3(soundFile)
		cur = self.db.cursor()
		try:
			with open(mp3File) as f:
				cur.execute(sql, (name, desc, f.read()))
		except Exception as e:
			raise
		finally:
			cur.close()
			remove(mp3File)
		id = -1
		return id

if __name__ == '__main__':
	print("Use this package as a library only")
	exit(1)

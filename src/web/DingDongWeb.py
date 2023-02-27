#!/usr/local/bin/python
"""#############################################################################

Date
	31 January 2023
 
Author(s)
	Dan Erickson (dan@danerick.com)

Description
	Hosts a basic web interface and API for storing the sound library and
	configuration options for DingDong.

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

from flask import Flask, render_template, send_file, jsonify, request
from flask_restful import Resource, Api, reqparse
from werkzeug.utils import secure_filename
from os import path, getenv, remove
from pathlib import Path
from tempfile import NamedTemporaryFile
import ast
import json
from DingDongDB import DingDongDB

# We must be running on Linux (preferrably in a container)
from platform import system
if not system() == 'Linux':
	print(f"FATAL: program must be run on Linux, does not support {system()}")
	exit(1)
del system

# Load settings from env, as we are running in container
API_BASE_URL = path.join('/', getenv('API_BASE_URL', 'api').strip('/'))
DB_HOST = getenv('DB_HOST')
DB_PASSWORD = getenv('DB_PASSWORD')
if DB_PASSWORD is None:
	DB_PASSWORD = getenv('POSTGRES_PASSWORD')
if DB_HOST is None or DB_PASSWORD is None:
	print('FATAL: set the DB_HOST and DB_PASSWORD env variables')
	exit(1)

# Connect to database backend
try:
	db = DingDongDB(DB_HOST, DB_PASSWORD)
except Exception as e:
	print('FATAL: could not connect to database backend')
	exit(1)

# Now we are ready, configure the server
app = Flask(__name__)
api = Api(app)

class Config(Resource):
	"""API endpoint for managing doorbell configuration"""
	def get(self):
		"""Give client current configuration options and values"""
		try:
			rtrn = db.getConfigDict()
			return {'config': rtrn}, 200
		except:
			app.logger.error('Could not get config from db')
			return {'message': 'Failure to get configuration'}, 500
	def post(self):
		"""Client updates the current configuration"""
		rqst = request.get_json()
		try:
			for key, val in rqst.items():
				db.setConfigValue(key, val)
			return {'config', rqst}, 200
		except:
			app.logger.error(f'Could not update config with {rqst}')
			return {'message': 'Failure to set configuration'}, 500

class Libary(Resource):
	"""API endpoint for managing sound effect library"""
	def get(self):
		"""Give client list of available sounds in library"""
		args = request.args
		try:
			start = args.get('start', default=0, type=int)
			limit = args.get('limit', default=10, type=int)
		except:
			return {'message': 'Invalid parameters provided'}, 400
		try:
			libList = db.getLibraryList(start, limit)
			return {'size': limit, 'library': libList}, 200
		except:
			return {'message': 'Failure to get library'}, 500

	def post(self):
		"""Client adds a new sound to the library"""
		parser = reqparse.RequestParser()
		parser.add_argument('name', required=True)
		parser.add_argument('file_name', required=True)
		parser.add_argument('description', required=True)
		args = request.args
		if 'file' not in request.files:
			return {'message': 'No file uploaded'}, 400
		recvFile = request.files['file']
		if recvFile.filename == '' or recvFile.filename is None:
			return {'message': 'No file uploaded'}, 400
		if Path(recvFile.filename).suffix not in ['mp4', 'mp3', 'wav', 'aac',
				'pcm', 'aiff', 'flac', 'alac']:
			return {'message': 'File type not valid'}, 400
		# Create temporary file to save to, then close it later
		try:
			tempFile = NamedTemporaryFile(mode='w+b', delete=False)
			tempFile.close()
			recvFile.save(tempFile.name)
			soundID = db.addToLibrary(
					args['name'],
					args['description'],
					Path(tempFile.name))
		except:
			return {'message': 'Could not upload file'}, 500
		finally:
			try: remove(tempFile.name)
			except: pass
		return {'name': args['name'], 'description': args['description'],
				'soundID': soundID}, 200

class IndexAPI(Resource):
	"""Helpful messages and status at the API Index"""
	def get(self):
		return {'status': 'OK'}, 200

@app.route('/')
def webIndex():
	return f'Pardon the dust, but this site is still being built! You can ' \
			'try our API at {API_BASE_URL} if you want!'

api.add_resource(Libary, path.join(API_BASE_URL, 'library'))
api.add_resource(IndexAPI, API_BASE_URL)

if __name__ == '__main__':
	app.run()
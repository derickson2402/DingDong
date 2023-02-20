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

from flask import Flask, render_template, send_file
from flask_restful import Resource, Api, reqparse
from os import path, getenv, mkdir, mknod
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
if DB_HOST is None or DB_PASSWORD is None:
	print('FATAL: set the DB_HOST and DB_PASSWORD env variables')
	exit(1)

# Connect to database backend
try:
	db = DingDongDB(DB_HOST, DB_PASSWORD)
except Exception as e:
	print('FATAL: could not connect to database backend')
	raise

# Now we are ready, configure the server
app = Flask(__name__)
api = Api(app)

class Config(Resource):
	"""API endpoint for managing doorbell configuration"""
	def get(self):
		"""Give client current configuration options and values"""
		return {'config': db.getConfigDict()}, 200
	def post(self):
		"""Client updates the current configuration"""
		parser = reqparse.RequestParser()
		parser.add_argument('option')
		args = parser.parse_args()
		return {'message': 'method not yet implemented'}, 404

class Libary(Resource):
	"""API endpoint for managing sound effect library"""
	def get(self):
		"""Give client list of available sounds in library"""
		return {'size': len(libDict), 'library': libDict}, 200
	def post(self):
		"""Client adds a new sound to the library"""
		parser = reqparse.RequestParser()
		parser.add_argument('name', required=True)
		parser.add_argument('file_name', required=True)
		parser.add_argument('description', required=True)
		args = parser.parse_args()
		try:
			libDict[libIDSeq] = {
				'name': args['name'],
				'file_name': args['file_name'],
				'description': args['description']
			}
			libIDSeq += 1
		except:
			print(f"ERROR: {path.join(API_BASE_URL, 'library')} POST could not add '{args['name']}' because it exists already")
			return {'message': f"could not add {args['name']}"}, 401
		return {'library': libDict}, 201
	pass

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
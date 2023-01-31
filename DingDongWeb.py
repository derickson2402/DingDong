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
	https://github.com/derickson2402/EECS388-Project-1.git
 
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

# We must be running on Linux (preferrably in a container)
from platform import system
if not system() == 'Linux':
	print(f"FATAL: program must be run on Linux, does not support {system()}")
	exit(1)
del system

# Load settings from env, as we are running in container
API_BASE_URL = path.join('/', getenv('API_BASE_URL', 'api').strip('/'))
LIB_DIR = path.join('/', getenv('LIBRARY_DIRECTORY', 'library').strip('/'))
LIB_CONF_FILE = getenv('LIB_CONF_FILE', 'dingdongconfig.json')

# Verify we can access the library folder
if not path.exists(LIB_DIR):
	try:
		print(f"WARNING: library directory '{LIB_DIR}' does not exist, creating it")
		mkdir(LIB_DIR)
	except:
		print(f"FATAL: could not create directory '{LIB_DIR}'")
		exit(1)

# Read in the configuration file
libDict = { }
configDict = { }
libIDSeq = 0
tempDict = { }
if path.isfile(LIB_CONF_FILE):
	try:
		with open(LIB_CONF_FILE) as f:
			tempDict = json.load(f)
	except:
		print(f"FATAL: could not read config file '{LIB_CONF_FILE}'")
		exit(1)

# Set up default config and override it with config file if it was found
if 'library' in tempDict.keys():
	libDict = tempDict['library']
else:
	libDict = { }
libDict = tempDict['library'] if ('library' in tempDict.keys()) else { }
libIDSeq = tempDict['id_seq'] if ('id_seq' in tempDict.keys()) else len(libDict)
configDict = tempDict['config'] if ('config' in tempDict.keys()) else {'sound': None, 'volume': 0.5 }

# Write back to config file to make sure it is well-formed and is not missing new settings
try:
	with open(LIB_CONF_FILE, "w") as f:
		json.dump({'id_seq': libIDSeq, 'library': libDict, 'config': configDict}, f)
except:
	print(f"FATAL: could not create config file '{LIB_CONF_FILE}'")
	exit(1)

# Now we are ready, configure the server
app = Flask(__name__)
api = Api(app)

class Config(Resource):
	"""API endpoint for managing doorbell configuration"""
	def get(self):
		"""Give client current configuration options and values"""
		return {'config': configDict}, 200
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
	return f'Pardon the dust, but this site is still being built! You can try our API at {API_BASE_URL} if you want!'

api.add_resource(Libary, path.join(API_BASE_URL, 'library'))
api.add_resource(IndexAPI, API_BASE_URL)

if __name__ == '__main__':
	app.run()
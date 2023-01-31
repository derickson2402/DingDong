from flask import Flask
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
API_URL = path.join('/', getenv('API_URL', 'api').strip("/"))
LIB_DIR = getenv('LIBRARY_DIRECTORY', 'dingdonglib')
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
libIDSeq = 0
if path.isfile(LIB_CONF_FILE):
	try:
		with open(LIB_CONF_FILE) as f:
			tempDict = json.load(f)
			libDict = tempDict['library']
			libIDSeq = tempDict['id_seq']
	except:
		print(f"FATAL: could not read config file '{LIB_CONF_FILE}'")
		exit(1)
else:
	try:
		print(f"WARNING: no config file found, creating it as '{LIB_CONF_FILE}'")
		with open(LIB_CONF_FILE, "w") as f:
			json.dump({'id_seq': libIDSeq, 'library': libDict}, f)
	except:
		print(f"FATAL: could not create config file '{LIB_CONF_FILE}'")
		exit(1)

# Now we are ready, configure the server
app = Flask(__name__)
api = Api(app)


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
			print(f"ERROR: {path.join(API_URL, 'library')} POST could not add '{args['name']}' because it exists already")
			return {'message': f"could not add {args['name']}"}, 401
		return {'library': libDict}, 201
	pass

api.add_resource(Libary, path.join(API_URL, 'library'))

if __name__ == '__main__':
	app.run()
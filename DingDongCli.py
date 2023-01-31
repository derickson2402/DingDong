#!/usr/local/bin/python
"""#############################################################################
Date
	31 February 2023
 
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

from os import path, getenv
import requests
import time

# Load settings from env, as we are running in container
try:
	API_URL = path.join('/', getenv('API_URL').strip('/'))
	POLL_INTERVAL = getenv('POLL_INTERVAL', 30)
except:
	print("FATAL: please specify $API_URL environment variable")
confDict = {'volume': '50', 'currentSound': None}

def checkIn():
	"""Ping the API for updates, download new sounds if needed"""
	url = path.join(API_URL, 'config')
	r = requests.get(url)
	if not r.status_code == 200:
		print(f"ERROR: got {r.status_code} during GET to {url}")
		return
	# Update our local config from response
	confDict['volume'] = r.json()['volume']
	if not confDict['currentSound'] == r.json()['currentSound']:
		if downloadSound():
			print(f"ERROR: failed to download new sound. Skipping update...")
		else:
			confDict['currentSound'] = r.json()['currentSound']
	return

def downloadSound() -> bool:
	"""Download the currentSound from API and set it locally. Returns True on success"""
	url = path.join(API_URL, 'download')
	r = requests.get(url)
	if not r.status_code == 200:
		print(f"ERROR: got {r.status_code} during GET to {url}")
		return False
	try:
		open('currentSound.mp3', 'wb').write(r.content)
	except:
		print(f"ERROR: could not save file after receiving from {url}")
		return False
	return True

if __name__ == '__main__':
	epoch = time.time()
	i = 0
	while True:
		time.sleep(epoch + i*POLL_INTERVAL - time.time())
		checkIn()

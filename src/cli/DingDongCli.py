#!/usr/local/bin/python
"""#############################################################################

Date
	15 April 2023
 
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

from os import path, getenv, environ
import requests
import time
# not allowed to execute RPi libary in dev container, so simulate doorbell with
# keyboard buttons instead
if not 'DEV_CONTAINER' in environ:
	import RPi.GPIO as GPIO
from pygame import mixer
import threading

# Load settings from env, as we are running in container
try:
	API_URL = getenv('API_URL')
	if API_URL is None:
		print("Make sure to specify $API_URL environment variable")
		exit(1)
	elif not API_URL[0:4] == 'http':
		API_URL = 'https://' + API_URL
	POLL_INTERVAL = int(getenv('POLL_INTERVAL', 30))
	BELL_PIN = int(getenv('DOORBELL_PIN', 16))
	SOUND_FILE = 'CurrentSound.mp3'
except:
	print("FATAL: could not parse env vars")
	exit(1)
confDict = {'Volume': '50', 'CurrentSound': None}

# Boot the audio device if we are on the Pi, audio doesnt work in container
if not 'DEV_CONTAINER' in environ:
	try:
		mixer.init()
	except Exception as e:
		print(e)
		print("FATAL: could not start the audio engine")
		exit(1)

def checkIn() -> None:
	"""Ping the API for updates, download new sounds if needed"""
	url = path.join(str(API_URL), 'config')
	print(f'pinging {url}')
	r = requests.get(url)
	print(f'got status {r.status_code}')
	if not r.status_code == 200:
		raise ConnectionError(f'ERROR: got {r.status_code} during GET to {url}')
	# Update our local config from response
	confDict['Volume'] = r.json()['Volume']
	if not confDict['CurrentSound'] == r.json()['CurrentSound']:
		if downloadSound():
			raise ConnectionAbortedError(f'ERROR: failed to download new sound. Skipping update...')
		else:
			confDict['CurrentSound'] = r.json()['CurrentSound']
	return

def downloadSound() -> bool:
	"""Download the CurrentSound from API and set it locally. Returns True on success"""
	url = path.join(str(API_URL), 'download')
	r = requests.get(url)
	if not r.status_code == 200:
		print(f"ERROR: got {r.status_code} during GET to {url}")
		return False
	try:
		open(SOUND_FILE, 'wb').write(r.content)
	except:
		print(f"ERROR: could not save file after receiving from {url}")
		return False
	return True

def threadCheckIn():
	"""Daemon that periodically fetches new sounds from remote API.
	Calls checkIn()"""
	epoch = time.time()
	i = 0
	while True:
		time.sleep(epoch + i*POLL_INTERVAL - time.time())
		checkIn()

def ringBell() -> None:
	"""Reset sound playback and play the doorbell noise. Exits immediately."""
	if 'DEV_CONTAINER' in environ:
		print(f'Debug: {confDict["CurrentSound"]} at {confDict["volume"]} volume')
	else:
		mixer.stop()
		sound = mixer.Sound(SOUND_FILE)
		sound.set_volume(confDict['Volume'] * 0.01)
		sound.play()
	return

def threadListenBell():
	"""Daemon listening for doorbell press, triggers the doorbell sound to
	play"""
	if 'DEV_CONTAINER' in environ:
		while True:
			input() # halt until user hits enter
			ringBell()
	else:
		# Can safely ignore errors below, since we know we are not on a Pi
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(BELL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		while True:
			GPIO.wait_for_edge(BELL_PIN, GPIO.FALLING)
			ringBell()

if __name__ == '__main__':
	# Get initial config then start up the daemon
	try:
		checkIn()
	except Exception as e:
		print(e)
		print("FATAL: Failed to get intitial configuration")
		exit(1)
	handlerCheckIn = threading.Thread(target=threadCheckIn, daemon=True)
	handlerListenDoorbell = threading.Thread(target=threadListenBell,daemon=True)
	handlerCheckIn.run()
	handlerListenDoorbell.run()

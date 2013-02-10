import logging
from FileProcessor import FileProcessor

__author__ = 'dur'

NAME = "StandardHostDC: "

def execute(paramsDictionary):
	logging.error(NAME+ "Wlaczam dodatkowe opcje przy odlaczaniu serwera")
	file = FileProcessor(paramsDictionary["HOME_PATH"]+"ServerSide/config/addresses.conf")
	if( paramsDictionary["CONNECTION_MODE"] == True ):
		paramsDictionary["CONNECTION"]._socket.close()
	logging.error(NAME+ "trying to write to addresses file")
	file.lockFile()
	addresses = file.readFile()
	for key in addresses:
		if key == paramsDictionary["CLIENT_ADDRESS"]:
			addresses[key] = 'F'
			file.writeToFile(addresses)
			file.unlockFile()
			logging.error(NAME+ "wrote to addresses file")
	if file.lock.is_locked:
		file.unlockFile()

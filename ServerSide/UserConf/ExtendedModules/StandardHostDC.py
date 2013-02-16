import logging
from FileProcessor import FileProcessor

__author__ = 'dur'

NAME = "StandardHostDC: "

def execute(paramsDictionary, message):
	logging.error(NAME+ "Wlaczam dodatkowe opcje przy odlaczaniu serwera")
	file = FileProcessor(paramsDictionary["HOME_PATH"]+"ServerSide/config/addresses.conf")
	if( paramsDictionary["CONNECTION_MODE"] == True ):
		paramsDictionary["CONNECTION"]._socket.close()
	logging.error(NAME+ "trying to write to addresses file")
	file.lockFile()
	addresses = file.readFile()
	addresses[paramsDictionary["CLIENT_ADDRESS"]] = 'F'
	file.writeToFile(addresses)
	file.unlockFile()
	logging.error(NAME+ "wrote to addresses file")
	if file.lock.is_locked:
		file.unlockFile()

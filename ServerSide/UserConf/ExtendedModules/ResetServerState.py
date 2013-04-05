import logging
from utils.FileProcessors import FileProcessor

__author__ = 'dur'
NAME = "ResetServerState: "

def execute(paramsDictionary, message):
	logging.info(NAME + "Reseting server state")
	file = FileProcessor(paramsDictionary["HOME_PATH"]+"ServerSide/config/addresses.conf")
	file.lockFile()
	addresses = file.readFile()
	for key in addresses:
		addresses[key] = 'F'
	file.writeToFile(addresses)
	file.unlockFile()
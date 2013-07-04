from utils.FileProcessors import FileProcessor
import utils.Logger as logger

__author__ = 'dur'
NAME = "ResetServerState: "

def execute(paramsDictionary, message):
	logger.logInfo(NAME + "Resetuje stan serwera")
	file = FileProcessor(paramsDictionary["HOME_PATH"]+"ServerSide/config/addresses.conf")
	file.lockFile()
	addresses = file.readFile()
	for key in addresses:
		addresses[key] = 'F'
	file.writeToFile(addresses)
	file.unlockFile()
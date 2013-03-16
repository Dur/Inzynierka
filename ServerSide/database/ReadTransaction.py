import logging
import math
from utils.FileProcessors import FileProcessor

__author__ = 'dur'

NAME = "ReadTransaction: "
LOCALHOST_NAME = "localhost"

class ReadTransaction:

	paramsDictionary = {}

	def __init__(self, paramsDictionary):
		self.paramsDictionary = paramsDictionary

	def checkDataVersions(self):
		homePath = self.paramsDictionary["HOME_PATH"]

		logging.error(NAME+ "Rozpoczynanie transakcji odczytu")
		processor = FileProcessor(homePath+"ServerSide/config/database_config/data_version.dat")
		processor.lockFile()
		dataVersions = processor.readFile()
		myDataVersion = dataVersions[LOCALHOST_NAME]
		logging.error("Lokalna wersja danych = " + myDataVersion)
		count = 0
		myVersion = 0
		for key in dataVersions:
			count = count + 1
			version = dataVersions[key]
			if version == myDataVersion:
				myVersion = myVersion + 1
		logging.error(NAME + "Zgodnych wersji: " + str(myVersion))
		logging.error(NAME + "Wszystkich wersji: " + str(count))
		processor.unlockFile()
		min = int(math.floor(count/2) + 1)
		if myVersion >= min:
			logging.error(NAME + "Mozna czytac")
			return True
		else:
			logging.error(NAME + "Nie mozna czytac")
			return False


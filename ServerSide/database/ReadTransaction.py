import MySQLdb
import math
import utils.Logger as logger
from utils.FileProcessors import FileProcessor

__author__ = 'dur'

NAME = "ReadTransaction: "
LOCALHOST_NAME = "localhost"
ERROR_MESSAGE = "Sorry, but server is temporary unavailable, please try again later"

class ReadTransaction:
	paramsDictionary = {}

	def __init__(self, paramsDictionary):
		self.paramsDictionary = paramsDictionary
		homePath = self.paramsDictionary["HOME_PATH"]
		self.processor = FileProcessor(homePath + "ServerSide/config/database_config/data_version.dat")
		self.addressesProcessor = FileProcessor(homePath + "ServerSide/config/addresses.conf")

	def executeTransaction(self, cursor, command):
		try:
			if self.checkActiveServersCount() == True and self.checkDataVersions() == True:
				cursor.execute(command)
				return cursor.fetchall()
			else:
				return ERROR_MESSAGE
		except MySQLdb.Error, e:
			logger.logError(NAME + "%d %s" % (e.args[0], e.args[1]))
			return "%d %s" % (e.args[0], e.args[1])

	def checkDataVersions(self):
		logger.logInfo(NAME + "Rozpoczynanie transakcji odczytu")
		self.processor.lockFile()
		dataVersions = self.processor.readFile()
		myDataVersion = dataVersions[LOCALHOST_NAME]
		logger.logInfo("Lokalna wersja danych = " + myDataVersion)
		count = 0
		myVersion = 0
		for key in dataVersions:
			count = count + 1
			version = dataVersions[key]
			if version == myDataVersion:
				myVersion = myVersion + 1
		logger.logInfo(NAME + "Zgodnych wersji: " + str(myVersion))
		logger.logInfo(NAME + "Wszystkich wersji: " + str(count))
		self.processor.unlockFile()
		min = int(math.floor(count / 2) + 1)
		if myVersion >= min:
			logger.logInfo(NAME + "Mozna czytac")
			return True
		else:
			logger.logError(NAME + "Nie mozna czytac")
			return False

	def checkActiveServersCount(self):
		self.addressesProcessor.lockFile()
		addresses = self.addressesProcessor.readFile()
		self.addressesProcessor.unlockFile()
		all = 1
		available = 1
		for key in addresses:
			all = all + 1
			if addresses[key] == 'T':
				available = available + 1
		min = int(math.floor(all / 2) + 1)
		if available >= min:
			logger.logImportant(NAME + "Wicej niz polowa serwerow aktywna, mozna wykonac operacje")
			return True
		else:
			logger.logImportant(NAME + "Mniej niz polowa serwerow aktywna, nie mozna wykonac operacji")
			return False

	def __del__(self):
		self.processor.unlockFile()
		self.addressesProcessor.unlockFile()

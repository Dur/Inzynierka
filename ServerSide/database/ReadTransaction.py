import MySQLdb
import math
import logging
from utils.FileProcessors import FileProcessor

__author__ = 'dur'

NAME = "ReadTransaction: "
LOCALHOST_NAME = "localhost"
ERROR_MESSAGE = "Sorry but database is not consistent, please try again later"

class ReadTransaction:
	paramsDictionary = {}

	def __init__(self, paramsDictionary):
		self.paramsDictionary = paramsDictionary
		homePath = self.paramsDictionary["HOME_PATH"]
		self.processor = FileProcessor(homePath + "ServerSide/config/database_config/data_version.dat")

	def executeTransaction(self, cursor, command):
		try:
			if self.checkDataVersions() == True:
				cursor.execute(command)
				return cursor.fetchall()
			else:
				return ERROR_MESSAGE
		except MySQLdb.Error, e:
			logging.error(NAME + "%d %s" % (e.args[0], e.args[1]))
			return "%d %s" % (e.args[0], e.args[1])

	def checkDataVersions(self):
		logging.info(NAME + "Rozpoczynanie transakcji odczytu")
		self.processor.lockFile()
		dataVersions = self.processor.readFile()
		myDataVersion = dataVersions[LOCALHOST_NAME]
		logging.info("Lokalna wersja danych = " + myDataVersion)
		count = 0
		myVersion = 0
		for key in dataVersions:
			count = count + 1
			version = dataVersions[key]
			if version == myDataVersion:
				myVersion = myVersion + 1
		logging.info(NAME + "Zgodnych wersji: " + str(myVersion))
		logging.info(NAME + "Wszystkich wersji: " + str(count))
		self.processor.unlockFile()
		min = int(math.floor(count / 2) + 1)
		if myVersion >= min:
			logging.info(NAME + "Mozna czytac")
			return True
		else:
			logging.error(NAME + "Nie mozna czytac")
			return False

	def __del__(self):
		self.processor.unlockFile()

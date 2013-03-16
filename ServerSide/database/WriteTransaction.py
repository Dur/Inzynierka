from Queue import Queue
from threading import Event
import threading.Event
import math
from utils.FileProcessors import FileProcessor
import logging

__author__ = 'dur'

NAME = "WriteTransaction: "
LOCALHOST_NAME = "localhost"
PREPARE = "PREPARE"
GLOBAL_COMMIT = "GLOBAL_COMMIT"
ABORT = "ABORT"
GLOBAL_ABORT = "GLOBAL_ABORT"
OK = "OK"

class WriteTransaction:

	responseQueue = None
	requestQueue = None
	eventVariable = Event()
	paramsDictionary = None
	versionProcessor = None
	addressesProcessor = None
	serversCount = 0
	activeServers = []


	def __init__(self, paramsDictionary):
		homePath = paramsDictionary["HOME_PATH"]
		self.paramsDictionary = paramsDictionary
		self.versionProcessor = FileProcessor(homePath + "ServerSide/config/database_config/data_version.dat")
		self.addressesProcessor = FileProcessor(homePath + "ServerSide/config/addresses.conf")


	def executeTransaction(self, cursor, command):
		if self.chceckTransactionPossibility() == True:
			pass

	def chceckTransactionPossibility(self):
		if self.checkActiveServersCount() and self.chceckDataVersions():
			return True
		else:
			return False

	def checkActiveServersCount(self):
		self.addressesProcessor.lockFile()
		addresses = self.addressesProcessor.readFile()
		all = 0
		available = 0
		for key in addresses:
			all = all + 1
			if addresses[key] == 'T':
				self.availableServers.append(key)
				available = available + 1
		self.addressesProcessor.unlockFile()
		self.serversCount = all + 1
		min = int(math.floor(all / 2) + 1)
		if available >= min:
			logging.error(NAME + "Wicej niz polowa serwerow aktywna")
			return True
		else:
			logging.error(NAME + "mniej niz polowa serwerow aktywna")
			return False

	def chceckDataVersions(self, activeServerList):
		self.versionProcessor.lockFile()
		dataVersions = self.versionProcessor.readFile()
		myDataVersion = dataVersions[LOCALHOST_NAME]
		logging.error("Lokalna wersja danych = " + myDataVersion)
		myVersion = 0
		for key in activeServerList:
			version = dataVersions[key]
			if version == myDataVersion:
				myVersion = myVersion + 1
		logging.error(NAME + "Zgodnych wersji: " + str(myVersion))
		logging.error(NAME + "Wszystkich wersji: " + str(self.serversCount))
		self.processor.unlockFile()
		min = int(math.floor(self.serversCount / 2) + 1)
		if myVersion >= min:
			logging.error(NAME + "Mozna wykonac transakcje zapisu")
			return True
		else:
			logging.error(NAME + "Nie mozna wykonac transakcji zapisu")
			return False
import MySQLdb
from Queue import Queue
from threading import Event
import math
from database.WriteTransactionThread import WriteTransactionThread
from utils.FileProcessors import FileProcessor
import logging

__author__ = 'dur'

NAME = "WriteTransaction: "
LOCALHOST_NAME = "localhost"
PREPARE_MESSAGE = "PREPARE"
GLOBAL_COMMIT = "GLOBAL_COMMIT"
ABORT = "ABORT"
GLOBAL_ABORT = "GLOBAL_ABORT"
OK = "OK"
OK_MESSAGE = "Query executed successfully"
COMMMIT = "commit"
CONNECTION_PROBLEM_ERROR = "Sorry, but server is temporary unavailable, please try again later"

class WriteTransaction:

	responseQueue = None
	eventVariable = Event()
	paramsDictionary = None
	versionProcessor = None
	addressesProcessor = None
	serversCount = 0
	activeServers = []
	initialised = False
	connectionsQueues = {}
	threads = {}
	waitForRemoteTime = 0
	myDataVersion = 0

	def __init__(self, paramsDictionary):
		homePath = paramsDictionary["HOME_PATH"]
		self.paramsDictionary = paramsDictionary
		self.versionProcessor = FileProcessor(homePath + "ServerSide/config/database_config/data_version.dat")
		self.addressesProcessor = FileProcessor(homePath + "ServerSide/config/addresses.conf")
		self.waitForRemoteTime = int(paramsDictionary["DB_PARAMS"]["waitForRemoteTime"])
		self.eventVariable.clear()


	def executeTransaction(self, cursor, command):
		if self.chceckTransactionPossibility() == True:
			try:
				cursor.execute(command)
			except MySQLdb.Error, e:
				cursor.execute("rollback")
				logging.error(NAME + "Rzucilo wyjatkiem SQL")
				logging.error(NAME + "%d %s" % (e.args[0], e.args[1]))
				return "%d %s" % (e.args[0], e.args[1])

			if self.initialised == False:
				self.initialise()
			self.paramsDictionary["ACTIVE_SERVERS"] = self.activeServers
			for address in self.activeServers:
				self.connectionsQueues[address].put(PREPARE_MESSAGE)
				self.connectionsQueues[address].put(command)
			logging.info(NAME + "Serwer rozpoczyna czekanie na zmiennej warunkowej")
			logging.info(NAME + "Czas oczekiwania na zmiennej warunkowej " + str(self.waitForRemoteTime))
			if self.eventVariable.is_set:
				logging.info(NAME + "Zmienna warunkowa ustawiona")
			else:
				logging.info(NAME + "Zmienna warunkowa NIE ustawiona")
			self.eventVariable.wait(int(self.waitForRemoteTime))
			self.eventVariable.clear()
			logging.info(NAME + "Serwer minal zmienna warunkowa")
			if self.responseQueue.full() != True:
				logging.error(NAME + "Wysylanie GLOBA_ABOT, nie wszystkie serwery odpowiedzialy z zadanym czasie")
				for address in self.activeServers:
					self.connectionsQueues[address].put(GLOBAL_ABORT)
				cursor.execute("rollback")
				return CONNECTION_PROBLEM_ERROR

			while self.responseQueue.empty() != True:
				response = self.responseQueue.get_nowait()
				logging.info(NAME + "Serwer wyciaga kolejne wiadomosci z kolejki")
				if response == ABORT:
					logging.error(NAME + "Wysylanie GLOBAL_ABORT, nie wszystkie serwery sa gotowe do zatwierdzenia transakcji")
					for address in self.activeServers:
						self.connectionsQueues[address].put(GLOBAL_ABORT)
					cursor.execute("rollback")
					return CONNECTION_PROBLEM_ERROR

			activeServersString = ""
			for address in self.activeServers:
				activeServersString = activeServersString + address + ":"

			for address in self.activeServers:
				self.connectionsQueues[address].put(GLOBAL_COMMIT)
				self.connectionsQueues[address].put(activeServersString)
			logging.info(NAME + "przygotowanie insertu do tabeli z wersjami")
			cursor.execute(self.generateInsertToDataVersions(command))
			cursor.execute(COMMMIT)
			self.insertNewDataVersions()
			logging.info(NAME + "Transakcja zakonczona powodzeniem")

			return OK_MESSAGE

	def initialise(self):
		self.responseQueue = Queue(len(self.activeServers))
		for address in self.activeServers:
			requestQueue = Queue()
			logging.info(NAME + "Adres przekazany do watku " + address)
			thread = WriteTransactionThread(self.responseQueue, requestQueue, self.eventVariable, self.paramsDictionary, address)
			self.connectionsQueues[address] = requestQueue
			self.threads[address] = thread
			thread.start()

	def chceckTransactionPossibility(self):
		if self.checkActiveServersCount() and self.checkDataVersions():
			return True
		else:
			return False

	def checkActiveServersCount(self):
		self.activeServers = []
		self.addressesProcessor.lockFile()
		addresses = self.addressesProcessor.readFile()
		all = 1
		available = 1
		for key in addresses:
			all = all + 1
			if addresses[key] == 'T':
				self.activeServers.append(key)
				available = available + 1
		self.addressesProcessor.unlockFile()
		self.serversCount = all + 1
		min = int(math.floor(all / 2) + 1)
		logging.info(NAME + "Aktywne serwery: " + str(self.activeServers))
		if available >= min:
			logging.info(NAME + "Wicej niz polowa serwerow aktywna")
			return True
		else:
			logging.error(NAME + "mniej niz polowa serwerow aktywna")
			return False

	def checkDataVersions(self):
		self.versionProcessor.lockFile()
		dataVersions = self.versionProcessor.readFile()
		self.myDataVersion = dataVersions[LOCALHOST_NAME]
		logging.info("Lokalna wersja danych = " + self.myDataVersion)
		myVersionCount = 1
		for key in self.activeServers:
			version = dataVersions[key]
			if version == self.myDataVersion:
				myVersionCount = myVersionCount + 1
		logging.info(NAME + "Zgodnych wersji: " + str(myVersionCount))
		logging.info(NAME + "Wszystkich wersji: " + str(self.serversCount))
		self.versionProcessor.unlockFile()
		min = int(math.floor(self.serversCount / 2) + 1)
		if myVersionCount >= min:
			logging.info(NAME + "Mozna wykonac transakcje zapisu")
			return True
		else:
			logging.error(NAME + "Nie mozna wykonac transakcji zapisu")
			return False

	def generateInsertToDataVersions(self, command):
		command = command.replace('\'', '\\\'')
		insert = "INSERT INTO " +  self.paramsDictionary["DB_PARAMS"]["versionsTableName"] + " VALUES(" + str((int(self.myDataVersion)+1)) + ",\'" + command + "\')"
		return insert

	def insertNewDataVersions(self):
		self.versionProcessor.lockFile()
		versions = self.versionProcessor.readFile()
		newVersion = str(int(versions[LOCALHOST_NAME]) +1)
		logging.info(NAME + "Nowa wersja danych = " + newVersion)
		for address in self.activeServers:
			versions[address] = newVersion
		versions[LOCALHOST_NAME] = newVersion
		self.versionProcessor.writeToFile(versions)
		self.versionProcessor.unlockFile()
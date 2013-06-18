import MySQLdb
from Queue import Queue
import utils.Logger as logger
from threading import Event
import math
from database.DelayedTransactionThread import DelayedTransactionThread
from database.WriteTransactionThread import WriteTransactionThread
from utils.FileProcessors import FileProcessor
from connections.Connection import Connection
import logging

__author__ = 'dur'

NAME = "WriteTransaction: "
LOCALHOST_NAME = "localhost"
PREPARE_MESSAGE = "PREPARE"
GLOBAL_COMMIT = "GLOBAL_COMMIT"
ABORT = "ABORT"
GLOBAL_ABORT = "GLOBAL_ABORT"
OK = "OK"
COMMIT = "commit"
WAIT = "WAIT"
OK_MESSAGE = "Query executed successfully"
STOP_THREAD = "INTERRUPT"
EXPECTED_TICKET = "expectedTicket"
TICKET_PARAM = "ticketServer"
SKIP = "SKIP"
CONNECTION_PROBLEM_ERROR = "Sorry, but server is temporary unavailable, please try again later"

class WriteTransaction:

	responseQueue = None
	eventVariable = Event()
	paramsDictionary = None
	versionProcessor = None
	addressesProcessor = None
	tempProcessor = None
	serversCount = 0
	activeServers = []
	connectionsQueues = {}
	threads = {}
	waitForRemoteTime = 0
	myDataVersion = 0
	homePath = ""


	def __init__(self, paramsDictionary):
		self.homePath = paramsDictionary["HOME_PATH"]
		self.paramsDictionary = paramsDictionary
		self.versionProcessor = FileProcessor(self.homePath + "ServerSide/config/database_config/data_version.dat")
		self.addressesProcessor = FileProcessor(self.homePath + "ServerSide/config/addresses.conf")
		self.waitForRemoteTime = int(paramsDictionary["DB_PARAMS"]["waitForRemoteTime"])
		self.eventVariable.clear()
		self.tempProcessor = FileProcessor(self.homePath + "ServerSide/config/tempParams.conf")


	def executeTransaction(self, cursor, command):
		logger.logImportant(NAME + "Rozpoczynanie transakcji zapisu")
		if self.chceckTransactionPossibility() == True:
			ticket = self.getTicket()
			logger.logImportant(NAME + "Mam: " + ticket + " Chce: " + self.readTempVars()[EXPECTED_TICKET] )

			if self.readTempVars()[EXPECTED_TICKET] == ticket:
				logger.logImportant(NAME + "Rozpoczynanie normalnej transakcji")
				return self.runNormalTransaction(cursor, command)
			else:
				logger.logImportant(NAME + "Rozpoczynanie odroczonej transakcji")
				return self.runDelayedTransaction(cursor, command, ticket)
		else:
			return CONNECTION_PROBLEM_ERROR

	def runNormalTransaction(self, cursor, command):
		try:
			cursor.execute(command)
		except MySQLdb.Error, e:
			cursor.execute("rollback")
			logger.logImportant(NAME + "Rzucilo wyjatkiem SQL")
			logger.logImportant(NAME + "%d %s" % (e.args[0], e.args[1]))
			return "%d %s" % (e.args[0], e.args[1])

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
			logger.logImportant(NAME + "Wysylanie GLOBA_ABOT, nie wszystkie serwery odpowiedzialy z zadanym czasie")
			for address in self.activeServers:
				self.connectionsQueues[address].put(GLOBAL_ABORT)
				self.connectionsQueues[address].put(STOP_THREAD)
			cursor.execute("rollback")
			return CONNECTION_PROBLEM_ERROR

		while self.responseQueue.empty() != True:
			response = self.responseQueue.get_nowait()
			logging.info(NAME + "Serwer wyciaga kolejne wiadomosci z kolejki")
			if response == ABORT:
				logger.logImportant(NAME + "Wysylanie GLOBAL_ABORT, nie wszystkie serwery sa gotowe do zatwierdzenia transakcji")
				for address in self.activeServers:
					self.connectionsQueues[address].put(GLOBAL_ABORT)
					self.connectionsQueues[address].put(STOP_THREAD)
				cursor.execute("rollback")
				return CONNECTION_PROBLEM_ERROR

		activeServersString = ""
		for address in self.activeServers:
			activeServersString = activeServersString + address + ":"

		for address in self.activeServers:
			self.connectionsQueues[address].put(GLOBAL_COMMIT)
			self.connectionsQueues[address].put(activeServersString)
			self.connectionsQueues[address].put(STOP_THREAD)
		logging.info(NAME + "przygotowanie insertu do tabeli z wersjami")
		cursor.execute(self.generateInsertToDataVersions(command))
		cursor.execute(COMMIT)
		self.insertNewDataVersions()
		logger.logImportant(NAME + "Transakcja zakonczona powodzeniem")
		return OK_MESSAGE

	def runDelayedTransaction(self, cursor, command, ticket):

		self.initaliseDelayed()

		self.paramsDictionary["ACTIVE_SERVERS"] = self.activeServers
		for address in self.activeServers:
			self.connectionsQueues[address].put(ticket)

		logging.info(NAME + "Czas oczekiwania na zmiennej warunkowej " + str(self.waitForRemoteTime))
		self.eventVariable.wait(int(self.waitForRemoteTime))
		self.eventVariable.clear()
		logging.info(NAME + "Serwer minal zmienna warunkowa")
		if self.responseQueue.full() != True or self.readTempVars()[EXPECTED_TICKET] != ticket:
			logging.error(NAME + "Wysylanie SKIP, nie wszystkie serwery odpowiedzialy w zadanym czasie")
			for address in self.activeServers:
				self.connectionsQueues[address].put(SKIP)
				self.connectionsQueues[address].put(STOP_THREAD)
			return CONNECTION_PROBLEM_ERROR

		while self.responseQueue.empty() != True:
			response = self.responseQueue.get_nowait()
			logging.info(NAME + "Serwer wyciaga kolejne wiadomosci z kolejki")
			if response == ABORT:
				logger.logImportant(NAME + "Wysylanie GLOBAL_ABORT, nie wszystkie serwery sa gotowe do zatwierdzenia transakcji")
				for address in self.activeServers:
					self.connectionsQueues[address].put(SKIP)
					self.connectionsQueues[address].put(STOP_THREAD)
				return CONNECTION_PROBLEM_ERROR

		for address in self.activeServers:
			self.connectionsQueues[address].put(OK)
			self.connectionsQueues[address].put(STOP_THREAD)

		return self.runNormalTransaction(cursor, command)

	def initialise(self):
		self.responseQueue = Queue(len(self.activeServers))
		for address in self.activeServers:
			requestQueue = Queue()
			logging.info(NAME + "Adres przekazany do watku " + address)
			thread = WriteTransactionThread(self.responseQueue, requestQueue, self.eventVariable, self.paramsDictionary, address)
			self.connectionsQueues[address] = requestQueue
			self.threads[address] = thread
			thread.start()

	def initialiseDelayed(self):
		self.responseQueue = Queue(len(self.activeServers))
		for address in self.activeServers:
			requestQueue = Queue()
			logging.info(NAME + "Adres przekazany do watku " + address)
			thread = DelayedTransactionThread(self.responseQueue, requestQueue, self.eventVariable, self.paramsDictionary, address)
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
		min = int(math.floor(all / 2) + 1)
		logger.logImportant(NAME + "Aktywne serwery: " + str(self.activeServers))
		if available >= min:
			logger.logImportant(NAME + "Wicej niz polowa serwerow aktywna")
			return True
		else:
			logger.logImportant(NAME + "mniej niz polowa serwerow aktywna")
			return False

	def checkDataVersions(self):
		self.versionProcessor.lockFile()
		dataVersions = self.versionProcessor.readFile()
		self.myDataVersion = dataVersions[LOCALHOST_NAME]
		logger.logImportant("Lokalna wersja danych = " + self.myDataVersion)
		myVersionCount = 1
		for key in self.activeServers:
			version = dataVersions[key]
			if version == self.myDataVersion:
				myVersionCount = myVersionCount + 1
		logger.logImportant(NAME + "Zgodnych wersji: " + str(myVersionCount))
		logger.logImportant(NAME + "Wszystkich wersji: " + str(self.serversCount))
		self.versionProcessor.unlockFile()
		min = int(math.floor(self.serversCount / 2) + 1)
		if myVersionCount >= min:
			logger.logImportant(NAME + "Mozna wykonac transakcje zapisu")
			return True
		else:
			logger.logImportant(NAME + "Nie mozna wykonac transakcji zapisu")
			return False

	def generateInsertToDataVersions(self, command):
		command = command.replace('\'', '\\\'')
		insert = "INSERT INTO " +  self.paramsDictionary["DB_PARAMS"]["versionsTableName"] + " VALUES(" + str((int(self.myDataVersion)+1)) + ",\'" + command + "\')"
		return insert

	def insertNewDataVersions(self):
		self.versionProcessor.lockFile()
		versions = self.versionProcessor.readFile()
		newVersion = str(int(versions[LOCALHOST_NAME]) +1)
		logger.logImportant(NAME + "Nowa wersja danych = " + newVersion)
		for address in self.activeServers:
			versions[address] = newVersion
		versions[LOCALHOST_NAME] = newVersion
		self.versionProcessor.writeToFile(versions)
		self.versionProcessor.unlockFile()

	def getTicket(self):
		connection = Connection("/home/dur/Projects/ServerSide/config/connection_config.conf")
		params = self.readTempVars()
		connection.connect(params[TICKET_PARAM], 80, "/ticket")
		return connection.get_message()

	def readTempVars(self):
		self.tempProcessor.lockFile()
		params = self.tempProcessor.readFile()
		self.tempProcessor.unlockFile()
		return params
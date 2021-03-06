import MySQLdb
from Queue import Queue
from database.utils1 import TicketUtil
import utils.Logger as logger
from threading import Event
import math
from database.DelayedTransactionThread import DelayedTransactionThread
from database.WriteTransactionThread import WriteTransactionThread
from utils.FileProcessors import FileProcessor

__author__ = 'dur'

NAME = "WriteTransaction: "
LOCALHOST_NAME = "localhost"
PREPARE_MESSAGE = "PREPARE"
GLOBAL_COMMIT = "GLOBAL_COMMIT"
ABORT = "ABORT"
GLOBAL_ABORT = "GLOBAL_ABORT"
SKIP_TICKETS = "skipTickets"
OK = "OK"
COMMIT = "commit"
WAIT = "WAIT"
OK_MESSAGE = "Zapytanie zostalo wykonane prawidlowo"
STOP_THREAD = "INTERRUPT"
EXPECTED_TICKET = "expectedTicket"
TICKET_PARAM = "ticketServer"
SKIP = "SKIP"
CONNECTION_PROBLEM_ERROR = "Serwer jest tymczasowo niedostepny, sprobuj ponownie pozniej"
START_TRANSACTION = "START"


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
		logger.logImportant(NAME + "Rozpoczynanie operacji zapisu")
		if self.chceckTransactionPossibility() == True:
			ticket = TicketUtil.getTicket()
			logger.logInfo(NAME + "Otrzymalem bilet: " + ticket + " Ocekiwany bilet: " + TicketUtil.readTempVars()[EXPECTED_TICKET])

			if TicketUtil.readTempVars()[EXPECTED_TICKET] == ticket:
				logger.logInfo(NAME + "Rozpoczynanie normalnej transakcji")
				return self.runNormalTransaction(cursor, command, ticket)
			else:
				logger.logInfo(NAME + "Rozpoczynanie odroczonej transakcji")
				return self.runDelayedTransaction(cursor, command, ticket)
		else:
			return CONNECTION_PROBLEM_ERROR

	def runNormalTransaction(self, cursor, command, ticket):
		try:
			cursor.execute(command)
		except MySQLdb.Error, e:
			cursor.execute("rollback")
			logger.logInfo(NAME + "Rzucilo wyjatkiem SQL")
			logger.logImportant(NAME + "%d %s" % (e.args[0], e.args[1]))
			return "%d %s" % (e.args[0], e.args[1])

		self.initialise()

		self.paramsDictionary["ACTIVE_SERVERS"] = self.activeServers
		for address in self.activeServers:
			self.connectionsQueues[address].put(PREPARE_MESSAGE)
			self.connectionsQueues[address].put(command)

		logger.logInfo(NAME + "Serwer rozpoczyna czekanie na zmiennej warunkowej")
		logger.logInfo(NAME + "Czas oczekiwania na zmiennej warunkowej " + str(self.waitForRemoteTime))
		if self.eventVariable.is_set:
			logger.logInfo(NAME + "Zmienna warunkowa ustawiona")
		else:
			logger.logInfo(NAME + "Zmienna warunkowa NIE ustawiona")
		self.eventVariable.wait(int(self.waitForRemoteTime))
		self.eventVariable.clear()
		logger.logInfo(NAME + "Serwer minal zmienna warunkowa")
		if not self.responseQueue.full():
			logger.logImportant(NAME + "Wysylanie GLOBAL_ABORT, nie wszystkie serwery odpowiedzialy w zadanym czasie")
			for address in self.activeServers:
				self.connectionsQueues[address].put(GLOBAL_ABORT)
				self.connectionsQueues[address].put(ticket)
				self.connectionsQueues[address].put(STOP_THREAD)
			cursor.execute("rollback")
			return CONNECTION_PROBLEM_ERROR

		while self.responseQueue.empty() != True:
			response = self.responseQueue.get_nowait()
			logger.logInfo(NAME + "Serwer wyciaga kolejne wiadomosci z kolejki")
			if response == ABORT:
				logger.logImportant(
					NAME + "Wysylanie GLOBAL_ABORT, nie wszystkie serwery sa gotowe do zatwierdzenia transakcji")
				for address in self.activeServers:
					self.connectionsQueues[address].put(GLOBAL_ABORT)
					self.connectionsQueues[address].put(ticket)
					self.connectionsQueues[address].put(STOP_THREAD)
				cursor.execute("rollback")
				return CONNECTION_PROBLEM_ERROR

		activeServersString = ""
		for address in self.activeServers:
			activeServersString = activeServersString + address + ":"

		for address in self.activeServers:
			self.connectionsQueues[address].put(GLOBAL_COMMIT)
			self.connectionsQueues[address].put(activeServersString)
			self.connectionsQueues[address].put(ticket)
			self.connectionsQueues[address].put(STOP_THREAD)
		logger.logInfo(NAME + "przygotowanie insertu do tabeli z wersjami")
		logger.logImportant(NAME + "Uzyskano zgode od wszystkich uczestnikow")
		cursor.execute(self.generateInsertToDataVersions(command))
		cursor.execute(COMMIT)
		self.insertNewDataVersions()
		TicketUtil.setNextExpectedTicket(ticket)
		logger.logImportant(NAME + "Operacja zakonczona powodzeniem")
		return OK_MESSAGE

	def runDelayedTransaction(self, cursor, command, ticket):

		self.initialiseDelayed()

		self.paramsDictionary["ACTIVE_SERVERS"] = self.activeServers
		for address in self.activeServers:
			self.connectionsQueues[address].put(START_TRANSACTION)
			self.connectionsQueues[address].put(ticket)

		logger.logInfo(NAME + "Czas oczekiwania na zmiennej warunkowej " + str(self.waitForRemoteTime))
		self.eventVariable.wait(int(self.waitForRemoteTime))
		self.eventVariable.clear()
		logger.logInfo(NAME + "Serwer minal zmienna warunkowa")
		if self.responseQueue.full() != True: ########### or TicketUtil.readTempVars()[EXPECTED_TICKET] != ticket:
			logger.logImportant(NAME + "Wysylanie SKIP, nie wszystkie serwery odpowiedzialy w zadanym czasie")
			for address in self.activeServers:
				self.connectionsQueues[address].put(SKIP)
				self.connectionsQueues[address].put(ticket)
				self.connectionsQueues[address].put(STOP_THREAD)
			return CONNECTION_PROBLEM_ERROR

		while self.responseQueue.empty() != True:
			response = self.responseQueue.get_nowait()
			logger.logInfo(NAME + "Serwer wyciaga kolejne wiadomosci z kolejki")
			if response == ABORT:
				logger.logImportant(NAME + "Wysylanie GLOBAL_ABORT, nie wszystkie serwery sa gotowe do zatwierdzenia transakcji")
				for address in self.activeServers:
					self.connectionsQueues[address].put(SKIP)
					self.connectionsQueues[address].put(STOP_THREAD)
				return CONNECTION_PROBLEM_ERROR

		for address in self.activeServers:
			self.connectionsQueues[address].put(OK)
			self.connectionsQueues[address].put(STOP_THREAD)

		return self.runNormalTransaction(cursor, command, ticket)

	def initialise(self):
		self.responseQueue = Queue(len(self.activeServers))
		for address in self.activeServers:
			requestQueue = Queue()
			logger.logInfo(NAME + "Adres przekazany do watku " + address)
			thread = WriteTransactionThread(self.responseQueue, requestQueue, self.eventVariable, self.paramsDictionary,
			                                address)
			self.connectionsQueues[address] = requestQueue
			self.threads[address] = thread
			thread.start()

	def initialiseDelayed(self):
		logger.logInfo(NAME + "Inicjowanie transakcji odroczonej")
		self.responseQueue = Queue(len(self.activeServers))
		for address in self.activeServers:
			requestQueue = Queue()
			logger.logInfo(NAME + "Adres przekazany do watku " + address)
			thread = DelayedTransactionThread(self.responseQueue, requestQueue, self.eventVariable,
			                                  self.paramsDictionary, address)
			self.connectionsQueues[address] = requestQueue
			self.threads[address] = thread
			thread.start()
			logger.logInfo(NAME + "Watek wystartowal")
		logger.logInfo(NAME + "Konczenie inicjalizacji transakcji opoznionej")

	def chceckTransactionPossibility(self):
		if self.checkActiveServersCount() and self.checkDataVersions():
			return True
		else:
			return False

	def checkActiveServersCount(self):
		self.activeServers = []
		self.addressesProcessor.lockFile()
		addresses = self.addressesProcessor.readFile()
		allServers = 1
		available = 1
		for key in addresses:
			allServers = allServers + 1
			if addresses[key] == 'T':
				self.activeServers.append(key)
				available += 1
		self.addressesProcessor.unlockFile()
		minVersion = int(math.floor(allServers / 2) + 1)
		logger.logInfo(NAME + "Aktywne serwery: " + str(self.activeServers))
		self.serversCount = len(addresses) + 1
		if available >= minVersion:
			logger.logImportant(NAME + "Warunek kworum dla zapisu spelniony, mozna przeprowadzic operacje")
			return True
		else:
			logger.logImportant(NAME + "Warunek kworum dla zapisu nie jest spelniony, nie mozna przeprowadzic operacji")
			return False

	def checkDataVersions(self):
		self.versionProcessor.lockFile()
		dataVersions = self.versionProcessor.readFile()
		self.myDataVersion = dataVersions[LOCALHOST_NAME]
		logger.logInfo("Lokalna wersja danych = " + self.myDataVersion)
		myVersionCount = 1
		for key in self.activeServers:
			version = dataVersions[key]
			if version == self.myDataVersion:
				myVersionCount = myVersionCount + 1
		logger.logInfo(NAME + "Zgodnych wersji: " + str(myVersionCount))
		logger.logInfo(NAME + "Wszystkich wersji: " + str(self.serversCount))
		self.versionProcessor.unlockFile()
		minVersion = int(math.floor(self.serversCount / 2) + 1)
		if myVersionCount >= minVersion:
			logger.logInfo(NAME + "Mozna wykonac transakcje zapisu")
			return True
		else:
			logger.logInfo(NAME + "Nie mozna wykonac transakcji zapisu")
			return False

	def generateInsertToDataVersions(self, command):
		command = command.replace('\'', '\\\'')
		insert = "INSERT INTO " + self.paramsDictionary["DB_PARAMS"]["versionsTableName"] + " VALUES(" + str(
			(int(self.myDataVersion) + 1)) + ",\'" + command + "\')"
		return insert

	def insertNewDataVersions(self):
		self.versionProcessor.lockFile()
		versions = self.versionProcessor.readFile()
		newVersion = str(int(versions[LOCALHOST_NAME]) + 1)
		logger.logInfo(NAME + "Nowa wersja danych = " + newVersion)
		for address in self.activeServers:
			versions[address] = newVersion
		versions[LOCALHOST_NAME] = newVersion
		self.versionProcessor.writeToFile(versions)
		self.versionProcessor.unlockFile()
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

	def __init__(self, paramsDictionary):
		homePath = paramsDictionary["HOME_PATH"]
		self.paramsDictionary = paramsDictionary
		self.versionProcessor = FileProcessor(homePath + "ServerSide/config/database_config/data_version.dat")
		self.addressesProcessor = FileProcessor(homePath + "ServerSide/config/addresses.conf")
		self.waitForRemoteTime = paramsDictionary["DB_PARAMS"]["waitForRemoteTime"]


	def executeTransaction(self, cursor, command):
		if self.chceckTransactionPossibility() == True:
			try:
				cursor.execute(command)
			except MySQLdb.Error, e:
				cursor.execute("rollback")
				logging.error(NAME + "%d %s" % (e.args[0], e.args[1]))
				return "%d %s" % (e.args[0], e.args[1])

			if self.initialised == False:
				self.initialise()
			for address in self.activeServers:
				self.connectionsQueues[address].put(PREPARE_MESSAGE)
				self.connectionsQueues[address].put(command)
			self.eventVariable.wait(self.waitForRemoteTime)
			self.eventVariable.clear()

			if self.responseQueue.full() != True:
				logging.error(NAME + "sending global abort, not all of servers responsed")
				for address in self.activeServers:
					self.connectionsQueues[address].put(GLOBAL_ABORT)
				cursor.execute("rollback")
				return CONNECTION_PROBLEM_ERROR

			while self.responseQueue.empty() != True:
				response = self.responseQueue.get_nowait()
				if response == ABORT:
					logging.error(NAME + "sending global abort, not all servers ready for commit")
					for address in self.activeServers:
						self.connectionsQueues[address].put(GLOBAL_ABORT)
					cursor.execute("rollback")
					return CONNECTION_PROBLEM_ERROR

			for address in self.activeServers:
				self.connectionsQueues[address].put(GLOBAL_COMMIT)
			cursor.execute("commit")
			return OK_MESSAGE


	def initialise(self):
		self.responseQueue = Queue(len(self.activeServers))
		for address in self.activeServers:
			requestQueue = Queue()
			thread = WriteTransactionThread(self.responseQueue, requestQueue, self.eventVariable, self.paramsDictionary)
			self.connectionsQueues[address] = requestQueue
			self.threads[address] = thread
			thread.start()

	def chceckTransactionPossibility(self):
		if self.checkActiveServersCount() and self.chceckDataVersions():
			return True
		else:
			return False

	def checkActiveServersCount(self):
		self.addressesProcessor.lockFile()
		addresses = self.addressesProcessor.readFile()
		all = 0
		available = 1
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
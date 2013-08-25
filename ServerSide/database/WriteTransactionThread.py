from threading import Thread
from connections.Connection import Connection
import logging
import utils.Logger as logger

NAME = "WriteTransactionThread: "
STOP_THREAD = "INTERRUPT"
LOCALHOST_NAME = "localhost"
PREPARE = "PREPARE"
GLOBAL_COMMIT = "GLOBAL_COMMIT"
ABORT = "ABORT"
GLOBAL_ABORT = "GLOBAL_ABORT"
OK = "OK"
OK_FLAG = 0
RESOURCE = "/writeTransaction"
EXIT = "EXIT"

class WriteTransactionThread(Thread):

	outputQueue = None
	inputQueue = None
	eventVariable = None
	clientAddress = None
	commands = []

	def __init__(self, outputQueue, inputQueue, eventVariable, paramsDictionary, address):
		Thread.__init__(self)
		self.clientAddress = address
		self.inputQueue = inputQueue
		self.eventVariable = eventVariable
		self.outputQueue = outputQueue
		self.paramsDictionary = paramsDictionary
		self.connection = None
		self.dbLogin = paramsDictionary["LOGIN"]
		self.dbPassword = paramsDictionary["PASSWORD"]

	def run(self):
		try:
			methodMapping = {PREPARE : self.prepare,
			                 GLOBAL_COMMIT : self.globalCommit,
			                 GLOBAL_ABORT : self.globalAbort}

			self.connection = Connection(self.paramsDictionary["HOME_PATH"]+"ServerSide/config/database_config/transaction_config.conf")
			if self.connection.connect(self.clientAddress, 80, RESOURCE) == OK_FLAG:
				logging.info(NAME + "Polaczenie dla transakcji zapisu nawiazane")
				self.connection.send_message(self.dbLogin)
				self.connection.send_message(self.dbPassword)

				command = self.inputQueue.get(True, None)
				while command != STOP_THREAD:
					methodMapping[command]()
					command = self.inputQueue.get(True, None)
					logger.logInfo(NAME + "Odebrano komende " + command)
				self.connection.send_message(EXIT)
			else:
				logger.logError(NAME + "Nie mozna nawiazac polaczenia dla transakcji zapisu")
				self.outputQueue.put(ABORT)
				self.connection._do_closing_handshake()
			logger.logInfo(NAME + "Konice watku transakcji zapisu")
		except Exception, e:
			logging.error(NAME + e.message )

	def prepare(self):
		logger.logInfo(NAME + "PrepareMethod")
		command = self.inputQueue.get(True, None)
		logger.logInfo(NAME + "Otrzymalem zapytanie sql do wykonania " + command)
		self.connection.send_message(PREPARE)
		self.connection.send_message(command)
		answer = self.connection.get_message()
		self.outputQueue.put(answer)
		logger.logInfo(NAME + "Zdalny serwer odpowiedzial: " + answer)
		if self.outputQueue.full():
			self.eventVariable.set()
			logger.logInfo(NAME + "Wybudzanie watku transakcji")

	def globalCommit(self):
		logger.logInfo(NAME + "GlobalCommitMethod")
		self.connection.send_message(GLOBAL_COMMIT)
		command = self.inputQueue.get(True, None)
		self.connection.send_message(command)
		ticket = self.inputQueue.get(True, None)
		self.connection.send_message(ticket)
		answer = self.connection.get_message()
		self.outputQueue.put(answer)
		logger.logInfo(NAME + "Zdalny serwer odpowiedzial: " + answer)
		if self.outputQueue.full():
			logger.logInfo(NAME + "Wybudzanie watku transakcji")

	def globalAbort(self):
		logger.logInfo(NAME + "GlobalAbortMethod")
		self.connection.send_message(GLOBAL_ABORT)
		ticket = self.inputQueue.get(True, None)
		self.connection.send_message(ticket)
		answer = self.connection.get_message()
		self.outputQueue.put(answer)
		logger.logInfo(NAME + "Zdalny serwer odpowiedzial: " + answer)
		if self.outputQueue.full():
			logger.logInfo(NAME + "Wybudzanie watku transakcji")


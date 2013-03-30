from threading import Thread
from connections.Connection import Connection
import logging

NAME = "WriteTransactionThread: "
STOP_THREAD = "INTERRUPT"
LOCALHOST_NAME = "localhost"
PREPARE = "PREPARE"
GLOBAL_COMMIT = "GLOBAL_COMMIT"
ABORT = "ABORT"
GLOBAL_ABORT = "GLOBAL_ABORT"
OK = "OK"
OK_FLAG = 0

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
			methodMapping = {PREPARE : self.prepare, GLOBAL_COMMIT : self.globalCommit, GLOBAL_ABORT : self.globalAbort}
			self.connection = Connection(self.paramsDictionary["HOME_PATH"]+"ServerSide/config/database_config/transaction_config.conf")
			if self.connection.connect(self.clientAddress, 80) == OK_FLAG:
				logging.error(NAME + "Polaczenie dla transakcji zapisu nawiazane")
				self.connection.send_message(self.dbLogin)
				self.connection.send_message(self.dbPassword)

				command = self.inputQueue.get(True, None)
				while command != STOP_THREAD:
					methodMapping[command]()
					command = self.inputQueue.get(True, None)
					logging.error(NAME + "Odebrano komende " + command)
			else:
				logging.error(NAME + "Nie mozna nawiazac polaczenia dla transakcji zapisu")
				self.outputQueue.put(ABORT)
				self.connection._do_closing_handshake()
			logging.error(NAME + "Konice watku transakcji zapisu")
		except Exception, e:
			logging.error(NAME + e.message )

	def prepare(self):
		logging.error(NAME + "PrepareMethod")
		command = self.inputQueue.get(True, None)
		logging.error(NAME + "got command to execute on remote " + command)
		self.connection.send_message(PREPARE)
		self.connection.send_message(command)
		answer = self.connection.get_message()
		self.outputQueue.put(answer)
		logging.error(NAME + "remote machine answered with " + answer)
		if self.outputQueue.full():
			self.eventVariable.set()
			logging.error(NAME + "Waking up transation")

	def globalCommit(self):
		logging.error(NAME + "GlobalCommitMethod")
		self.connection.send_message(GLOBAL_COMMIT)
		command = self.inputQueue.get(True, None)
		self.connection.send_message(command)
		answer = self.connection.get_message()
		self.outputQueue.put(answer)
		logging.error(NAME + "remote machine answered with " + answer)
		if self.outputQueue.full():
			logging.error(NAME + "Waking up transation")

	def globalAbort(self):
		logging.error(NAME + "GlobalAbortMethod")
		self.connection.send_message(GLOBAL_ABORT)
		answer = self.connection.get_message()
		self.outputQueue.put(answer)
		logging.error(NAME + "remote machine answered with " + answer)
		if self.outputQueue.full():
			logging.error(NAME + "Waking up transation")


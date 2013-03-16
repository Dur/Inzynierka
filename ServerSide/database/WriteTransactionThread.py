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

	def __init__(self, outputQueue, inputQueue, eventVariable, commands, paramsDictionary):
		Thread.__init__(self)
		self.clientAddress = paramsDictionary["CLIENT_ADDRESS"]
		self.inputQueue = inputQueue
		self.eventVariable = eventVariable
		self.outputQueue = outputQueue
		self.commands = commands
		self.paramsDictionary = paramsDictionary
		self.connection = None

	def run(self):
		methodMapping = {PREPARE : self.prepare, GLOBAL_COMMIT : self.globalCommit, GLOBAL_ABORT : self.globalAbort}
		command = self.inputQueue.get(True, None)
		self.connection = Connection(self.paramsDictionary["HOME_PATH"]+"ServerSide/config/database_config/transaction_config.conf")
		if self.connection.connect(self.clientAddress, 80) == OK_FLAG:
			logging.error(NAME + "Polaczenie dla transakcji zapisu nawiazane")
			while command != STOP_THREAD:
				methodMapping[command]()
				command = self.inputQueue.get(True, None)
		else:
			logging.error(NAME + "Nie mozna nawiazac polaczenia dla transakcji zapisu")
			self.outputQueue.put(ABORT)
			self.connection._do_closing_handshake()
		logging.error(NAME + "Konice watku transakcji zapisu")

	def prepare(self):
		logging.error(NAME + "PrepareMethod")
		self.connection.send_message(PREPARE)
		self.outputQueue.put(self.connection.get_message())

	def globalCommit(self):
		logging.error(NAME + "GlobalCommitMethod")
		self.connection.send_message(GLOBAL_COMMIT)
		self.outputQueue.put(self.connection.get_message())

	def globalAbort(self):
		logging.error(NAME + "GlobalAbortMethod")
		self.connection.send_message(GLOBAL_ABORT)
		self.outputQueue.put(self.connection.get_message())


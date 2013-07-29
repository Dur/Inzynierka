from threading import Thread
from connections.Connection import Connection
import utils.Logger as logger

NAME = "DelayedTransactionThread: "
STOP_THREAD = "INTERRUPT"
LOCALHOST_NAME = "localhost"
SKIP = "SKIP"
START = "START"
ABORT = "ABORT"
OK = "OK"
OK_FLAG = 0
RESOURCE = "/delayedTransaction"
EXIT = "EXIT"


class DelayedTransactionThread(Thread):

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

	def run(self):
		try:
			methodMapping = {SKIP : self.skip,
			                 START : self.startTransaction,
			                 OK : self.ok}

			self.connection = Connection(self.paramsDictionary["HOME_PATH"]+"ServerSide/config/connection_config.conf")
			if self.connection.connect(self.clientAddress, 80, RESOURCE) == OK_FLAG:
				logger.logImportant(NAME + "Polaczenie z uczestnikiem transakcji " + self.clientAddress + " nawiazane" )

				command = self.inputQueue.get(True, None)
				while command != STOP_THREAD:
					methodMapping[command]()
					command = self.inputQueue.get(True, None)
					logger.logInfo(NAME + "Odebrano komende " + command)
				self.connection.send_message(EXIT)
			else:
				logger.logError(NAME + "Nie mozna nawiazac polaczenia z " + self.clientAddress)
				self.outputQueue.put(ABORT)
				self.connection._do_closing_handshake()
			logger.logImportant(NAME + "Koordynator konczy polaczenie z " + self.clientAddress)
		except Exception, e:
			logger.logImportant(NAME + e.message )

	def skip(self):
		logger.logInfo(NAME + "SkipMethod")
		self.connection.send_message(SKIP)

	def startTransaction(self):
		logger.logInfo(NAME + "StartMethod")
		ticket = self.inputQueue.get(True, None)
		self.connection.send_message(ticket)
		try:
			answer = self.connection.get_message()
		except Exception, e:
			logger.logError(NAME + e.message )
			return
		self.outputQueue.put(answer)
		logger.logImportant(NAME + "Uczestnik " + self.clientAddress + " odpowiedzial: " + answer)
		if self.outputQueue.full():
			self.eventVariable.set()
			logger.logInfo(NAME + "Wybudzanie watku transakcji")

	def ok(self):
		logger.logInfo(NAME + "OkMethod")
		self.connection.send_message(OK)


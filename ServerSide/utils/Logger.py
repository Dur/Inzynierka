from connections.Connection import Connection
from utils.FileProcessors import FileProcessor

__author__ = 'dur'

IMPORTANT = "IMP"
ERROR = "ERROR"
INFO = "INFO"
DEBUG = "DEBUG"
HOME_PATH = "/home/dur/Projects/"
LOGGER = "logger"

class Logger():

	def logError(self, message):
		connection = Connection(HOME_PATH + "ServerSide/config/connection_config.conf")
		connection.connect(self._getLoggerAddress(), 80, "/log")
		connection.send_message(message)
		connection.send_message(ERROR)
		connection._do_closing_handshake()

	def logImportant(self, message):
		connection = Connection(HOME_PATH + "ServerSide/config/connection_config.conf")
		connection.connect(self._getLoggerAddress(), 80, "/log")
		connection.send_message(message)
		connection.send_message(IMPORTANT)
		connection._do_closing_handshake()

	def logInfo(self, message):
		connection = Connection(HOME_PATH + "ServerSide/config/connection_config.conf")
		connection.connect(self._getLoggerAddress(), 80, "/log")
		connection.send_message(message)
		connection.send_message(INFO)
		connection._do_closing_handshake()

	def logDebug(self, message):
		connection = Connection(HOME_PATH + "ServerSide/config/connection_config.conf")
		connection.connect(self._getLoggerAddress(), 80, "/log")
		connection.send_message(message)
		connection.send_message(DEBUG)
		connection._do_closing_handshake()

	def _getLoggerAddress(self):
		tempProcessor = FileProcessor(HOME_PATH + "ServerSide/config/tempParams.conf")
		tempProcessor.lockFile()
		params = tempProcessor.readFile()
		tempProcessor.unlockFile()
		return params[LOGGER]



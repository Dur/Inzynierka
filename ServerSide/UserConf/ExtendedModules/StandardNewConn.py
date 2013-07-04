import utils.Logger as logger
from connections.Connection import Connection
from utils.FileProcessors import FileProcessor

__author__ = 'dur'

PING = "PING:PING"
NAME = "StandardNewConn: "
RESOURCE = "/newPing"
ERROR = -1

def execute(paramsDictionary, message):
	remoteAddress = paramsDictionary["CLIENT_ADDRESS"]

	logger.logImportant(NAME+ "Wykryto probe nawiazania polaczenia od " + remoteAddress)
	file = FileProcessor(paramsDictionary["HOME_PATH"]+"ServerSide/config/addresses.conf")
	paramsDictionary["CONNECTION_MODE"] = False
	try:
		file.lockFile()
		addresses = file.readFile()
		for key in addresses:
			logger.logInfo(NAME+ "klucz %s", key)
			logger.logInfo(NAME+ "adres serwera zdalnego %s", remoteAddress)
			logger.logInfo(NAME+ "addresses[key] %s", addresses[key])
			if key == remoteAddress:
				logger.logInfo(NAME+ "znalazl dopasowanie")
				if( addresses[key] != 'T' ):
					logger.logInfo(NAME+ "proba nawiazania polaczenia z nowododanym serwerem")
					paramsDictionary["CONNECTION"] = Connection(paramsDictionary["HOME_PATH"]+"ServerSide/config/ping_config.conf")
					if paramsDictionary["CONNECTION"].connect(remoteAddress, 80, RESOURCE) != ERROR:
						paramsDictionary["SOCKET"] = paramsDictionary["CONNECTION"]._stream
						paramsDictionary["SOCKET"].send_message(PING)
						paramsDictionary["SOCKET"].receive_message()
						logger.logImportant(NAME+ "Polaczenie z " + remoteAddress + " nawiazane")
						addresses[key] = 'T'
						file.writeToFile(addresses)
						paramsDictionary["CONNECTION_MODE"] = True
				break
	except Exception, e:
		logger.logError(NAME + e.message)
		file.unlockFile()
	file.unlockFile()
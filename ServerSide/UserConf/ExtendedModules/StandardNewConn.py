import logging
from connections.PingConnection import PingConnection
from utils.FileProcessors import FileProcessor

__author__ = 'dur'

PING = "PING:PING"
NAME = "StandardNewConn: "
RESOURCE = "/newPing"

def execute(paramsDictionary, message):
	remoteAddress = paramsDictionary["CLIENT_ADDRESS"]

	logging.error(NAME+ "Wlaczam dodatkowe opcje przy podlaczaniuserwera")
	file = FileProcessor(paramsDictionary["HOME_PATH"]+"ServerSide/config/addresses.conf")
	paramsDictionary["CONNECTION_MODE"] = False
	file.lockFile()
	addresses = file.readFile()
	for key in addresses:
		logging.error(NAME+ "key %s", key)
		logging.error(NAME+ "remote address %s", remoteAddress)
		logging.error(NAME+ "addresses[key] %s", addresses[key])
		if key == remoteAddress:
			logging.error(NAME+ "znalazl dopasowanie")
			if( addresses[key] != 'T' ):
				logging.error(NAME+ "proba nawiazania polaczenia z nowododanym serwerem")
				paramsDictionary["CONNECTION"] = PingConnection(paramsDictionary["HOME_PATH"]+"ServerSide/config/ping_config.conf")
				paramsDictionary["CONNECTION"].connect(remoteAddress, 80, RESOURCE)
				paramsDictionary["SOCKET"] = paramsDictionary["CONNECTION"]._stream
				paramsDictionary["SOCKET"].send_message(PING)
				paramsDictionary["SOCKET"].receive_message()
				logging.error(NAME+ "nawiazywanie polaczenia z nowododanym serwerem")
				addresses[key] = 'T'
				file.writeToFile(addresses)
				paramsDictionary["CONNECTION_MODE"] = True
			break
	file.unlockFile()
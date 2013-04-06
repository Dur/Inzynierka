import logging
from connections.Connection import Connection
from utils.FileProcessors import FileProcessor


__author__ = 'dur'
RESOURCE = "/broadcastDataVersion"
NAME = "BroadcastNewDataVersion: "
LOCALHOST_NAME = "localhost"

def execute(paramsDictionary, message):
	logging.info(NAME + "wewnatrz modulu rozglaszania nowej wersji ")
	homePath = paramsDictionary["HOME_PATH"]

	addressesfile = FileProcessor(paramsDictionary["HOME_PATH"]+"ServerSide/config/addresses.conf")
	addressesfile.lockFile()
	addresses = addressesfile.readFile()
	addressesfile.unlockFile()

	versionsFile = FileProcessor(homePath+"ServerSide/config/database_config/data_version.dat")
	versionsFile.lockFile()
	dataVersions = versionsFile.readFile()
	versionsFile.unlockFile()

	myVersion = dataVersions[LOCALHOST_NAME]
	logging.info(NAME + "Moja wersja danych " + myVersion)
	for address in addresses:
		if addresses[address] == "T":
			logging.info(NAME + "wysylanie wersji do " + address)
			connection = Connection(homePath + "ServerSide/config/connection_config.conf" )
			connection.connect(address, 80, RESOURCE)
			connection.send_message(myVersion)
			connection._do_closing_handshake()
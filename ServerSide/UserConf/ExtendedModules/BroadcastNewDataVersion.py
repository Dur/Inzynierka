import logging
from connections.Connection import Connection
from utils.FileProcessors import FileProcessor


__author__ = 'dur'
RESOURCE = "/broadcastDataVersion"
NAME = "BroadcastNewDataVersion: "
LOCALHOST_NAME = "localhost"
OK_FLAG = 0

def execute(paramsDictionary, message):
	logging.info(NAME + "wewnatrz modulu rozglaszania nowej wersji ")

	homePath = paramsDictionary["HOME_PATH"]

	lock = paramsDictionary["LOCK"]
	if lock.is_locked == False:
		return

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
			if connection.connect(address, 80, RESOURCE) == OK_FLAG:
				connection.send_message(myVersion)
				connection._do_closing_handshake()
			else:
				logging.error(NAME + "Nie moge polaczyc sie z serwerem o adresie " + address)

	lock.release()
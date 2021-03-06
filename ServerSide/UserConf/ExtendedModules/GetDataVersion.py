from utils.FileProcessors import FileProcessor

__author__ = 'dur'
import utils.Logger as logger


# modul sluzacy do wymiany informacji o wersji danych na kazdym serwerze


LOCALHOST = "localhost"
GET_DATA_VERSION = "DATA_VERSION?"
NAME = "GetDataVersion: "

def execute(paramsDictionary, message):
	logger.logInfo(NAME + "Wewnatrz modulu wymiany wersji danych")
	if paramsDictionary["CONNECTION_MODE"] == True:
		dataVersionConnectionMode(paramsDictionary)
	else:
		dataVersionRequestMode(paramsDictionary)

def dataVersionConnectionMode(paramsDictionary):

	socket = paramsDictionary["SOCKET"]
	remoteAddress = paramsDictionary["CLIENT_ADDRESS"]
	homePath = paramsDictionary["HOME_PATH"]

	logger.logInfo(NAME + "Pobieranie wersji danych")
	socket.send_message(GET_DATA_VERSION)

	clientVersion = socket.receive_message()
	logger.logInfo(NAME + "Otrzymano wersje danych klienta " + clientVersion)

	processor = FileProcessor(homePath+"ServerSide/config/database_config/data_version.dat")
	dataVersions = processor.readFile()
	dataVersions[remoteAddress] = clientVersion
	processor.lockFile()
	temp = processor.readFile()
	temp[remoteAddress] = dataVersions[remoteAddress]
	processor.writeToFile(temp)
	processor.unlockFile()

	if socket.receive_message() == GET_DATA_VERSION:
		socket.send_message(temp[LOCALHOST])
		logger.logInfo(NAME + "Wyslano wersje danych do klienta " + temp[LOCALHOST])


def dataVersionRequestMode(paramsDictionary):

	socket = paramsDictionary["SOCKET"]
	remoteAddress = paramsDictionary["CLIENT_ADDRESS"]
	homePath = paramsDictionary["HOME_PATH"]

	if socket.receive_message() == GET_DATA_VERSION:
		logger.logInfo(NAME + "Otrzymano zapytanie o wersje danych")
		processor = FileProcessor(homePath+"ServerSide/config/database_config/data_version.dat")
		dataVersions = processor.readFile()
		socket.send_message(dataVersions[LOCALHOST])
		logger.logInfo(NAME + "Wysylano wersji danych " + dataVersions[LOCALHOST])

		socket.send_message(GET_DATA_VERSION)

		clientVersion = socket.receive_message()
		dataVersions[remoteAddress] = clientVersion
		logger.logInfo(NAME + "Otrzymano wersje danych klienta " + clientVersion)

		processor.lockFile()
		temp = processor.readFile()
		temp[remoteAddress] = dataVersions[remoteAddress]
		processor.writeToFile(temp)
		processor.unlockFile()

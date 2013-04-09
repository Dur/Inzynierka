import MySQLdb
import logging
from connections.Connection import Connection
from database.utils1.DatabaseConnector import DatabaseConnector
from utils.ConfigurationReader import ConfigurationReader
from utils.FileProcessors import FileProcessor
from utils.filelock import FileLock

__author__ = 'dur'

NAME = "MakeCoherent: "
RESOURCE = "/makeCoherent"
END_MESSAGE = "END"
ERROR = -1
LOCALHOST_NAME = "localhost"
LOCK_ERROR = "LOCK_ERROR"
UP_TO_DATE = "UP_TO_DATE"

def execute(paramsDictionary, message):
	homePath = paramsDictionary["HOME_PATH"]

	if "LOCK" in paramsDictionary:
		lock = paramsDictionary["LOCK"]
	else:
		lockFilePath = paramsDictionary["HOME_PATH"]+"ServerSide/config/database_config/dbLock.dat"
		lock = FileLock(lockFilePath,2,.05)
		paramsDictionary["LOCK"] = lock

	lock.acquire()

	if lock.is_locked == False:
		return

	versionsFile = FileProcessor(homePath+"ServerSide/config/database_config/data_version.dat")
	versionsFile.lockFile()
	dataVersions = versionsFile.readFile()
	versionsFile.unlockFile()

	if checkIfServerIsUpToDate(dataVersions) == True:
		logging.info(NAME + "server is up to date")
		lock.release()
		return

	addressesfile = FileProcessor(paramsDictionary["HOME_PATH"]+"ServerSide/config/addresses.conf")
	addressesfile.lockFile()
	addresses = addressesfile.readFile()
	addressesfile.unlockFile()

	addressesToConnect = findActiveUpToDateServer(addresses, dataVersions)

	if len(addressesToConnect) > 0:
		connection = Connection(homePath + "ServerSide/config/connection_config.conf" )
		for addressToConnect in addressesToConnect:
			connection.connect(addressToConnect, 80, RESOURCE)
			connection.send_message(dataVersions[LOCALHOST_NAME])
			version = connection.get_message()
			if version != LOCK_ERROR:
				logging.info(NAME + "Connected to " + addressToConnect)
				break

		if version == LOCK_ERROR:
			logging.error(NAME + "cant make server up to date")
			return

		configReader = ConfigurationReader(paramsDictionary["HOME_PATH"]+"ServerSide/config/database_config/database.conf")
		dbParamsDict = configReader.readConfigFile()
		paramsDictionary["DB_PARAMS"] = dbParamsDict

		login = dbParamsDict["DEFAULT_LOGIN"]
		password = dbParamsDict["DEFAULT_PASSWORD"]

		try:
			db = MySQLdb.connect(dbParamsDict["HOST"], login, password, dbParamsDict["DATABASE"])
			cursor = db.cursor()
			logging.info(NAME + "polaczenie z baza nawiazane")
			while version != END_MESSAGE:
				command = connection.get_message()
				logging.info(NAME + "executing: " + command )
				cursor.execute(command)

				command = command.replace('\'', '\\\'')
				logging.info(NAME + "new command " + command)
				insert = "INSERT INTO " +  dbParamsDict["versionsTableName"] + " VALUES(" + str(version) + ",\'" + command + "\')"

				logging.info(NAME + "executing " + insert)
				cursor.execute(insert)
				logging.info(NAME + "wykonano inserta")
				currentVersion = version
				version = connection.get_message()
			logging.info(NAME + "zamykanie polaczenia z baza danych")
			cursor.execute("commit")
		except MySQLdb.Error, e:
			logging.error("%d %s" % (e.args[0], e.args[1]))
			cursor.execute("rollback")
		except Exception, ee:
			logging.error(ee.message)
			cursor.execute("rollback")

		versionsFile.lockFile()
		dataVersions = versionsFile.readFile()
		dataVersions[LOCALHOST_NAME] = currentVersion
		versionsFile.writeToFile(dataVersions)
		versionsFile.unlockFile()
		logging.info(NAME + "zapisano zmiany do pliku z wersjami")
		connection._do_closing_handshake()


def findActiveUpToDateServer(addresses, versions):
	addressesToRet = []
	maxVersionAddresses = findServersWithMaxDataVersion(versions)
	for address in maxVersionAddresses:
		logging.info(NAME + "analizowany adres " + address)
		if address in addresses:
			logging.info(NAME + "Adres wystepuje w adresach")
			if addresses[address] == "T":
				logging.info(NAME + "znalezino serwer do odpytania " + address)
				addressesToRet.append(address)
		return addressesToRet

def findServersWithMaxDataVersion(versions):
	maxVersionAddresses = []
	maxVersion = 0
	for address in versions:
		logging.info(NAME + "analizuje " + address)
		if int(versions[address]) > maxVersion:
			maxVersionAddresses = []
			maxVersionAddresses.append(address)
			maxVersion = int(versions[address])
		elif int(versions[address]) == maxVersion:
			maxVersionAddresses.append(address)
	logging.info(NAME + "Maksymalna wersja = " + str(maxVersion) )
	logging.info(NAME + "Serwery o tej wersji " + str(maxVersionAddresses))
	return maxVersionAddresses

def checkIfServerIsUpToDate(dataVersions):
	myVersion = dataVersions[LOCALHOST_NAME]
	for address in dataVersions:
		logging.info(NAME + "analizuje " + address)
		if int(dataVersions[address]) > int(myVersion):
			logging.info(NAME + "Server is out of date")
			return False
	return True



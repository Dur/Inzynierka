import MySQLdb
from connections.Connection import Connection
from utils.ConfigurationReader import ConfigurationReader
from utils.FileProcessors import FileProcessor
from utils.filelock import FileLock
import utils.Logger as logger

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

	try:
		lock.acquire()
	except Exception, e:
		logger.logError(NAME + e.message)
		if lock.is_locked:
			lock.release()
		return

	if lock.is_locked == False:
		return

	versionsFile = FileProcessor(homePath+"ServerSide/config/database_config/data_version.dat")
	versionsFile.lockFile()
	dataVersions = versionsFile.readFile()
	versionsFile.unlockFile()

	if checkIfServerIsUpToDate(dataVersions) == True:
		logger.logInfo(NAME + "Dane na serwerze sa aktualne")
		lock.release()
		return

	addressesfile = FileProcessor(paramsDictionary["HOME_PATH"]+"ServerSide/config/addresses.conf")
	addressesfile.lockFile()
	addresses = addressesfile.readFile()
	addressesfile.unlockFile()

	addressesToConnect = findActiveUpToDateServer(addresses, dataVersions)
	try:
		if len(addressesToConnect) > 0:
			connection = Connection(homePath + "ServerSide/config/connection_config.conf" )
			for addressToConnect in addressesToConnect:
				if connection.connect(addressToConnect, 80, RESOURCE) != ERROR:
					connection.send_message(dataVersions[LOCALHOST_NAME])
					version = connection.get_message()
					if version != LOCK_ERROR:
						logger.logInfo(NAME + "Polaczony z " + addressToConnect)
						break

			if version == LOCK_ERROR:
				logger.logError(NAME + "Nie mozna zaktualizowac serwera")
				return

			configReader = ConfigurationReader(paramsDictionary["HOME_PATH"]+"ServerSide/config/database_config/database.conf")
			dbParamsDict = configReader.readConfigFile()
			paramsDictionary["DB_PARAMS"] = dbParamsDict

			login = dbParamsDict["DEFAULT_LOGIN"]
			password = dbParamsDict["DEFAULT_PASSWORD"]
		else:
			logger.logError(NAME + "Brak serwerow, od ktorych mozna pobrac aktualne dane")
			return
	except Exception, e:
		logger.logError(NAME + e.message)
		if lock.is_locked:
			lock.release()

	try:
		db = MySQLdb.connect(dbParamsDict["HOST"], login, password, dbParamsDict["DATABASE"])
		cursor = db.cursor()
		logger.logImportant(NAME + "Rozpoczynanie uspojniania danych")
		while version != END_MESSAGE:
			command = connection.get_message()
			logger.logImportant(NAME + "Wykonuje: " + command )
			cursor.execute(command)

			command = command.replace('\'', '\\\'')
			logger.logInfo(NAME + "Komenda po transformacji " + command)
			insert = "INSERT INTO " +  dbParamsDict["versionsTableName"] + " VALUES(" + str(version) + ",\'" + command + "\')"

			logger.logInfo(NAME + "Wykonuje: " + insert)
			cursor.execute(insert)
			logger.logInfo(NAME + "wykonano inserta")
			currentVersion = version
			version = connection.get_message()
		logger.logInfo(NAME + "zamykanie polaczenia z baza danych")
		cursor.execute("commit")
	except MySQLdb.Error, e:
		logger.logError("%d %s" % (e.args[0], e.args[1]))
		cursor.execute("rollback")
	except Exception, ee:
		logger.logError(ee.message)
		cursor.execute("rollback")
		if lock.is_locked:
			lock.release()

	versionsFile.lockFile()
	dataVersions = versionsFile.readFile()
	dataVersions[LOCALHOST_NAME] = currentVersion
	versionsFile.writeToFile(dataVersions)
	versionsFile.unlockFile()
	logger.logImportant(NAME + "Dane sa spojne")
	connection._do_closing_handshake()


def findActiveUpToDateServer(addresses, versions):
	addressesToRet = []
	maxVersionAddresses = findServersWithMaxDataVersion(versions)
	for address in maxVersionAddresses:
		logger.logInfo(NAME + "analizowany adres " + address)
		if address in addresses:
			logger.logInfo(NAME + "Adres wystepuje w adresach")
			if addresses[address] == "T":
				logger.logInfo(NAME + "znalezino serwer do odpytania " + address)
				addressesToRet.append(address)
	return addressesToRet

def findServersWithMaxDataVersion(versions):
	maxVersionAddresses = []
	maxVersion = 0
	for address in versions:
		logger.logInfo(NAME + "analizuje " + address)
		if int(versions[address]) > maxVersion:
			maxVersionAddresses = []
			maxVersionAddresses.append(address)
			maxVersion = int(versions[address])
		elif int(versions[address]) == maxVersion:
			maxVersionAddresses.append(address)
	logger.logInfo(NAME + "Maksymalna wersja = " + str(maxVersion) )
	logger.logInfo(NAME + "Serwery o tej wersji " + str(maxVersionAddresses))
	return maxVersionAddresses

def checkIfServerIsUpToDate(dataVersions):
	myVersion = dataVersions[LOCALHOST_NAME]
	for address in dataVersions:
		logger.logInfo(NAME + "analizuje " + address)
		if int(dataVersions[address]) > int(myVersion):
			logger.logInfo(NAME + "Dane na serwerze nie sa aktualne")
			return False
	return True



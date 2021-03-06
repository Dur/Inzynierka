from mod_python import apache
from database.utils1 import TicketUtil
from database.utils1.DatabaseConnector import DatabaseConnector
from utils.ConfigurationReader import ConfigurationReader
from utils.FileProcessors import FileProcessor
from utils.filelock import FileLock
import utils.Logger as logger

NAME = "writeTransaction_wsh: "
PREPARE = "PREPARE"
GLOBAL_COMMIT = "GLOBAL_COMMIT"
ABORT = "ABORT"
GLOBAL_ABORT = "GLOBAL_ABORT"
OK = "OK"
EXIT = "EXIT"
ERROR = -1
OK_CODE = 0
READY_COMMIT = "READY_COMMIT"
COMMIT = "commit"
ROLLBACK = "rollback"
LOCALHOST_NAME = "localhost"

def web_socket_do_extra_handshake(request):
	pass  # Always accept.

def web_socket_transfer_data(request):

	logger.logInfo(NAME+ "Server dostal zgloszenie")

	paramsDictionary = {}
	paramsDictionary["SOCKET"] = request.ws_stream
	paramsDictionary["HOME_PATH"] = request.get_options()["PROJECT_LOCATION"]
	methodMapping = {PREPARE : prepare, GLOBAL_COMMIT : globalCommit, GLOBAL_ABORT : globalAbort}
	configReader = ConfigurationReader(paramsDictionary["HOME_PATH"]+"ServerSide/config/database_config/database.conf")
	dbParamsDict = configReader.readConfigFile()
	paramsDictionary["DB_PARAMS"] = dbParamsDict
	paramsDictionary["CLIENT_ADDRESS"] = request.connection.remote_ip

	login = request.ws_stream.receive_message()

	password = request.ws_stream.receive_message()

	db = DatabaseConnector(login, password, dbParamsDict["DATABASE"], dbParamsDict["HOST"])

	command = request.ws_stream.receive_message()
	lockFilePath = paramsDictionary["HOME_PATH"]+"ServerSide/config/database_config/dbLock.dat"
	lock = FileLock(lockFilePath,2,.05)
	try:
		while command != EXIT:
			methodMapping[command](paramsDictionary, db, lock)
			command = request.ws_stream.receive_message()
		if lock.is_locked:
			lock.release()
	except Exception, e:
		logger.logError(NAME + e.message)
		if lock.is_locked:
			lock.release()
		return apache.HTTP_OK
	logger.logInfo(NAME + "Klient zakonczyl transakcje")
	return apache.HTTP_OK

def prepare(paramsDictionary, db, lock):
	logger.logInfo(NAME + "Prepare")
	try:
		socket = paramsDictionary["SOCKET"]
		command = socket.receive_message()
		paramsDictionary["COMMAND"] = command
		logger.logInfo(NAME + "Wezel otrzymal komende do wykonania " + command)
		if db.initConnection() == ERROR:
			logger.logError(NAME + "Nie moge polaczyc sie z baza danych")
			socket.send_message(ABORT)
			if lock.is_locked:
				lock.release()
			return
		lock.acquire()
		if lock.is_locked == False:
			logger.logError(NAME + "Nie moge zalozyc blokady")
			socket.send_message(ABORT)
			lock.release()
			return
		if db.executeQueryWithoutTransaction(command) != OK_CODE:
			socket.send_message(ABORT)
			logger.logError(NAME + "Nie moge wykonac polecenia")
			lock.release()
			return
		logger.logImportant(NAME + "Uczestnik jest gotowy do zaakceptowania operacji")
		socket.send_message(READY_COMMIT)
		return
	except Exception, e:
		logger.logError(NAME + e.message)
		if lock.is_locked:
			lock.release()

def globalCommit(paramsDictionary, db, lock):
	try:
		socket = paramsDictionary["SOCKET"]
		servers = socket.receive_message()
		logger.logInfo(NAME + "Mam serwery " + servers)
		servers = servers.split(':')
		servers.append(paramsDictionary["CLIENT_ADDRESS"])
		logger.logImportant(NAME + "Uczestnik zaakceptowal operacje")
		db.executeQueryWithoutTransaction(generateInsertToDataVersions(paramsDictionary))
		db.executeQueryWithoutTransaction(COMMIT)
		insertNewDataVersions(servers, paramsDictionary)
		ticket = socket.receive_message()
		TicketUtil.setNextExpectedTicket(ticket)
		socket.send_message(OK)
		if lock.is_locked:
			lock.release()
	except Exception, e:
		logger.logError(NAME + e.message)
		if lock.is_locked:
			lock.release()


def globalAbort(paramsDictionary, db, lock):
	try:
		socket = paramsDictionary["SOCKET"]
		logger.logImportant(NAME + "Orzymano polecenie GLOBAL_ABORT")
		db.executeQueryWithoutTransaction(ROLLBACK)
		ticket = socket.receive_message()
		TicketUtil.skipTicket(ticket)
		socket.send_message(OK)
		if lock.is_locked:
			lock.release()
	except Exception, e:
		logger.logError(NAME + e.message)
		if lock.is_locked:
			lock.release()

def generateInsertToDataVersions(paramsDictionary):
	logger.logInfo(NAME + "Metoda generujaca wiersz dla tabeli z wersjami")
	versionProcessor = FileProcessor(paramsDictionary["HOME_PATH"] + "ServerSide/config/database_config/data_version.dat")
	dataVersions = versionProcessor.readFile()
	logger.logInfo(NAME + dataVersions[LOCALHOST_NAME])
	command = paramsDictionary["COMMAND"]
	command = command.replace('\'', '\\\'')
	myDataVersion = dataVersions[LOCALHOST_NAME]
	insert = "INSERT INTO " +  paramsDictionary["DB_PARAMS"]["versionsTableName"] + " VALUES(" + str((int(myDataVersion)+1)) + ",\'" + command + "\')"
	logger.logInfo(NAME + "wygenerowano komende insert " + insert)
	return insert

def insertNewDataVersions(serversList, paramsDictionary):
	try:
		homePath = paramsDictionary["HOME_PATH"]
		logger.logInfo(NAME + "Metoda wstawiajaca wiersz do tabeli z wierszami")
		versionProcessor = FileProcessor(homePath + "ServerSide/config/database_config/data_version.dat")
		versionProcessor.lockFile()
		logger.logInfo(NAME + "Plik z wersjami zablokowany")
		logger.logInfo(NAME + "Zapisywanie do pliku z wersjami")
		versions = versionProcessor.readFile()
		newVersion = str(int(versions[LOCALHOST_NAME]) +1)
		for address in serversList:
			logger.logInfo(NAME + "Dla adresu: " + address)
			if(address in versions):
				versions[address] = newVersion
				logger.logInfo(NAME + "Zapisano " + address )
		versions[LOCALHOST_NAME] = newVersion
		versionProcessor.writeToFile(versions)
		versionProcessor.unlockFile()
	except Exception, e:
		logger.logError(NAME + e.message)
		versionProcessor.unlockFile()

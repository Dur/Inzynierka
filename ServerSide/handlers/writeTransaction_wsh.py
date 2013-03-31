from database.utils1.DatabaseConnector import DatabaseConnector
from utils.ConfigurationReader import ConfigurationReader
from utils.FileProcessors import FileProcessor
from utils.filelock import FileLock

import logging

NAME = "writeTransaction_wsh: "
PREPARE = "PREPARE"
GLOBAL_COMMIT = "GLOBAL_COMMIT"
ABORT = "ABORT"
GLOBAL_ABORT = "GLOBAL_ABORT"
OK = "OK"
EXIT = "exit"
ERROR = -1
OK_CODE = 0
READY_COMMIT = "READY_COMMIT"
COMMIT = "commit"
ROLLBACK = "rollback"
LOCALHOST_NAME = "localhost"

def web_socket_do_extra_handshake(request):
	pass  # Always accept.

def web_socket_transfer_data(request):

	logging.error(NAME+ "Server dostal zgloszenie")

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
	lockFilePath = paramsDictionary["HOME_PATH"]+"ServerSide/config/database_config/executedCommands.dat"
	lock = FileLock(lockFilePath,5,.05)
	while command != EXIT:
		methodMapping[command](paramsDictionary, db, lock)
		command = request.ws_stream.receive_message()
	if lock.is_locked:
		lock.release()
	return

def prepare(paramsDictionary, db, lock):
	logging.error(NAME + "Prepare method")
	socket = paramsDictionary["SOCKET"]
	command = socket.receive_message()
	paramsDictionary["COMMAND"] = command
	logging.error(NAME + "received command to execute " + command)
	if db.initConnection() == ERROR:
		logging.error(NAME + "Cant connect to database")
		socket.send_message(ABORT)
		if lock.is_locked:
			lock.release()
		return
	lock.acquire()
	if lock.is_locked == False:
		logging.error(NAME + "Cant aquire lock")
		socket.send_message(ABORT)
		lock.release()
		return
	if db.executeQueryWithoutTransaction(command) != OK_CODE:
		socket.send_message(ABORT)
		logging.error(NAME + "Cant execute query")
		lock.release()
		return
	logging.error(NAME + "Sending ready commit")
	socket.send_message(READY_COMMIT)
	return

def globalCommit(paramsDictionary, db, lock):
	socket = paramsDictionary["SOCKET"]
	servers = socket.receive_message()
	logging.info(NAME + " got serwers " + servers)
	servers = servers.split(':')
	servers.append(paramsDictionary["CLIENT_ADDRESS"])
	logging.error(NAME + "Received global commit message")
	db.executeQueryWithoutTransaction(generateInsertToDataVersions(paramsDictionary))
	db.executeQueryWithoutTransaction(COMMIT)
	insertNewDataVersions(servers, paramsDictionary)
	socket.send_message(OK)
	if lock.is_locked:
		lock.release()


def globalAbort(paramsDictionary, db, lock):
	socket = paramsDictionary["SOCKET"]
	logging.error(NAME + "Received global abort message")
	db.executeQueryWithoutTransaction(ROLLBACK)
	socket.send_message(OK)
	if lock.is_locked:
		lock.release()

def generateInsertToDataVersions(paramsDictionary):
	logging.info(NAME + "inside generat inserto to database method")
	versionProcessor = FileProcessor(paramsDictionary["HOME_PATH"] + "ServerSide/config/database_config/data_version.dat")
	dataVersions = versionProcessor.readFile()
	logging.info(NAME + dataVersions[LOCALHOST_NAME])
	command = paramsDictionary["COMMAND"]
	command = command.replace('\'', '\\\'')
	myDataVersion = dataVersions[LOCALHOST_NAME]
	insert = "INSERT INTO " +  paramsDictionary["DB_PARAMS"]["versionsTableName"] + " VALUES(" + str((int(myDataVersion)+1)) + ",\'" + command + "\')"
	return insert

def insertNewDataVersions(serversList, paramsDictionary):
	homePath = paramsDictionary["HOME_PATH"]
	logging.info(NAME + "inside insert into data versions method")
	versionProcessor = FileProcessor(homePath + "ServerSide/config/database_config/data_version.dat")
	versionProcessor.lockFile()
	logging.info(NAME + "versionsFile locked")
	logging.info(NAME + "writeing to versions file")
	versions = versionProcessor.readFile()
	newVersion = str(int(versions[LOCALHOST_NAME]) +1)
	for address in serversList:
		logging.info(NAME + "for address " + address)
		if(address in versions):
			versions[address] = newVersion
			logging.info(NAME + "wrote " + address )
	versions[LOCALHOST_NAME] = newVersion
	versionProcessor.writeToFile(versions)
	versionProcessor.unlockFile()

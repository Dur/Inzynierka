from database.utils1.DatabaseConnector import DatabaseConnector
from utils.ConfigurationReader import ConfigurationReader
from utils.filelock import FileLock

import logging

NAME = "write_transaction_wsh: "
PREPARE = "PREPARE"
GLOBAL_COMMIT = "GLOBAL_COMMIT"
ABORT = "ABORT"
GLOBAL_ABORT = "GLOBAL_ABORT"
OK = "OK"
EXIT = "exit"
ERROR = -1
OK_CODE = 1
READY_COMMIT = "READY_COMMIT"
COMMIT = "commit"
ROLLBACK = "rollback"

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

	login = request.ws_stream.receive_message()

	password = request.ws_stream.receive_message()

	db = DatabaseConnector(login, password, dbParamsDict["DATABASE"], dbParamsDict["HOST"])

	command = request.ws_stream.get_message()
	lockFilePath = paramsDictionary["HOME_PATH"]+"ServerSide/config/database_config/executedCommands.dat"
	lock = FileLock(lockFilePath,5,.05)
	while command != EXIT:
		methodMapping[command](paramsDictionary, db, lock)
		command = request.ws_stream.get_message()
	if lock.is_locked:
		lock.release()
	return

def prepare(paramsDictionary, db, lock):
	logging.error(NAME + "Prepare method")
	socket = paramsDictionary["SOCKET"]
	command = socket.get_message()
	logging.error(NAME + "received command to execute " + command)
	if db.initConnection() == ERROR:
		logging.error(NAME + "Cant connect to database")
		socket.send_message(ABORT)
		lock.release()
		return
	lock.aquire()
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
	socket.send_message(READY_COMMIT)
	return

def globalCommit(paramsDictionary, db, lock):
	socket = paramsDictionary["SOCKET"]
	logging.error(NAME + "Received global commit message")
	db.executeQueryWithoutTransaction(COMMIT)
	socket.send_message(OK)
	lock.release()


def globalAbort(paramsDictionary, db, lock):
	socket = paramsDictionary["SOCKET"]
	logging.error(NAME + "Received global abort message")
	db.executeQueryWithoutTransaction(ROLLBACK)
	socket.send_message(OK)
	lock.release()

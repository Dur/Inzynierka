from database.utils1.DatabaseConnector import DatabaseConnector
from utils.ConfigurationReader import ConfigurationReader

__author__ = 'dur'
import logging

NAME = "write_transaction_wsh: "
LOCALHOST_NAME = "localhost"
PREPARE = "PREPARE"
GLOBAL_COMMIT = "GLOBAL_COMMIT"
ABORT = "ABORT"
GLOBAL_ABORT = "GLOBAL_ABORT"
OK = "OK"
EXIT = "exit"

def web_socket_do_extra_handshake(request):
	pass  # Always accept.

def web_socket_transfer_data(request):

	logging.error(NAME+ "Server dostal zgloszenie")

	paramsDictionary = {}
	paramsDictionary["REQUEST"] = request
	paramsDictionary["CLIENT_ADDRESS"]= request.connection.remote_ip
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
	while command != EXIT:
		methodMapping[command]()
		command = request.ws_stream.get_message()

def prepare(paramsDictionary):
	socket = paramsDictionary["SOCKET"]
	command = socket.get_message()

	pass

def globalCommit(paramsDictionary):
	pass

def globalAbort(paramsDictionary):
	pass


import logging
from database.utils1.DatabaseConnector import DatabaseConnector
from utils.ConfigurationReader import ConfigurationReader
from utils.filelock import FileLock

ERROR = -1
NAME = "dbQuery_wsh: "
CLOSING_MESSAGE = "EXIT"

def web_socket_do_extra_handshake(request):
	pass  # Always accept.


def web_socket_transfer_data(request):

	logging.error(NAME+ "Server dostal zgloszenie od klienta")

	paramsDictionary = {}
	paramsDictionary["REQUEST"] = request
	paramsDictionary["CLIENT_ADDRESS"]= request.connection.remote_ip
	paramsDictionary["SOCKET"] = request.ws_stream
	paramsDictionary["HOME_PATH"] = request.get_options()["PROJECT_LOCATION"]

	configReader = ConfigurationReader(paramsDictionary["HOME_PATH"]+"ServerSide/config/database_config/database.conf")
	dbParamsDict = configReader.readConfigFile()
	paramsDictionary["DB_PARAMS"] = dbParamsDict

	login = request.ws_stream.receive_message()
	password = request.ws_stream.receive_message()
	paramsDictionary["LOGIN"] = login
	paramsDictionary["PASSWORD"] = password


	db = DatabaseConnector(login, password, dbParamsDict["DATABASE"], dbParamsDict["HOST"])

	if db.initConnection() == ERROR:
		request.ws_stream.send_message("Invalid username or password")
		logging.error(NAME + "User supplied invalid credentials, closing connection")
		return
	logging.error(NAME + "polaczenie z baza nawiazane")
	lockFilePath = paramsDictionary["HOME_PATH"]+"ServerSide/config/database_config/executedCommands.dat"
	lock = FileLock(lockFilePath)
	while(True):
		try:
			query = request.ws_stream.receive_message()
			logging.error(NAME + "otrzymal " + query)
			if query == CLOSING_MESSAGE:
				db.closeConnection()
				return
			else:
				lock.acquire()
				output = db.executeSQL(query, paramsDictionary)
				lock.release()
				logging.error(NAME + "wynik zapytania " + str(output))
				request.ws_stream.send_message(str(output))

		except Exception, e:
			logging.error(NAME + "ERROR while receiving message " + e.message)
			db.closeConnection()
			if lock.is_locked:
				lock.release()
			return
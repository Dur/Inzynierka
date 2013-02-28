import logging
from database.utils.DatabaseConnector import DatabaseConnector
from utils.ConfigurationReader import ConfigurationReader

ERROR = -1
NAME = "dbQuery_wsh: "
CLOSING_MESSAGE = "QUIT"

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

	db = DatabaseConnector(login, password, dbParamsDict["DATABASE"], dbParamsDict["HOST"])

	if db.initConnection() == ERROR:
		request.ws_stream.send_message("Invalid username or password")
		logging.error(NAME + "User supplied invalid credentials, closing connection")
		return
	logging.error(NAME + "polaczenie z baza nawiazane")
	while(True):
		try:
			query = request.ws_stream.receive_message()
			logging.error(NAME + "otrzymal " + query)
			if query == CLOSING_MESSAGE:
				db.closeConnection()
				return
			else:
				output = db.executeSQL(query)
				logging.error(NAME + "wynik zapytania " + str(output))
				request.ws_stream.send_message(str(output))

		except Exception, e:
			logging.error(NAME + "ERROR while receiving message " + e.message)
			db.closeConnection()
			return
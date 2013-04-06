import MySQLdb
import logging
from utils.ConfigurationReader import ConfigurationReader

NAME = "makeCoherent_wsh: "
ERROR = -1
END = "END"

def web_socket_do_extra_handshake(request):
	pass  # Always accept.


def web_socket_transfer_data(request):

	logging.error(NAME+ "Server dostal zgloszenie")

	paramsDictionary = {}
	socket = request.ws_stream
	paramsDictionary["HOME_PATH"] = request.get_options()["PROJECT_LOCATION"]

	configReader = ConfigurationReader(paramsDictionary["HOME_PATH"]+"ServerSide/config/database_config/database.conf")
	dbParamsDict = configReader.readConfigFile()

	login = dbParamsDict["DEFAULT_LOGIN"]
	password = dbParamsDict["DEFAULT_PASSWORD"]

	clientVersion = socket.receive_message()
	logging.info(NAME + "client version " + clientVersion)
	try:
		db = MySQLdb.connect(dbParamsDict["HOST"], login, password, dbParamsDict["DATABASE"])
		cursor = db.cursor()
		logging.info(NAME + "polaczenie z baza nawiazane")
		cursor.execute("select * from versions where id > " + str(clientVersion) + " order by id")
		logging.info(NAME + "komenda wyslana do bazy")
		for version, command in cursor.fetchall():
			socket.send_message(str(version))
			socket.send_message(command)
			logging.info(NAME + "Wyslano " + version + " " + command)
		socket.send_message(END)
		logging.info(NAME + "wyslano wiadomosc konczaca")
	except MySQLdb.Error, e:
		logging.error("%d %s" % (e.args[0], e.args[1]))
	except Exception, ee:
		logging.error(ee.message)






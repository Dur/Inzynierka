import Queue
import logging
import time
from connections.ListenSocket import ListenSocket
from utils.ModulesLoader import ModulesLoader
from utils.ConfigurationReader import ConfigurationReader

NAME = "newPing_wsh: "
PONG = "PONG:PONG"
PING = "PING:PING"

def web_socket_do_extra_handshake(request):
	pass  # Always accept.


def web_socket_transfer_data(request):

	logging.info(NAME+ "Server dostal zgloszenie")

	paramsDictionary = {}
	paramsDictionary["REQUEST"] = request
	paramsDictionary["CLIENT_ADDRESS"]= request.connection.remote_ip
	paramsDictionary["SOCKET"] = request.ws_stream
	paramsDictionary["HOME_PATH"] = request.get_options()["PROJECT_LOCATION"]
	paramsDictionary["CONNECTION_MODE"] = False

	configReader = ConfigurationReader(paramsDictionary["HOME_PATH"]+"ServerSide/config/runParams.conf")
	paramsDictionary["CONFIG_PARAMS"] = configReader.readConfigFile()

	paramsDictionary["SOCKET"].receive_message()
	logging.info(NAME+ "Server otrzymal ping od " + paramsDictionary["CLIENT_ADDRESS"])
	paramsDictionary["SOCKET"].send_message(PONG)
	logging.info(NAME+ "Server odpowiedzial do " + paramsDictionary["CLIENT_ADDRESS"])

	loader = ModulesLoader()
	modules = loader.loadModules(paramsDictionary["HOME_PATH"]+"ServerSide/config/modules.ext")
	paramsDictionary["MODULES"] = modules
	logging.info(NAME+ "Serwer wczytal moduly")

	if modules.has_key("NEW_CONN"):
		for singleModule in modules["NEW_CONN"]:
			singleModule.execute(paramsDictionary, None)

	paramsDictionary["QUEUE"] = Queue.Queue(0)

	logging.info(NAME+ "Serwer rozpoczyna pingowanie")
	listener = ListenSocket(paramsDictionary, modules)
	listener.setDaemon(True)
	listener.start()
	while(True):
		try:
			for singleModule in modules["PERIODIC"]:
				singleModule.execute(paramsDictionary, None)
			time.sleep(int(paramsDictionary["CONFIG_PARAMS"]["singlePeriod"]))
		except Exception, e:
			logging.error(NAME+ "ERROR w modulach okresowych, zamykanie polaczenia")
			logging.error(NAME + e.message)
			for singleModule in modules["HOST_DC"]:
				singleModule.execute(paramsDictionary, None)
			if listener.is_alive:
				logging.info(NAME + "Oczekiwanie na watek nasluchujacy")
				listener.join()
				logging.info(NAME + "Watek nasluchujacy zakonczyl dzialanie")
			return



			#1000100100000000 - Ping frame in binary with no data
			#1000101000000000 - Pong frame in binary with no data
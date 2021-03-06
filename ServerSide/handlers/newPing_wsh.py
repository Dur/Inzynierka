import Queue
import utils.Logger as logger
from mod_python import apache
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

	logger.logInfo(NAME+ "Server dostal zgloszenie")

	paramsDictionary = {}
	paramsDictionary["REQUEST"] = request
	paramsDictionary["CLIENT_ADDRESS"]= request.connection.remote_ip
	paramsDictionary["SOCKET"] = request.ws_stream
	paramsDictionary["HOME_PATH"] = request.get_options()["PROJECT_LOCATION"]
	paramsDictionary["CONNECTION_MODE"] = False

	configReader = ConfigurationReader(paramsDictionary["HOME_PATH"]+"ServerSide/config/runParams.conf")
	paramsDictionary["CONFIG_PARAMS"] = configReader.readConfigFile()

	paramsDictionary["SOCKET"].receive_message()
	logger.logInfo(NAME+ "Server otrzymal ping od " + paramsDictionary["CLIENT_ADDRESS"])
	paramsDictionary["SOCKET"].send_message(PONG)
	logger.logInfo(NAME+ "Server odpowiedzial do " + paramsDictionary["CLIENT_ADDRESS"])

	loader = ModulesLoader()
	modules = loader.loadModules(paramsDictionary["HOME_PATH"]+"ServerSide/config/modules.ext")
	paramsDictionary["MODULES"] = modules
	logger.logInfo(NAME+ "Serwer wczytal moduly")

	if modules.has_key("NEW_CONN"):
		for singleModule in modules["NEW_CONN"]:
			singleModule.execute(paramsDictionary, None)

	paramsDictionary["QUEUE"] = Queue.Queue(0)

	logger.logInfo(NAME+ "Serwer rozpoczyna pingowanie")
	listener = ListenSocket(paramsDictionary, modules)
	listener.setDaemon(True)
	listener.start()
	while(True):
		try:
			for singleModule in modules["PERIODIC"]:
				singleModule.execute(paramsDictionary, None)
			time.sleep(int(paramsDictionary["CONFIG_PARAMS"]["singlePeriod"]))
		except Exception, e:
			logger.logError(NAME+ "ERROR w modulach okresowych, zamykanie polaczenia")
			logger.logError(NAME + e.message)
			for singleModule in modules["HOST_DC"]:
				singleModule.execute(paramsDictionary, None)
			logger.logInfo(NAME + "Polaczenie zakonczone")
			return apache.HTTP_OK



			#1000100100000000 - Ping frame in binary with no data
			#1000101000000000 - Pong frame in binary with no data
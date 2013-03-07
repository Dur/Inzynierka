import Queue
import logging
import time
from connections.ListenSocket import ListenSocket
from connections.PingConnection import PingConnection
from utils.FileProcessor import FileProcessor
from utils.ModulesLoader import ModulesLoader
from utils.ConfigurationReader import ConfigurationReader

NAME = "newHost_wsh: "
PONG = "PONG:PONG"
PING = "PING:PING"
EXIT = "EXIT"

def web_socket_do_extra_handshake(request):
	pass  # Always accept.


def web_socket_transfer_data(request):

	logging.error(NAME+ "Server dostal zgloszenie")

	paramsDictionary = {}
	paramsDictionary["REQUEST"] = request
	paramsDictionary["CLIENT_ADDRESS"]= request.connection.remote_ip
	paramsDictionary["SOCKET"] = request.ws_stream
	paramsDictionary["HOME_PATH"] = request.get_options()["PROJECT_LOCATION"]

	configReader = ConfigurationReader(paramsDictionary["HOME_PATH"]+"ServerSide/config/runParams.conf")
	paramsDictionary["CONFIG_PARAMS"] = configReader.readConfigFile()

	paramsDictionary["SOCKET"].receive_message()
	logging.error(NAME+ "Server otrzymal ping od " + paramsDictionary["CLIENT_ADDRESS"])


	remoteAddress = paramsDictionary["CLIENT_ADDRESS"]

	file = FileProcessor(paramsDictionary["HOME_PATH"]+"ServerSide/config/addresses.conf")
	paramsDictionary["CONNECTION_MODE"] = True
	file.lockFile()
	addresses = file.readFile()
	for key in addresses:
		logging.error(NAME+ "key %s", key)
		logging.error(NAME+ "remote address %s", remoteAddress)
		logging.error(NAME+ "addresses[key] %s", addresses[key])
		if key == remoteAddress and addresses[key] == 'F':
			logging.error(NAME+ "znalazl dopasowanie")
			logging.error(NAME+ "proba nawiazania polaczenia z nowododanym serwerem")
			paramsDictionary["CONNECTION"] = PingConnection(paramsDictionary["HOME_PATH"]+"ServerSide/config/ping_config.conf")
			paramsDictionary["CONNECTION"].connect(remoteAddress, 80)
			paramsDictionary["SOCKET"].send_message(PONG)
			logging.error(NAME+ "Server odpowiedzial PONG do " + paramsDictionary["CLIENT_ADDRESS"])

			paramsDictionary["SOCKET"] = paramsDictionary["CONNECTION"]._stream
			paramsDictionary["SOCKET"].send_message(PING)
			paramsDictionary["SOCKET"].receive_message()

			logging.error(NAME+ "nawiazywanie polaczenia z nowododanym serwerem")
			addresses[key] = 'T'
			file.writeToFile(addresses)
			break
		else:
			paramsDictionary["SOCKET"].send_message(EXIT)
			logging.error(NAME+ "Server odpowiedzial EXIT do " + paramsDictionary["CLIENT_ADDRESS"])
			file.unlockFile()
			return
	file.unlockFile()


	loader = ModulesLoader()
	modules = loader.loadModules(paramsDictionary["HOME_PATH"]+"ServerSide/config/modules.ext")
	paramsDictionary["MODULES"] = modules
	logging.error(NAME+ "server loaded modules")

	for singleModule in modules["NEW_CONN"]:
		singleModule.execute(paramsDictionary, None)

	paramsDictionary["QUEUE"] = Queue.Queue(0)

	logging.error(NAME+ "server starting pinging")
	listener = ListenSocket(paramsDictionary, modules)
	listener.setDaemon(True)
	listener.start()
	while(True):
		try:
			for singleModule in modules["PERIODIC"]:
				singleModule.execute(paramsDictionary, None)
			time.sleep(int(paramsDictionary["CONFIG_PARAMS"]["singlePeriod"]))
		except Exception, e:
			logging.error(NAME+ "error in periodic modules. closing connecion")
			logging.error(NAME + e.message)
			for singleModule in modules["HOST_DC"]:
				singleModule.execute(paramsDictionary, None)
			return



			#1000100100000000 - Ping frame in binary with no data
			#1000101000000000 - Pong frame in binary with no data
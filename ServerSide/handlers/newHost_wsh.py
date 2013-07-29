import Queue
from mod_python import apache
import utils.Logger as logger
import time
from connections.Connection import Connection
from connections.ListenSocket import ListenSocket
from utils.FileProcessors import FileProcessor
from utils.ModulesLoader import ModulesLoader
from utils.ConfigurationReader import ConfigurationReader

NAME = "newHost_wsh: "
PONG = "PONG:PONG"
PING = "PING:PING"
EXIT = "EXIT"
RESOURCE = "/newPing"
ERROR = -1

def web_socket_do_extra_handshake(request):
	pass  # Always accept.


def web_socket_transfer_data(request):

	logger.logInfo(NAME+ "Server dostal zgloszenie")

	paramsDictionary = {}
	paramsDictionary["REQUEST"] = request
	paramsDictionary["CLIENT_ADDRESS"]= request.connection.remote_ip
	paramsDictionary["SOCKET"] = request.ws_stream
	paramsDictionary["HOME_PATH"] = request.get_options()["PROJECT_LOCATION"]

	configReader = ConfigurationReader(paramsDictionary["HOME_PATH"]+"ServerSide/config/runParams.conf")
	paramsDictionary["CONFIG_PARAMS"] = configReader.readConfigFile()

	paramsDictionary["SOCKET"].receive_message()
	logger.logImportant(NAME+ "Serwer " + paramsDictionary["CLIENT_ADDRESS"] + " probuje nawiazac polaczenie")

	remoteAddress = paramsDictionary["CLIENT_ADDRESS"]

	file = FileProcessor(paramsDictionary["HOME_PATH"]+"ServerSide/config/addresses.conf")
	paramsDictionary["CONNECTION_MODE"] = True
	try:
		file.lockFile()
		addresses = file.readFile()

		for key in addresses:
			logger.logInfo(NAME+ "klucz %s " + key)
			logger.logInfo(NAME+ "adres zdalnej maszyny %s " + remoteAddress)
			logger.logInfo(NAME+ "addresses[key] %s " + addresses[key])
			if key == remoteAddress:
				if addresses[key] == 'F':
					logger.logInfo(NAME+ "znalazl dopasowanie")
					paramsDictionary["SOCKET"].send_message(PONG)
					logger.logInfo(NAME+ "Server odpowiedzial PONG do " + paramsDictionary["CLIENT_ADDRESS"])
					logger.logInfo(NAME+ "proba nawiazania polaczenia z nowododanym serwerem")
					paramsDictionary["CONNECTION"] = Connection(paramsDictionary["HOME_PATH"]+"ServerSide/config/connection_config.conf")
					if paramsDictionary["CONNECTION"].connect(remoteAddress, 80, RESOURCE) != ERROR:
						paramsDictionary["SOCKET"] = paramsDictionary["CONNECTION"]._stream
						paramsDictionary["SOCKET"].send_message(PING)
						paramsDictionary["SOCKET"].receive_message()
						logger.logInfo(NAME+ "nawiazywanie polaczenia z nowododanym serwerem")
						addresses[key] = 'T'
						file.writeToFile(addresses)
						break
				else:
					paramsDictionary["SOCKET"].send_message(EXIT)
					logger.logInfo(NAME+ "Server odpowiedzial EXIT do " + paramsDictionary["CLIENT_ADDRESS"])
					file.unlockFile()
					return apache.HTTP_OK
		file.unlockFile()
	except Exception, e:
		logger.logError(NAME + e.message)
		file.unlockFile()
		return apache.HTTP_OK

	loader = ModulesLoader()
	modules = loader.loadModules(paramsDictionary["HOME_PATH"]+"ServerSide/config/modules.ext")
	paramsDictionary["MODULES"] = modules
	logger.logInfo(NAME+ "Serwer wczytal moduly")

	if modules.has_key("NEW_CONN"):
		for singleModule in modules["NEW_CONN"]:
			singleModule.execute(paramsDictionary, None)

	paramsDictionary["QUEUE"] = Queue.Queue(0)

	logger.logImportant(NAME+ "Polaczenie z " + paramsDictionary["CLIENT_ADDRESS"] + " nawiazane")
	listener = ListenSocket(paramsDictionary, modules)
	listener.setDaemon(True)
	listener.start()
	while(True):
		try:
			for singleModule in modules["PERIODIC"]:
				singleModule.execute(paramsDictionary, None)
			time.sleep(int(paramsDictionary["CONFIG_PARAMS"]["singlePeriod"]))
		except Exception, e:
			logger.logError(NAME+ "ERROR w modulach cyklicznych, zamykanie polaczenia")
			logger.logError(NAME + e.message)
			for singleModule in modules["HOST_DC"]:
				singleModule.execute(paramsDictionary, None)
			return apache.HTTP_OK



			#1000100100000000 - Ping frame in binary with no data
			#1000101000000000 - Pong frame in binary with no data
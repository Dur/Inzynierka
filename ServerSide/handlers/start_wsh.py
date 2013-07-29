from connections.Connection import Connection
import time
from utils.ConfigurationReader import ConfigurationReader
from utils.FileProcessors import FileProcessor
from utils.ModulesLoader import ModulesLoader

__author__ = 'dur'

import utils.Logger as logger

NAME = "start_wsh: "
PING = "PING:PING"
RESOURCE = "/newHost"
PONG = "PONG:PONG"
ERROR = -1
def web_socket_do_extra_handshake(request):
	pass  # Always accept.


def web_socket_transfer_data(request):
	paramsDictionary = {}
	paramsDictionary["REQUEST"] = request
	paramsDictionary["SOCKET"] = request.ws_stream
	paramsDictionary["HOME_PATH"] = request.get_options()["PROJECT_LOCATION"]

	loader = ModulesLoader()
	modules = loader.loadModules(paramsDictionary["HOME_PATH"]+"ServerSide/config/modules.ext")
	paramsDictionary["MODULES"] = modules
	logger.logInfo(NAME+ "Serwer wczytal moduly")

	configReader = ConfigurationReader(paramsDictionary["HOME_PATH"]+"ServerSide/config/runParams.conf")
	runParams = configReader.readConfigFile()

	if modules.has_key("BEFORE_CONNECT"):
		for singleModule in modules["BEFORE_CONNECT"]:
			singleModule.execute(paramsDictionary, None)

	firstTimeIteration = True
	file = FileProcessor(paramsDictionary["HOME_PATH"]+"ServerSide/config/addresses.conf")

	while True:
		if modules.has_key("BEFORE_CONNECT_PERIODIC"):
			for singleModule in modules["BEFORE_CONNECT_PERIODIC"]:
				singleModule.execute(paramsDictionary, None)
		try:
			file.lockFile()
			addresses = file.readFile()
			file.unlockFile()
			for key in addresses:
				try:
					file.lockFile()
					tempAddresses = file.readFile()
					if( tempAddresses[key] == 'F' ):
						connection = Connection(request.get_options()["PROJECT_LOCATION"]+"ServerSide/config/connection_config.conf")
						if( connection.connect(key,80, RESOURCE) != ERROR ):
							logger.logInfo(NAME+ "Polaczenie z " + key + " nawiazane")
							connection.send_message(PING)
							logger.logInfo(NAME+ "Wysylanie pingu z metody startowej")
							if connection.get_message() == PONG:
								logger.logInfo(NAME+ "Metoda startowa otrzymala odpowiedz, zamykanie polaczenia")
								connection._do_closing_handshake()
								logger.logInfo(NAME + "########### polaczenie zakonczone, zapisywanie pliku adresowego")
								tempAddresses[key] = 'T'
								file.writeToFile(tempAddresses)
								logger.logInfo(NAME + "Zapisano zmiany do pliku adresowego")
							else:
								logger.logError(NAME+ "Serwer " + key + " nie odpowiedzial na PING, zrywanie polaczenia")
						else:
							logger.logError(NAME+ "Nie moge polaczyc sie z " + key)
					file.unlockFile()
				except Exception, e:
					logger.logError(NAME + e.message)
					file.unlockFile()
		except Exception, e:
			logger.logError(NAME + e.message)
			file.unlockFile()
			continue
		file.unlockFile()

		if firstTimeIteration == True:
			firstTimeIteration = False
			if modules.has_key("AFTER_CONNECT"):
				for singleModule in modules["AFTER_CONNECT"]:
					singleModule.execute(paramsDictionary, None)

		if modules.has_key("AFTER_CONNECT_PERIODIC"):
			for singleModule in modules["AFTER_CONNECT_PERIODIC"]:
				singleModule.execute(paramsDictionary, None)

		logger.logInfo(NAME+ "Serwer rozpoczyna czeanie na kolejna ture sprawdzania")
		time.sleep(int(runParams["ConnectionCheckPeriod"]))
		logger.logInfo(NAME+ "Serwer wznawia sprawdzanie")
from connections.Connection import Connection
from connections.PingConnection import PingConnection
import time
from utils.FileProcessors import FileProcessor
from utils.ModulesLoader import ModulesLoader

__author__ = 'dur'

import logging

NAME = "start_wsh: "
PING = "PING:PING"
RESOURCE = "/newHost"
PONG = "PONG:PONG"
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
	logging.info(NAME+ "Serwer wczytal moduly")

	if modules.has_key("BEFORE_CONNECT"):
		for singleModule in modules["BEFORE_CONNECT"]:
			singleModule.execute(paramsDictionary, None)

	firstTimeIteration = True
	file = FileProcessor(paramsDictionary["HOME_PATH"]+"ServerSide/config/addresses.conf")

	while True:
		if modules.has_key("BEFORE_CONNECT_PERIODIC"):
			for singleModule in modules["BEFORE_CONNECT_PERIODIC"]:
				singleModule.execute(paramsDictionary, None)

		file.lockFile()
		addresses = file.readFile()
		for key in addresses:
			if( addresses[key] == 'F' ):
				connection = Connection(request.get_options()["PROJECT_LOCATION"]+"ServerSide/config/connection_config.conf")
				if( connection.connect(key,80, RESOURCE) != -1 ):
					logging.info(NAME+ "Polaczenie z %s nawiazane", key)
					connection.send_message(PING)
					logging.info(NAME+ "Wysylanie pingu z metody startowej")
					if connection.get_message() == PONG:
						logging.info(NAME+ "Metoda startowa otrzymala odpowiedz, zamykanie polaczenia")
						connection._do_closing_handshake()
						addresses[key] = 'T'
					else:
						logging.error(NAME+ "Serwer " + key + " nie odpowiedzial na PING, zrywanie polaczenia")
				else:
					logging.error(NAME+ "Nie moge polaczyc sie z %s", key)
		file.writeToFile(addresses)
		file.unlockFile()

		if firstTimeIteration == True:
			firstTimeIteration = False
			if modules.has_key("AFTER_CONNECT"):
				for singleModule in modules["AFTER_CONNECT"]:
					singleModule.execute(paramsDictionary, None)

		if modules.has_key("AFTER_CONNECT_PERIODIC"):
			for singleModule in modules["AFTER_CONNECT_PERIODIC"]:
				singleModule.execute(paramsDictionary, None)

		logging.info(NAME+ "Serwer rozpoczyna czeanie na kolejna ture sprawdzania")
		time.sleep(60)
		logging.info(NAME+ "Serwer wznawia sprawdzanie")
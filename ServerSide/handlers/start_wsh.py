from connections.PingConnection import PingConnection
from utils.FileProcessor import FileProcessor
import time

__author__ = 'dur'

import logging

NAME = "start_wsh: "
PING = "PING:PING"
PONG = "PONG:PONG"
def web_socket_do_extra_handshake(request):
	pass  # Always accept.


def web_socket_transfer_data(request):
	file = FileProcessor(request.get_options()["PROJECT_LOCATION"]+"ServerSide/config/addresses.conf")
	file.lockFile()
	addresses = file.readFile()
	for key in addresses:
		addresses[key] = 'F'
	file.writeToFile(addresses)
	while True:
		for key in addresses:
			if( addresses[key] == 'F' ):
				connection = PingConnection(request.get_options()["PROJECT_LOCATION"]+"ServerSide/config/connection_config.conf")
				if( connection.connect(key,80) != -1 ):
					logging.error(NAME+ "connection with %s established", key)
					connection.send_message(PING)
					logging.error(NAME+ "sending ping from start method")
					if connection.get_message() == PONG:
						logging.error(NAME+ "start method received answer, closing connection")
						connection._do_closing_handshake()
						addresses[key] = 'T'
					else:
						logging.error(NAME+ "Serwer nie odpowiedzial na PING, zrywanie polaczenia")
				else:
					logging.error(NAME+ "unable to connect to %s", key)
		file.writeToFile(addresses)
		file.unlockFile()
		logging.error(NAME+ "Serwer rozpoczyna czeanie na kolejna ture sprawdzania")
		time.sleep(60)
		logging.error(NAME+ "Serwer wznawia sprawdzanie")
		file.lockFile()
		addresses = file.readFile()
		file.unlockFile()
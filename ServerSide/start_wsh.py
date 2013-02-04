__author__ = 'dur'

from FileProcessor import FileProcessor
from PingConnection import PingConnection
import logging

NAME = "start_wsh: "
def web_socket_do_extra_handshake(request):
	pass  # Always accept.


def web_socket_transfer_data(request):
	file = FileProcessor("/home/dur/Projects/ServerSide/addresses.conf")
	file.lockFile()
	addresses = file.readFile()
	for key in addresses:
		addresses[key] = 'F'
	file.writeToFile(addresses)
	file.unlockFile()
	print addresses
	for key in addresses:
		connection = PingConnection("/home/dur/Projects/ServerSide/ping_config.conf")
		if( connection.connect(key,80) != -1 ):
			addresses[key] = 'T'
			file.lockFile()
			file.writeToFile(addresses)
			file.unlockFile()
			logging.error(NAME+ "connection with %s established", key)
			connection.send("Ping")
			logging.error(NAME+ "sending ping from start method")
			connection.get_message()
			logging.error(NAME+ "start method received answer, closing connection")
			connection._do_closing_handshake()
		else:
			logging.error(NAME+ "unable to connect to %s", key)
	return
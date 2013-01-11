__author__ = 'dur'

from FileProcessor import FileProcessor
from PingConnection import PingConnection
import logging

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
	for key in addresses:
		connection = PingConnection("/home/dur/Projects/ServerSide/ping_config.conf")
		if( connection.connect(key,80) != -1 ):
			addresses[key] = 'T'
			file.lockFile()
			file.writeToFile(addresses)
			file.unlockFile()
			logging.error("connection with %s established", key)
			connection.send("Ping")
			logging.error("sending ping from start method")
			connection.get_message()
			logging.error("start method received answer, closing connection")
			connection._do_closing_handshake()
		else:
			logging.error("unable to connect to %s", key)
	return
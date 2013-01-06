__author__ = 'dur'

from FileProcessor import FileProcessor
from PingConnection import PingConnection
import time
def web_socket_do_extra_handshake(request):
	pass  # Always accept.


def web_socket_transfer_data(request):
	file = FileProcessor("/home/dur/Projects/ServerSide/addresses.conf")
	file.lockFile()
	addresses = file.readFile()
	for key in addresses:
		addresses[key] = 'T'
	file.writeToFile(addresses)
	file.unlockFile()
	new = {}
	connection = PingConnection("/home/dur/Projects/ServerSide/ping_config.conf")
	while True:
		file.lockFile()
		org = file.readFile()
		for key in org:
			if( connection.connect(key,80) != -1 ):
				connection.send("Ping")
				connection.get_message()
				connection._do_closing_handshake()
				new[key] = 'T'
			else:
				new[key] = 'F'
		file.mergeFile(org, new)
		file.unlockFile()
		time.sleep(2)
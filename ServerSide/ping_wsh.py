__author__ = 'dur'
import logging
from FileProcessor import FileProcessor

def web_socket_do_extra_handshake(request):
	pass  # Always accept.


def web_socket_transfer_data(request):
	request.ws_stream.send_message("Pong")
	logging.error("Server otrzymal ping od " + request.connection.remote_ip)
	file = FileProcessor("/home/dur/Projects/ServerSide/addresses.conf")
	file.lockFile()
	addresses = file.readFile()
	for key in addresses:
		if key == request.connection.remote_ip:
			addresses[key] = 'T'
			break
	file.writeToFile(addresses)
	file.unlockFile()

	#1000100100000000 - Ping frame in binary with no data
	#1000101000000000 - Pong frame in binary with no data
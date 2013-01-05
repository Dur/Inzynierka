__author__ = 'dur'

from FileProcessor import FileProcessor
import time
def web_socket_do_extra_handshake(request):
	pass  # Always accept.


def web_socket_transfer_data(request):
	file = FileProcessor("/home/dur/Projects/ServerSide/addresses.conf")
	addresses = file.readFile()
	for key in addresses:
		addresses[key] = 'T'
	file.writeToFile(addresses)
	new = {}
	while True:
		org = file.readFile()
		for key in org:
			try:
				
				new[key] = 'T'
			except:
				new[key] = 'F'

		file.mergeFile(org, new)
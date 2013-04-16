import logging
from mod_python import apache
from utils.FileProcessors import FileProcessor


NAME = "broadcastDataVersion_wsh: "

def web_socket_do_extra_handshake(request):

	pass  # Always accept.


def web_socket_transfer_data(request):
	logging.info(NAME + "Server dostal zgloszenie")
	clientAddress = request.connection.remote_ip
	socket = request.ws_stream
	homePath = request.get_options()["PROJECT_LOCATION"]
	try:
		versionsFile = FileProcessor(homePath+"ServerSide/config/database_config/data_version.dat")
		versionsFile.lockFile()
		dataVersions = versionsFile.readFile()
		version = socket.receive_message()
		logging.info(NAME + "Otrzymano nowa wersje klienta " + version)
		dataVersions[clientAddress] = version
		versionsFile.writeToFile(dataVersions)
		versionsFile.unlockFile()
	except Exception, e:
		logging.error(NAME + e.message)
		versionsFile.unlockFile()
		return apache.HTTP_OK
	logging.info(NAME + "Zapisano nowa wersje")
	return apache.HTTP_OK
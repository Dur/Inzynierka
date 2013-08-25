from mod_python import apache
from utils.FileProcessors import FileProcessor
import utils.Logger as logger
NAME = "ticket_wsh: "


def web_socket_do_extra_handshake(request):

	pass  # Always accept.


def web_socket_transfer_data(request):
	logger.logInfo(NAME + "Zgloszenie po bilet od " + str(request.connection.remote_ip))

	homePath = request.get_options()["PROJECT_LOCATION"]
	processor = FileProcessor(homePath + "ServerSide/config/database_config/ticketNumber.dat")
	processor.lockFile()
	number = processor.readFirstLine()
	nextNumber = int(number) + 1
	processor.writeSingleLine(str(nextNumber))
	processor.unlockFile()
	request.ws_stream.send_message(str(nextNumber))
	logger.logInfo(NAME + request.connection.remote_ip + " otrzymal bilet " + str(nextNumber))
	return apache.HTTP_OK

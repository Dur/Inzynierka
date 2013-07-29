from mod_python import apache
import time
import utils.Logger as logger
from utils.FileProcessors import FileProcessor

IMPORTANT = "IMP"
ERROR = "ERROR"
INFO = "INFO"
DEBUG = "DEBUG"
map = {ERROR : "ServerSide/log/error.log",
       INFO : "ServerSide/log/info.log",
       DEBUG : "ServerSide/log/debug.log",
       IMPORTANT : "ServerSide/log/important.log"}

def web_socket_do_extra_handshake(request):
	pass  # Always accept.


def web_socket_transfer_data(request):
	path = request.get_options()["PROJECT_LOCATION"]
	message = request.ws_stream.receive_message()
	level = request.ws_stream.receive_message()
	processor = FileProcessor(path + map[level])
	processor.lockFile()
	toLog = time.strftime('%x %X') + " " + request.connection.remote_ip + " " + message + '\n'
	processor.appendToFile(toLog)
	processor.unlockFile()
	return apache.HTTP_OK




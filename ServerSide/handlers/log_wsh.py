from mod_python import apache
import time
import utils.Logger as logger
from utils.FileProcessors import FileProcessor

IMPORTANT = "IMP"
ERROR = "ERROR"
INFO = "INFO"
DEBUG = "DEBUG"
map = {ERROR : "ServerSide/log/important.log",
       INFO : "ServerSide/log/important.log",
       DEBUG : "ServerSide/log/important.log",
       IMPORTANT : "ServerSide/log/important.log"}

addressMap = {"192.168.56.104" : "Serwer 3",
       "192.168.56.103" : "Serwer 2",
       "192.168.56.105" : "Serwer 4",
       "192.168.56.106" : "Serwer 5",
       "127.0.0.1": "Serwer 1"}

def web_socket_do_extra_handshake(request):
	pass  # Always accept.


def web_socket_transfer_data(request):
	path = request.get_options()["PROJECT_LOCATION"]
	message = request.ws_stream.receive_message()
	level = request.ws_stream.receive_message()
	processor = FileProcessor(path + map[level])
	processor.lockFile()
	toLog = time.strftime('%x %X') + " " + mapIpOnServerName(request.connection.remote_ip) + " " + message + '\n'
	processor.appendToFile(toLog)
	processor.unlockFile()
	return apache.HTTP_OK

def mapIpOnServerName(address):
	return addressMap[address]




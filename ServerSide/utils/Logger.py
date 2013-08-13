__author__ = 'dur'


from utils.FileProcessors import FileProcessor
IMPORTANT = "IMP"
ERROR = "ERROR"
INFO = "INFO"
DEBUG = "DEBUG"
HOME_PATH = "/home/dur/Projects/"
LOGGER = "logger"


def logError(message):
	connection = Connection(HOME_PATH + "ServerSide/config/connection_config.conf")
	connection.connect(_getLoggerAddress(), 80, "/log")
	if connection.isConnected:
		connection.send_message(message)
		connection.send_message(ERROR)
		connection._do_closing_handshake()

def logImportant(message):
	connection = Connection(HOME_PATH + "ServerSide/config/connection_config.conf")
	connection.connect(_getLoggerAddress(), 80, "/log")
	if connection.isConnected:
		connection.send_message(message)
		connection.send_message(IMPORTANT)
		connection._do_closing_handshake()

def logInfo(message):
	connection = Connection(HOME_PATH + "ServerSide/config/connection_config.conf")
	connection.connect(_getLoggerAddress(), 80, "/log")
	if connection.isConnected:
		connection.send_message(message)
		connection.send_message(INFO)
		connection._do_closing_handshake()

def logDebug(message):
	connection = Connection(HOME_PATH + "ServerSide/config/connection_config.conf")
	connection.connect(_getLoggerAddress(), 80, "/log")
	if connection.isConnected:
		connection.send_message(message)
		connection.send_message(DEBUG)
		connection._do_closing_handshake()

def _getLoggerAddress():
	tempProcessor = FileProcessor(HOME_PATH + "ServerSide/config/tempParams.conf")
	tempProcessor.lockFile()
	params = tempProcessor.readFile()
	tempProcessor.unlockFile()
	return params[LOGGER]



import socket
from mod_pywebsocket import common
from mod_pywebsocket.stream import Stream
from mod_pywebsocket.stream import StreamOptions
from WebSocket._TLSSocket import _TLSSocket
from WebSocket.ClientRequest import ClientRequest
from WebSocket.ClientHandshakeProcessor import ClientHandshakeProcessor
from utils.ConfigurationReader import ConfigurationReader


_UPGRADE_HEADER = 'Upgrade: websocket\r\n'
_CONNECTION_HEADER = 'Connection: Upgrade\r\n'

_GOODBYE_MESSAGE = 'Goodbye'

_PROTOCOL_VERSION_HYBI13 = 'hybi13'

NAME = "Connection: "
OK_FLAG = 0
ERROR_FLAG = -1


class Connection(object):

	def __init__(self, configFile):
		self.configFile = configFile
		configReader = ConfigurationReader(self.configFile)
		self.dictionary=configReader.readConfigFile()
		self._socket = None
		self.list=[]

	def connect(self, host, port, resource):
		self._socket = socket.socket()
		self.dictionary['server_port'] = port
		self.dictionary['server_host'] = host
		self.dictionary['resource'] = resource
		self._socket.settimeout(int(self.dictionary.get('socket_timeout')))
		try:
			#logger.logInfo(NAME + "connecting to " + host + ":" + str(port) + resource )
			self._socket.connect((host, int(port)))
			self.isConnected = True
			if self.dictionary.get('use_tls') == 'True':
				self._socket = _TLSSocket(self._socket)

			version = self.dictionary.get('protocol_version')

			self._handshake = ClientHandshakeProcessor(
				self._socket, self.dictionary)

			self._handshake.handshake()

			#logger.logInfo(NAME + 'Nawiazano polaczenie z ' + host+":"+str(port))

			request = ClientRequest(self._socket)

			version_map = {
			_PROTOCOL_VERSION_HYBI13: common.VERSION_HYBI13}
			request.ws_version = version_map[version]

			stream_option = StreamOptions()
			stream_option.mask_send = True
			stream_option.unmask_receive = False

			self._stream = Stream(request, stream_option)
			return OK_FLAG
		except Exception, e:
			self.isConnected = False
			#logger.logError(NAME+"Wystapil problem")
			#logger.logError(NAME + e.message)
			print(e.message)
			return ERROR_FLAG

	def send_message(self, message):
		if self.isConnected == True:
			self._stream.send_message(message)

	def get_message(self):
		if self.isConnected == True:
			message = self._stream.receive_message()
			return message
		return ""

	def _do_closing_handshake(self):
		self._socket.close()



import logging
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

	def connect(self, host, port):
		self._socket = socket.socket()
		self.dictionary['server_port'] = port
		self.dictionary['server_host'] = host
		self._socket.settimeout(int(self.dictionary.get('socket_timeout')))
		try:
			self._socket.connect((host, int(port)))
			if self.dictionary.get('use_tls') == 'True':
				self._socket = _TLSSocket(self._socket)

			version = self.dictionary.get('protocol_version')

			self._handshake = ClientHandshakeProcessor(
				self._socket, self.dictionary)

			self._handshake.handshake()

			logging.error(NAME + 'Connection established with ' + host+":"+str(port))

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
			logging.error(NAME+"Wystapil nieznany problem")
			logging.error(e.message)
			return ERROR_FLAG

	def send_message(self, message):
		self._stream.send_message(message)
		logging.error(NAME + "Message send " + message)

	def get_message(self):
		message = self._stream.receive_message()
		logging.error(NAME + "Message recived " + message)
		return message

	def _do_closing_handshake(self):
		self._stream.close_connection()

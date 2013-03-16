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


class Connection(object):

	def __init__(self, configFile):
		self.configFile = configFile
		configReader = ConfigurationReader(self.configFile)
		self.dictionary=configReader.readConfigFile()
		logging.basicConfig(level=logging.getLevelName(self.dictionary.get('log_level').upper()))
		self._socket = None
		self.list=[]

	def connect(self, host, port):
		self._socket = socket.socket()
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

			if self.dictionary.get('deflate_stream') == 'True':
				stream_option.deflate_stream = True

			if self.dictionary.get('deflate_frame') == 'True':
				processor = True
				processor.setup_stream_options(stream_option)

			self._stream = Stream(request, stream_option)
		except Exception, e:
			logging.error(NAME+"Wystapil nieznany problem")
			logging.error(e.message)
			return

	def send_message(self, message):
		self._stream.send_message(message)
		logging.error(NAME + "Message send " + message)

	def get_message(self):
		message = self._stream.receive_message()
		logging.error(NAME + "Message recived " + message)
		return message

	def _do_closing_handshake(self):
		self._stream.close_connection()

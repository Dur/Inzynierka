import logging
import socket
from mod_pywebsocket import common
from mod_pywebsocket.stream import Stream
from mod_pywebsocket.stream import StreamOptions
from WebSocket._TLSSocket import _TLSSocket
from WebSocket.ClientRequest import ClientRequest
from WebSocket.ClientHandshakeProcessor import ClientHandshakeProcessor

NAME = "PingConnection: "
_UPGRADE_HEADER = 'Upgrade: websocket\r\n'
_CONNECTION_HEADER = 'Connection: Upgrade\r\n'

_GOODBYE_MESSAGE = 'Goodbye'

_PROTOCOL_VERSION_HYBI13 = 'hybi13'
CONNECTION_PROBLEM_FLAG = -1
CONNECTION_OK_FLAG = 0


class PingConnection(object):

	_stream = None

	def __init__(self, configFile):
		self.configFile = configFile
		self.dictionary=dict()
		with open(self.configFile, 'r') as f:
			for singleLine in f:
				singleLine = singleLine.replace('\n','')
				splitedLine = singleLine.split('=')
				self.dictionary[splitedLine[0]] = splitedLine[1]
		self._socket = None

	def connect(self, host, port, resource):
		self.dictionary['server_port'] = port
		self.dictionary['server_host'] = host
		self.dictionary['resource'] = resource
		self._socket = socket.socket()
		self._socket.settimeout(int(self.dictionary.get('socket_timeout')))
		try:
			self._socket.connect((host,int(port)))
			if self.dictionary.get('use_tls') == 'True':
				self._socket = _TLSSocket(self._socket)

			version = self.dictionary.get('protocol_version')

			self._handshake = ClientHandshakeProcessor(
				self._socket, self.dictionary)

			self._handshake.handshake()

			request = ClientRequest(self._socket)

			version_map = {
			_PROTOCOL_VERSION_HYBI13: common.VERSION_HYBI13}
			request.ws_version = version_map[version]

			stream_option = StreamOptions()
			stream_option.mask_send = True
			stream_option.unmask_receive = False

			self._stream = Stream(request, stream_option)
			logging.error(NAME+ "connection ok")
			return CONNECTION_OK_FLAG
		except:
			self._socket.close()
			logging.error(NAME+ "unable to connect")
			return CONNECTION_PROBLEM_FLAG

	def send_message(self, message):
		self._stream.send_message(message)

	def get_message(self):
		return self._stream.receive_message()

	def _do_closing_handshake(self):
		self._socket.close()

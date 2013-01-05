from mod_pywebsocket.msgutil import MessageReceiver, MessageSender
from ClientHandshakeProcessor import ClientHandshakeProcessor
from ClientRequest import ClientRequest
from ListenSocket import ListenSocket
from _TLSSocket import _TLSSocket

import logging
import socket


from mod_pywebsocket import common
from mod_pywebsocket.stream import Stream
from mod_pywebsocket.stream import StreamOptions
from mod_pywebsocket import util

_UPGRADE_HEADER = 'Upgrade: websocket\r\n'
_CONNECTION_HEADER = 'Connection: Upgrade\r\n'

_GOODBYE_MESSAGE = 'Goodbye'

_PROTOCOL_VERSION_HYBI13 = 'hybi13'


class Connection(object):

	def __init__(self, configFile):
		print "connection init"
		self.configFile = configFile
		self.dictionary=dict()
		with open(self.configFile, 'r') as f:
			for singleLine in f:
				singleLine = singleLine.replace('\n','')
				splitedLine = singleLine.split('=')
				self.dictionary[splitedLine[0]] = splitedLine[1]
		print self.dictionary
		logging.basicConfig(level=logging.getLevelName(self.dictionary.get('log_level').upper()))
		self._socket = None
		self.list=[]
		self._logger = util.get_class_logger(self)

	def connect(self):

		self._socket = socket.socket()
		self._socket.settimeout(int(self.dictionary.get('socket_timeout')))
		try:
			self._socket.connect((self.dictionary.get('server_host'),
			                      int(self.dictionary.get('server_port'))))
			print "Conneting to %s" %self.dictionary.get('server_host')
			if self.dictionary.get('use_tls') == 'True':
				self._socket = _TLSSocket(self._socket)

			version = self.dictionary.get('protocol_version')

			self._handshake = ClientHandshakeProcessor(
				self._socket, self.dictionary)

			self._handshake.handshake()

			self._logger.info('Connection established')

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
			thread = ListenSocket("Thread",self, self.list)
			thread.start()
		finally:
			print "po powitaniu, serwer oczekuje na dane"

	def send(self, message):
		for line in message.split(','):
			self._stream.send_message(line)
			print 'Send: %s' % line

	def get_message(self):
		if not self.list:
			return(None)
		else:
			return self.list.pop(0)

	def _do_closing_handshake(self):
		"""Perform closing handshake using the specified closing frame."""

		if self.dictionary.get('message').split(',')[-1] == _GOODBYE_MESSAGE:
			# requested server initiated closing handshake, so
			# expecting closing handshake message from server.
			self._logger.info('Wait for server-initiated closing handshake')
			message = self._stream.receive_message()
			if message is None:
				return
		self._stream.close_connection()

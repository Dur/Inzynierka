from threading import Thread
from mod_pywebsocket._stream_base import ConnectionTerminatedException
import logging

__author__ = 'dur'

class ListenSocket( Thread ):

	def run(self):
		try:
			logging.error("wewnatrz watku")
			while( True ):
				received = self.connection._stream.receive_message()
				self.dispatcher.dispatch(received)
				logging.error("received %s", received)

		except ConnectionTerminatedException, a:
			logging.error( "Server closed connection in listenSocket")
			self.connection._socket.close()
			return
		except Exception, e:
			logging.error( "Error occurred in listenSocket")
			self.connection._socket.close()
			return

	def __init__(self, connection, dispatcher):
		Thread.__init__(self)
		self.dispatcher = dispatcher
		self.connection = connection

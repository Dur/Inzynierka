from threading import Thread
from mod_pywebsocket._stream_base import ConnectionTerminatedException
import time
import logging

__author__ = 'dur'

class ListenSocket( Thread ):

	def run(self):
		try:
			while( True ):
				received = self.connection._stream.receive_message()
				self.dispatcher.dispatch(received)
				logging.error("received %s", received)
				time.sleep(10)

		except ConnectionTerminatedException, a:
			logging.error( "Server closed connection")
			self.connection._socket.close()
			return
		except Exception, e:
			self.connection._socket.close()
			return

	def __init__(self, connection, dispatcher):
		Thread.__init__(self)
		self.dispatcher = dispatcher
		self.connection = connection

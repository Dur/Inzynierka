from threading import Thread
from mod_pywebsocket._stream_base import ConnectionTerminatedException
import logging

__author__ = 'dur'

class ListenSocket( Thread ):

	def run(self):
#		try:
		logging.error("wewnatrz watku")
		while( True ):
			received = self.stream.receive_message()
			logging.error("received %s", received)
			if( received == "Ping"):
				self.stream.send_message("Pong")
#				self.dispatcher.dispatch(received)

#		except ConnectionTerminatedException, a:
#			logging.error( "Server closed connection in listenSocket")
#			logging.error(a.message)
#			raise
#			return
#		except Exception, e:
#			logging.error( "Error occurred in listenSocket")
#			logging.error(e.message)
#			raise
#			return

	def __init__(self, stream, dispatcher, queue):
		Thread.__init__(self)
		self.dispatcher = dispatcher
		self.stream = stream
		self.queue = queue

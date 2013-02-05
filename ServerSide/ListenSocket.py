from threading import Thread
from mod_pywebsocket._stream_base import ConnectionTerminatedException
import logging

__author__ = 'dur'
NAME = "ListenSocket: "
class ListenSocket( Thread ):

	def run(self):
		try:
			logging.error(NAME+"wewnatrz watku")
			while( True ):
				received = self.stream.receive_message()
				logging.error(NAME+"odebrano %s", received)
				self.dispatch(self, received)
		except Exception, e:
			logging.error(NAME+"Wystapil nieznany problem")
			logging.error(e.message)
			return

	def __init__(self, stream, queue):
		Thread.__init__(self)
		self.stream = stream
		self.queue = queue

	def dispatch(self, message):
		if( message == "Ping"):
			self.stream.send_message("Pong")
			logging.error(NAME+"wyslano Pong")
		if (message == "Pong" ):
			self.queue.put(message)
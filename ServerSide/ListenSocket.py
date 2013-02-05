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
				if( received == "Ping"):
					self.stream.send_message("Pong")
					logging.error(NAME+"wyslano Pong")
	#				self.dispatcher.dispatch(received)
				if (received == "Pong" ):
					self.queue.put(received)
		except Exception, e:
			logging.error(NAME+"Error occurred in listenSocket")
			logging.error(e.message)
			return

	def __init__(self, stream, dispatcher, queue):
		Thread.__init__(self)
		self.dispatcher = dispatcher
		self.stream = stream
		self.queue = queue

from threading import Thread
from mod_pywebsocket._stream_base import ConnectionTerminatedException

__author__ = 'dur'

class ListenSocket( Thread ):

	def run(self):
		try:
			while True:
				print("wating for messag from remote")
				received = self.connection._stream.receive_message()
				print("got message from remote")
				self.queue.put(received)
				print("added message from remote")

		except ConnectionTerminatedException, a:
			print "Server closed connection"
			return
		except Exception, e:
			print"exception %s" %e
			self.connection._do_closing_handshake()
			self.connection._socket.close()
			return

	def __init__(self, connection, queue):
		Thread.__init__(self)
		self.queue = queue
		self.connection = connection
		print "Listen thread created"
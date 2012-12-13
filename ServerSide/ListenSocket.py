from threading import Thread
from mod_pywebsocket._stream_base import ConnectionTerminatedException

__author__ = 'dur'

class ListenSocket( Thread ):

	def run(self):
		try:
			received = self.connection._stream.receive_message()
			while received != "":
				self.list.append(received)
				received = self.connection._stream.receive_message()

		except ConnectionTerminatedException, a:
			print "Server closed connection"
			return
		except Exception, e:
			print"exception %s" %e
			self.connection._do_closing_handshake()
			self.connection._socket.close()
			return

	def __init__(self, name, connection, list):
		Thread.__init__(self)
		self.name = name
		self.list = list
		self.connection = connection
		print "thread %s created" %name
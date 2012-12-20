from threading import Thread
from mod_pywebsocket._stream_base import ConnectionTerminatedException
import time

__author__ = 'dur'
class TestSender(Thread):
	def run(self):
		try:
			while True:
				self.connection.send("Read")
				time.sleep(2)

		except ConnectionTerminatedException, a:
			print "Server closed connection"
			return
		except Exception, e:
			print"exception %s" %e
			self.connection._do_closing_handshake()
			self.connection._socket.close()
			return

	def __init__(self, connection):
		Thread.__init__(self)
		self.connection = connection

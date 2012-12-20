from threading import Thread
from mod_pywebsocket._stream_base import ConnectionTerminatedException

__author__ = 'dur'

class WriteSocket(Thread):
	def run(self):
		try:
			while True:
				print("Waiting for message to send")
				line = self.queue.get(True)
				self.connection._stream.send_message(line)
				print("Message sent")

		except ConnectionTerminatedException, a:
			print "Server closed connection"
			return
		except Exception, e:
			print"exception %s" % e
			self.connection._do_closing_handshake()
			self.connection._socket.close()
			return

	def __init__(self, connection, queue):
		Thread.__init__(self)
		self.queue = queue
		self.connection = connection
		print "write thread created"
import utils.Logger as logger
from threading import Thread
from Queue import Queue
from Queue import Empty

__author__ = 'dur'
NAME = "KillableListenThread "

class _ListenThread(Thread):

	def __init__(self, socket, queue):
		Thread.__init__(self)
		self.socket = socket
		self.queue = queue
		self.setDaemon(True)

	def run(self):
		while True:
			self.queue.put(self.socket.receive_message())

class KillableListenThread(Thread):

	def __init__(self, socket, stopQueue):
		Thread.__init__(self)
		self.internalQueue = Queue()
		self.listener = _ListenThread(socket, self.internalQueue)
		self.socket = socket
		self.messageQueue = Queue()
		self.stopQueue = stopQueue
		self.stop = False

	def run(self):
		self.listener.start()
		while(self.stopQueue.empty()):
			try:
				message = self.internalQueue.get(True, 2)
			except Empty:
				logger.logInfo(NAME + "No message")
				continue
			self.messageQueue.put(message)

	def getMessage(self, waitTime):
		try:
			message = self.internalQueue.get(True, waitTime)
			return message
		except Empty:
			return None
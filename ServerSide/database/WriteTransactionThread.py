from threading import Thread
__author__ = 'dur'
import logging
NAME = "WriteTransactionThread: "
STOP_THREAD = "INTERRUPT"
LOCALHOST_NAME = "localhost"
PREPARE = "PREPARE"
GLOBAL_COMMIT = "GLOBAL_COMMIT"
ABORT = "ABORT"
GLOBAL_ABORT = "GLOBAL_ABORT"
OK = "OK"
class WriteTransactionThread(Thread):

	outputQueue = None
	inputQueue = None
	eventVariable = None
	clientAddress = None
	commands = []

	def __init__(self, outputQueue, inputQueue, eventVariable, clientAddress, commands):
		Thread.__init__(self)
		self.clientAddress = clientAddress
		self.inputQueue = inputQueue
		self.eventVariable = eventVariable
		self.outputQueue = outputQueue
		self.commands = commands


	def run(self):
		methodMapping = {PREPARE : self.prepare, GLOBAL_COMMIT : self.globalCommit, GLOBAL_ABORT : self.globalAbort}
		command = self.inputQueue.get(True, None)

		while command != STOP_THREAD:
			methodMapping[command]()
			command = self.inputQueue.get(True, None)
		print "Konice watku"

	def prepare(self):

		print "prepareMethod"
	def globalCommit(self):
		print "globalCommitMethod"
	def globalAbort(self):
		print 'globalAbortMethod'


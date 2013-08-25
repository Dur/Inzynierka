from threading import Thread
import utils.Logger as logger

__author__ = 'dur'

NAME = "ListenSocket: "

class ListenSocket( Thread ):

	def __init__(self, paramsDictionary, modules):
		Thread.__init__(self)
		self.paramsDictionary = paramsDictionary
		self.modules = modules

	def run(self):
		try:
			logger.logInfo(NAME+"wewnatrz watku")
			while( True ):
				logger.logInfo(NAME+"Oczekiwanie na wiadomosc")
				received = self.paramsDictionary["SOCKET"].receive_message()
				logger.logInfo(NAME+"odebrano " + received)
				if received != None:
					self.dispatch(received)
				else:
					logger.logError(NAME+"odebrano pusta wiadomosc")
		except Exception, e:
			logger.logError(NAME+"Wystapil problem z polaczeniem")
			logger.logError(NAME + e.message)
			raise Exception("Problem z polaczeniem w watku nasluchujacym")


	def dispatch(self, message):
		splited = message.split(':')
		module = splited[0]
		if len(splited) > 1:
			message = splited[1]
		else:
			message = None
		if( self.modules[module] != None ):
			logger.logInfo(NAME+"znaleziono modul odpowiadajacy za obsluge")
			for singleModule in self.modules[module]:
				singleModule.execute(self.paramsDictionary, message)
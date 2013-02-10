from threading import Thread
import logging

__author__ = 'dur'

NAME = "ListenSocket: "

class ListenSocket( Thread ):

	def __init__(self, paramsDictionary, modules):
		Thread.__init__(self)
		self.paramsDictionary = paramsDictionary
		self.modules = modules

	def run(self):
		try:
			logging.error(NAME+"wewnatrz watku")
			while( True ):
				received = self.paramsDictionary["SOCKET"].receive_message()
				logging.error(NAME+"odebrano %s", received)
				self.dispatch(received)
		except Exception, e:
			logging.error(NAME+"Wystapil nieznany problem")
			logging.error(e.message)
			return


	def dispatch(self, message):
		if( self.modules[message] != None ):
			logging.error(NAME+"znaleziono modul odpowiadajacy za obsluge")
			for singleModule in self.modules[message]:
				singleModule.execute(self.paramsDictionary)
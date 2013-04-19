import logging
from utils.FileProcessors import FileProcessor

__author__ = 'dur'

NAME = "StandardHostDC: "

def execute(paramsDictionary, message):
	logging.info(NAME+ "Wlaczam dodatkowe opcje przy odlaczaniu serwera")
	file = FileProcessor(paramsDictionary["HOME_PATH"]+"ServerSide/config/addresses.conf")
	if( paramsDictionary["CONNECTION_MODE"] == True ):
		paramsDictionary["CONNECTION"]._socket.close()
	logging.info(NAME+ "Proba zapisu do pliku adresowego")
	writeOk = False
	while writeOk != True:
		try:
			file.lockFile()
			logging.info(NAME + "Plik adresowy zablokowany")
			writeOk = True
			addresses = file.readFile()
			addresses[paramsDictionary["CLIENT_ADDRESS"]] = 'F'
			file.writeToFile(addresses)
			file.unlockFile()
			logging.info(NAME+ "Plik adresowy zaktualizowany")
			if file.lock.is_locked:
				file.unlockFile()
		except Exception, e:
			logging.error(NAME + "Nie mozna zablokowac pliku adresowego, czekanie bedzie wznowione")


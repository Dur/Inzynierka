import utils.Logger as logger
from utils.FileProcessors import FileProcessor

__author__ = 'dur'

NAME = "StandardHostDC: "

def execute(paramsDictionary, message):
	remoteAddress = paramsDictionary["CLIENT_ADDRESS"]
	logger.logImportant(NAME+ "Wykryto odlaczenie serwera " + remoteAddress)
	file = FileProcessor(paramsDictionary["HOME_PATH"]+"ServerSide/config/addresses.conf")
	if( paramsDictionary["CONNECTION_MODE"] == True ):
		paramsDictionary["CONNECTION"]._socket.close()
	logger.logInfo(NAME+ "Proba zapisu do pliku adresowego")
	writeOk = False
	while writeOk != True:
		try:
			file.lockFile()
			logger.logInfo(NAME + "Plik adresowy zablokowany")
			writeOk = True
			addresses = file.readFile()
			addresses[paramsDictionary["CLIENT_ADDRESS"]] = 'F'
			file.writeToFile(addresses)
			file.unlockFile()
			logger.logInfo(NAME+ "Plik adresowy zaktualizowany")
			if file.lock.is_locked:
				file.unlockFile()
		except Exception, e:
			logger.logError(NAME + "Nie mozna zablokowac pliku adresowego, czekanie bedzie wznowione")


from os import remove
import utils.Logger as logger
from utils.FileProcessors import FileProcessor
__author__ = 'dur'

'''Modul sluzacy do uwierzytelniania serwerow przy uzyciu hasle krotkotrwalych'''

GET_PASSWORD = "PASSWORD?"
PASSWORD_OK = "PASS_OK"
WRONG_PASSWORD = "AUTH_FAILD"
NAME = "AuthNewConn: "

def execute(paramsDictionary, message):
	logger.logInfo(NAME + "Wewnatrz modulu autoryzacji")
	if paramsDictionary["CONNECTION_MODE"] == True:
		authConnectionMode(paramsDictionary)
	else:
		authRequestMode(paramsDictionary)

def authConnectionMode(paramsDictionary):
	remoteAddress = paramsDictionary["CLIENT_ADDRESS"]
	logger.logImportant(NAME + "Uwierzytelnianie podlaczajacego sie serwera " + remoteAddress)
	socket = paramsDictionary["SOCKET"]
	homePath = paramsDictionary["HOME_PATH"]
	logger.logImportant(NAME + "przed wyslaniem zapytania o haslo")
	socket.send_message(GET_PASSWORD)
	logger.logImportant(NAME + "Oczekiwanie na haslo od serwera")
	password = socket.receive_message()

	logger.logImportant(NAME + "Otrzymano haslo od " + remoteAddress)
	processor = FileProcessor(homePath+"ServerSide/config/pass/all_to_me.pass")
	passwords = processor.readFile()
	logger.logInfo(NAME + "spodziewane haslo " + passwords[remoteAddress] + " otrzymano " + password )
	if(passwords[remoteAddress] == password ):
		logger.logImportant(NAME + "Haslo otrzymane od " + remoteAddress + " zgodne")

		socket.send_message(PASSWORD_OK)

		logger.logInfo(NAME + "czekam na zapytanie o haslo")

		message = socket.receive_message()

		if  message == GET_PASSWORD:
			processor = FileProcessor(homePath+"ServerSide/config/pass/me_to_all.pass")
			passwords = processor.readFile()
			logger.logImportant(NAME + "Wysylam swoje haslo do " + remoteAddress)

			socket.send_message(passwords[remoteAddress])

			message = socket.receive_message()

		if message == PASSWORD_OK:
			logger.logImportant(NAME + "Haslo zaakceptowane przez " + remoteAddress)
			pass
		else:
			logger.logError(NAME + "Haslo pzeslane przez " + remoteAddress + " niezgodne, zamykanie polaczenia")
			paramsDictionary["CONNECTION"]._socket.close()
	else:
		logger.logError(NAME + "Haslo pzeslane przez " + remoteAddress + " niezgodne, zamykanie polaczenia")
		socket.send_message(WRONG_PASSWORD)
		paramsDictionary["CONNECTION"]._socket.close()



def authRequestMode(paramsDictionary):
	remoteAddress = paramsDictionary["CLIENT_ADDRESS"]
	logger.logImportant(NAME + "Uwierzytelnianie serwera " + remoteAddress)
	socket = paramsDictionary["SOCKET"]

	homePath = paramsDictionary["HOME_PATH"]

	message = socket.receive_message()

	if  message == GET_PASSWORD:
		processor = FileProcessor(homePath+"ServerSide/config/pass/me_to_all.pass")
		passwords = processor.readFile()
		logger.logImportant(NAME + "Wysylam swoje haslo do " + remoteAddress)

		socket.send_message(passwords[remoteAddress])

		message = socket.receive_message()

	if message == PASSWORD_OK:
		socket.send_message(GET_PASSWORD)

		password = socket.receive_message()

		logger.logImportant(NAME + "Otrzymano haslo od " + remoteAddress)
		processor = FileProcessor(homePath+"ServerSide/config/pass/all_to_me.pass")
		passwords = processor.readFile()
		logger.logInfo(NAME + "spodziewane haslo " + passwords[remoteAddress] + " otrzymano " + password )
		if(passwords[remoteAddress] == password ):
			logger.logImportant(NAME + "Haslo od " + remoteAddress + " zgodne")

			socket.send_message(PASSWORD_OK)
		else:
			logger.logError(NAME + "Haslo pzeslane przez " + remoteAddress + " niezgodne, zamykanie polaczenia")
			socket.send_message(WRONG_PASSWORD)
	else:
		logger.logError(NAME + "Haslo pzeslane przez " + remoteAddress + " niezgodne, zamykanie polaczenia")
	pass
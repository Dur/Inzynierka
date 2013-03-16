from utils.FileProcessors import FileProcessor

__author__ = 'dur'
import logging

expectedMessage = "NEW_PASS"
NEW_PASS = "NEW_PASS"
OLD = "OLD"
ACK = "ACK"
NEW = "NEW"
RES_MODULE = "PASS_EXCH_REQ:"
NAME = "PasswordExchangeResponse: "


def getOldPassword(paramsDictionary, argument):
	socket = paramsDictionary["SOCKET"]
	remoteAddress = paramsDictionary["CLIENT_ADDRESS"]
	homePath = paramsDictionary["HOME_PATH"]

	logging.error(NAME + "wyszukuje stare haslo")
	processor = FileProcessor(homePath+"ServerSide/config/pass/me_to_all.pass")
	passwords = processor.readFile()
	oldPass = passwords[remoteAddress]

	socket.send_message(RES_MODULE+OLD+"%"+oldPass)
	logging.error(NAME + "wyslalem stare haslo")
	global expectedMessage
	expectedMessage = NEW

def setNewPassword(paramsDictionary, newPass):
	socket = paramsDictionary["SOCKET"]
	remoteAddress = paramsDictionary["CLIENT_ADDRESS"]
	homePath = paramsDictionary["HOME_PATH"]

	logging.error(NAME + "Otrzymalem nowe haslo")
	processor = FileProcessor(homePath+"ServerSide/config/pass/me_to_all.pass")
	passwords = processor.readFile()
	passwords[remoteAddress] = newPass
	processor.lockFile()
	processor.writeToFile(passwords)
	processor.unlockFile()
	logging.error(NAME + "zapisalem nowe haslo")
	socket.send_message(RES_MODULE+ACK)
	logging.error(NAME + "Wyslalem potwierdzenie")
	global expectedMessage
	expectedMessage = NEW_PASS

functions = {NEW_PASS: getOldPassword,
             NEW: setNewPassword,
}


def execute(paramsDictionary, message):
	logging.error(NAME + "otrzymalem " + message)
	splited = message.split('%')
	toCall = splited[0]
	if len(splited) > 1:
		argument = splited[1]
	else:
		argument = None
	function = functions[toCall]
	function(paramsDictionary, argument)


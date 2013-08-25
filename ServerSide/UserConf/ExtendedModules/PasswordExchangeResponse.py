from utils.FileProcessors import FileProcessor

__author__ = 'dur'
import utils.Logger as logger

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

	#logger.logInfo(NAME + "wyszukuje stare haslo")
	processor = FileProcessor(homePath+"ServerSide/config/pass/me_to_all.pass")
	passwords = processor.readFile()
	oldPass = passwords[remoteAddress]

	socket.send_message(RES_MODULE+OLD+"%"+oldPass)
	#logger.logInfo(NAME + "wyslalem stare haslo do " + remoteAddress)
	global expectedMessage
	expectedMessage = NEW

def setNewPassword(paramsDictionary, newPass):
	socket = paramsDictionary["SOCKET"]
	remoteAddress = paramsDictionary["CLIENT_ADDRESS"]
	homePath = paramsDictionary["HOME_PATH"]

	#logger.logInfo(NAME + "Otrzymalem nowe haslo")
	processor = FileProcessor(homePath+"ServerSide/config/pass/me_to_all.pass")
	processor.lockFile()
	passwords = processor.readFile()
	passwords[remoteAddress] = newPass
	processor.writeToFile(passwords)
	processor.unlockFile()
	#logger.logInfo(NAME + "zapisalem nowe haslo")
	socket.send_message(RES_MODULE+ACK)
	#logger.logInfo(NAME + "Wyslalem potwierdzenie do " + remoteAddress)
	global expectedMessage
	expectedMessage = NEW_PASS

functions = {NEW_PASS: getOldPassword,
             NEW: setNewPassword,
}


def execute(paramsDictionary, message):
	#logger.logInfo(NAME + "otrzymalem " + message)
	splited = message.split('%')
	toCall = splited[0]
	if len(splited) > 1:
		argument = splited[1]
	else:
		argument = None
	function = functions[toCall]
	function(paramsDictionary, argument)


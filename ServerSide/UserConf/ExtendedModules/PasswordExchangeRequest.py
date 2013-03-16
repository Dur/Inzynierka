from utils.FileProcessors import FileProcessor

__author__ = 'dur'
import logging
import string
import random

expectedMessage = "OLD"
generatedPass = None
OLD = "OLD"
NEW = "NEW"
ACK = "ACK"
RES_MODULE = "PASS_EXCH_RES:"
NAME = "PasswordExchangeRequest: "
PASSWORD_LENGTH = 24


def checkOldPassword(paramsDictionary, oldPass):
	socket = paramsDictionary["SOCKET"]
	remoteAddress = paramsDictionary["CLIENT_ADDRESS"]
	homePath = paramsDictionary["HOME_PATH"]

	logging.error(NAME + "Otrzymalem stare haslo")
	processor = FileProcessor(homePath+"ServerSide/config/pass/all_to_me.pass")
	passwords = processor.readFile()
	logging.error(NAME + "spodziewane haslo " + passwords[remoteAddress] + " otrzymano " + oldPass )
	if(passwords[remoteAddress] == oldPass ):
		logging.error(NAME + "Haslo zgodne")
		global generatedPass
		generatedPass = generatePassword(PASSWORD_LENGTH)
		socket.send_message(RES_MODULE+NEW+"%"+generatedPass)
		logging.error(NAME + "Wyslalem nowe haslo")
		global expectedMessage
		expectedMessage = ACK


def acknowlage(paramsDictionary, argument):
	remoteAddress = paramsDictionary["CLIENT_ADDRESS"]
	homePath = paramsDictionary["HOME_PATH"]

	logging.error(NAME + "dostalem potwierdzenie zmiany hasla")
	file = FileProcessor(homePath+"ServerSide/config/pass/all_to_me.pass")
	file.lockFile()
	passwords = file.readFile()
	passwords[remoteAddress] = generatedPass
	file.writeToFile(passwords)
	file.unlockFile()
	logging.error(NAME + "Haslo zostalo zmienione")
	global expectedMessage
	expectedMessage = OLD
	global generatedPass
	generatedPass = None

functions = {OLD: checkOldPassword,
             ACK: acknowlage
			}


def execute(paramsDictionary, message):
	splited = message.split('%')
	toCall = splited[0]
	if len(splited) > 1:
		argument = splited[1]
	else:
		argument = None
	function = functions[toCall]
	function(paramsDictionary, argument)


def generatePassword(passwordLength):
	chars=string.ascii_letters + string.digits
	return ''.join(random.choice(chars) for x in range(passwordLength))
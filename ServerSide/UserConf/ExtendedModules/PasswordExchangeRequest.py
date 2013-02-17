__author__ = 'dur'
import logging
from FileProcessor import FileProcessor
import string
import random

expectedMessage = "NEW_PASS"
generatedPass = None
NEW_PASS = "NEW_PASS"
OLD = "OLD"
NEW = "NEW"
ACK = "ACK"
RES_MODULE = "PASS_EXCH_RES:"
NAME = "PasswordExchangeRequest: "


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
		generatedPass = generatePassword()
		socket.send_message(RES_MODULE+NEW+"%"+generatedPass)
		logging.error(NAME + "Wyslalem nowe haslo")
		global expectedMessage
		expectedMessage = ACK

def passwordExchange(paramsDictionary, argument):
	socket = paramsDictionary["SOCKET"]

	logging.error(NAME + "Wysylam zapytanie o stare haslo")
	socket.send_message(RES_MODULE+NEW_PASS)
	global expectedMessage
	expectedMessage = OLD

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
	logging.error(NAME + "Haslo zostalo zmienione" )
	global expectedMessage
	expectedMessage = NEW_PASS
	global generatedPass
	generatedPass = None

functions = {OLD: checkOldPassword,
             NEW_PASS: passwordExchange,
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


def generatePassword(size=24, chars=string.ascii_letters + string.digits):
	return ''.join(random.choice(chars) for x in range(size))
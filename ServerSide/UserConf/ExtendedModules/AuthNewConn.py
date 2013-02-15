import logging
from FileProcessor import FileProcessor
__author__ = 'dur'


GET_PASSWORD = "PASSWORD?"
PASSWORD_OK = "PASS_OK"
WRONG_PASSWORD = "AUTH_FAILD"
NAME = "AuthNewConn: "

def execute(paramsDictionary):
	logging.error(NAME + "Wewnatrz modulu autoryzacji")
	if paramsDictionary["CONNECTION_MODE"] == True:
		authConnectionMode(paramsDictionary)
	else:
		authRequestMode(paramsDictionary)

def authConnectionMode(paramsDictionary):
	logging.error(NAME + "autoryzacja dla polaczenia")
	socket = paramsDictionary["SOCKET"]
	remoteAddress = paramsDictionary["CLIENT_ADDRESS"]
	homePath = paramsDictionary["HOME_PATH"]

	socket.send_message(GET_PASSWORD)

	password = socket.receive_message()

	logging.error(NAME + "Otrzymano haslo z serwera")
	processor = FileProcessor(homePath+"ServerSide/config/pass/all_to_me.pass")
	passwords = processor.readFile()
	logging.error(NAME + "spodziewane haslo " + passwords[remoteAddress] + " otrzymano " + password )
	if(passwords[remoteAddress] == password ):
		logging.error(NAME + "Haslo zgodne")

		socket.send_message(PASSWORD_OK)

		logging.error(NAME + "czekam na zapytanie o haslo")

		message = socket.receive_message()

		if  message == GET_PASSWORD:
			processor = FileProcessor(homePath+"ServerSide/config/pass/me_to_all.pass")
			passwords = processor.readFile()
			logging.error(NAME + "wysylam swoje haslo")

			socket.send_message(passwords[remoteAddress])

			message = socket.receive_message()

		if message == PASSWORD_OK:
			pass
		else:
			logging.error(NAME + "Haslo niezgodne zamykanie polaczenia")
			paramsDictionary["SOCKET"].close()
	else:
		logging.error(NAME + "Haslo pzeslane przez serwer niezgodne zamykanie polaczenia")
		socket.send_message(WRONG_PASSWORD)
		paramsDictionary["SOCKET"].close()



def authRequestMode(paramsDictionary):
	logging.error(NAME + "Autoryzacja dla zadania")
	socket = paramsDictionary["SOCKET"]
	remoteAddress = paramsDictionary["CLIENT_ADDRESS"]
	homePath = paramsDictionary["HOME_PATH"]

	message = socket.receive_message()

	if  message == GET_PASSWORD:
		processor = FileProcessor(homePath+"ServerSide/config/pass/me_to_all.pass")
		passwords = processor.readFile()
		logging.error(NAME + "wysylam swoje haslo")

		socket.send_message(passwords[remoteAddress])

		message = socket.receive_message()

	if message == PASSWORD_OK:
		socket.send_message(GET_PASSWORD)

		password = socket.receive_message()

		logging.error(NAME + "Otrzymano haslo z serwera")
		processor = FileProcessor(homePath+"ServerSide/config/pass/all_to_me.pass")
		passwords = processor.readFile()
		logging.error(NAME + "spodziewane haslo " + passwords[remoteAddress] + " otrzymano " + password )
		if(passwords[remoteAddress] == password ):
			logging.error(NAME + "Haslo zgodne")

			socket.send_message(PASSWORD_OK)
		else:
			logging.error(NAME + "Haslo pzeslane przez serwer niezgodne zamykanie polaczenia")
			socket.send_message(WRONG_PASSWORD)
	else:
		logging.error(NAME + "Haslo niezgodne zamykanie polaczenia")
	pass
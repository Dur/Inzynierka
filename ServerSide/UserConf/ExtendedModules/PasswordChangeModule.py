__author__ = 'dur'
import logging
from FileProcessor import FileProcessor
__author__ = 'dur'

'''Modul sluzacy do uwierzytelniania serwerow przy uzyciu hasle krotkotrwalych'''

GET_PASSWORD = "PASSWORD?"
PASSWORD_OK = "PASS_OK"
WRONG_PASSWORD = "AUTH_FAILD"
NAME = "PasswordChangeModule: "

def execute(paramsDictionary, message):
	logging.error(NAME + "Wewnatrz modulu wymiany hasla")
	if paramsDictionary["CONNECTION_MODE"] == True:
		passChangeConnectionMode(paramsDictionary)
	else:
		passChangeRequestMode(paramsDictionary)

def passChangeConnectionMode(paramsDictionary):
	pass

def passChangeRequestMode(paramsDictionary):
	pass
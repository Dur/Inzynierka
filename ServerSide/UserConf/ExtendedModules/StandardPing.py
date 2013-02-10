__author__ = 'dur'

NAME = "StandardPing: "
PONG = "PONG"
import logging

def execute(paramsDictionary):
	paramsDictionary["SOCKET"].send_message(PONG)
	logging.error(NAME+"wyslano Pong")

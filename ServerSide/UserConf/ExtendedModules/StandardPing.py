__author__ = 'dur'

NAME = "StandardPing: "
PING = "PING"
PONG = "PONG:PONG"
import logging

def execute(paramsDictionary, message):
	if message == PING:
		paramsDictionary["SOCKET"].send_message(PONG)
		logging.info(NAME+"wyslano " + PONG )

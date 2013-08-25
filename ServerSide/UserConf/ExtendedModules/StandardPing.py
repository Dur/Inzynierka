__author__ = 'dur'

NAME = "StandardPing: "
PING = "PING"
PONG = "PONG:PONG"
import utils.Logger as logger

def execute(paramsDictionary, message):
	if message == PING:
		paramsDictionary["SOCKET"].send_message(PONG)
		#logger.logInfo(NAME+"wyslano " + PONG )

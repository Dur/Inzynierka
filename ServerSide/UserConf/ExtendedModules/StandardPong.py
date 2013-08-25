__author__ = 'dur'

NAME = "StandardPong: "
PONG = "PONG"
import utils.Logger as logger

def execute(paramsDictionary, message):
	if message == PONG:
		paramsDictionary["QUEUE"].put(PONG)
		logger.logInfo(NAME+"Pong wrzucony do kolejki")
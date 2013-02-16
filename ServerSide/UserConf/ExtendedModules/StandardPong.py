__author__ = 'dur'

NAME = "StandardPong: "
PONG = "PONG:PONG"
import logging

def execute(paramsDictionary, message):
	if message == PONG:
		paramsDictionary["QUEUE"].put(PONG)
		logging.error(NAME+"Pong wrzucony do kolejki")
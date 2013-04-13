__author__ = 'dur'

NAME = "StandardPong: "
PONG = "PONG"
import logging

def execute(paramsDictionary, message):
	if message == PONG:
		paramsDictionary["QUEUE"].put(PONG)
		logging.info(NAME+"Pong wrzucony do kolejki")
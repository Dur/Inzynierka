__author__ = 'dur'

NAME = "StandardPong: "
import logging

def printMe():
	print "From Pong"

def execute(paramsDictionary):
	paramsDictionary["QUEUE"].put("PONG")
	logging.error(NAME+"Pong wrzucony do kolejki")
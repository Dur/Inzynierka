__author__ = 'dur'

NAME = "StandardPong: "
import logging

def printMe():
	print "From Pong"

def execute(socket, queue, remoteAddress):
	queue.put("PONG")
	logging.error(NAME+"Pong wrzucony do kolejki")
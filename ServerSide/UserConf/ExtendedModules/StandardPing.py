__author__ = 'dur'

NAME = "StandardPing: "
PONG = "PONG"
import logging

def printMe():
	print "From Ping"

def execute(socket, queue, dummy):
	socket.send_message(PONG)
	logging.error(NAME+"wyslano Pong")

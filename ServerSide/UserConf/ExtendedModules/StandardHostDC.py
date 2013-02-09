import logging

__author__ = 'dur'

NAME = "StandardHostDC: "
def printMe():
	print "From Host DC"

def execute(socket, queue, remoteAddress):
	logging.error(NAME+ "Wlaczam dodatkowe opcje przy odlaczaniu serwera")

import logging

__author__ = 'dur'

NAME = "StandardNewConn: "

def execute(socket, queue, remoteAddress):
	logging.error(NAME+ "Wlaczam dodatkowe opcje przy podlaczaniuserwera")
	global address
	logging.error(NAME+ "######################### global %s", address)
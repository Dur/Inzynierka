__author__ = 'dur'
import logging
from Connection import Connection
import time

_GOODBYE_MESSAGE = u'Goodbye'
_READ_FILE = u"Read"

TIME_OUT = 6

def web_socket_do_extra_handshake(request):

	pass  # Always accept.


def web_socket_transfer_data(request):
	while True:
		logging.error("Server otrzymal ping")
		line = request.ws_stream.receive_message()
		logging.error("Server apache otrzymal wiadomosc")

#1000100100000000 - Ping frame in binary with no data
#1000101000000000 - Pong frame in binary with no data
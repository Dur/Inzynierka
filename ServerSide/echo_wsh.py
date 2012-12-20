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
		logging.error("Server apache oczekuje na wiadomosc")
		line = request.ws_stream.receive_message()
		logging.error("Server apache otrzymal wiadomosc")
		if line is None:
			return
		if isinstance(line, unicode):
			if line == _READ_FILE:
				with open("/home/dur/websock_handlers/file.txt", 'r') as f:
					logging.error("zaczyna czytanie")
					for singleLine in f:
						logging.error('Wyslal %s' % singleLine)
						request.ws_stream.send_message(singleLine, binary=False)
			elif line == _GOODBYE_MESSAGE:
				return
			else:
				request.ws_stream.send_message(line, binary=False)
		else:
			request.ws_stream.send_message(line, binary=True)
		logging.error("przd nawiazaniem polaczenia")
#		con = Connection()
#		con.connect()
#		logging.error("po polaczeniu")
#		con.send('Read')
#		logging.error("wyslano tekst")

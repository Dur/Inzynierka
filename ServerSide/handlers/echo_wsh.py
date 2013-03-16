import logging

_GOODBYE_MESSAGE = "CYA"
_READ_FILE = u"Read"

NAME = "echo_wsh: "

def web_socket_do_extra_handshake(request):

	pass  # Always accept.


def web_socket_transfer_data(request):
	while True:
		line = request.ws_stream.receive_message()
		logging.error(NAME + "Serwer otrzymal " + line)
		request.ws_stream.send_message(line)
		if line == _GOODBYE_MESSAGE:
			return

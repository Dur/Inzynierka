__author__ = 'dur'
import logging
from Connection import Connection
import time
from mod_python import apache
module = apache.import_module('/home/dur/Pulpit/test2.py')

_GOODBYE_MESSAGE = u'Goodbye'
_READ_FILE = u"Read"

TIME_OUT = 6

def web_socket_do_extra_handshake(request):

	pass  # Always accept.


def web_socket_transfer_data(request):
	while True:
		logging.error("Server otrzymal ping")
		message = request.ws_stream.receive_message()
		host = request.hostname
		if ('foo' not in module.dict):
			module.dict['foo'] = 'bar'
			logging.error("added to cache")
		else:
			logging.error("value alreday in cache")
			module.dict['foo'] = module.dict['foo']+'a'
		logging.error(module.dict['foo'] )
	#		with FileLock("/home/dur/Projects/ServerSide/addresses.conf"):
		logging.error("################# sending ping")
		request.ws_stream.send_message("1000100100000000", binary=True)
		logging.error(request.connection.local_addr)


#1000100100000000 - Ping frame in binary with no data
#1000101000000000 - Pong frame in binary with no data
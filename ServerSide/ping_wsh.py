from Queue import Queue
from mod_pywebsocket._stream_base import ConnectionTerminatedException

__author__ = 'dur'
import logging
from FileProcessor import FileProcessor
from PingConnection import PingConnection
from ListenSocket import ListenSocket
from Dispatcher import Dispatcher
import time

def web_socket_do_extra_handshake(request):
	pass  # Always accept.


def web_socket_transfer_data(request):
	request.ws_stream.receive_message()
	remoteAddress = request.connection.remote_ip
	request.ws_stream.send_message("Pong")
	logging.error("Server otrzymal ping od " + remoteAddress)
	file = FileProcessor("/home/dur/Projects/ServerSide/addresses.conf")
	connectMode = False
	file.lockFile()
	addresses = file.readFile()
	for key in addresses:
		logging.error("key %s", key)
		logging.error("remote address %s", remoteAddress)
		logging.error("addresses[key] %s", addresses[key])
		if key == remoteAddress:
			logging.error("znalazl dopasowanie")
			if( addresses[key] != 'T' ):
				logging.error("proba nawiazania polaczenia z nowododanym serwerem")
				connection = PingConnection("/home/dur/Projects/ServerSide/ping_config.conf")
				connection.connect(remoteAddress, 80)
				connection.send("Ping")
				logging.error("nawiazywanie polaczenia z nowododanym serwerem")
				addresses[key] = 'T'
				file.writeToFile(addresses)
				connectMode = True
			break
	file.unlockFile()

	queue = Queue(0)
	logging.error("server starting pinging")
	if( connectMode ):
		listener = ListenSocket(connection._stream, Dispatcher(), queue)
	else:
		listener = ListenSocket(request.ws_stream, Dispatcher(), queue)

	listener.setDaemon(True)
	listener.start()
	while(True):
		try:
			if( connectMode ):
				connection.send("Ping")
				logging.error("sending ping to connection")
			else:
				request.ws_stream.send_message("Ping")
				logging.error("sending ping to request")
			message = queue.get(True, 2)
			if message == None:
				raise ConnectionTerminatedException("Server closed connection")
			time.sleep(2)

		except ConnectionTerminatedException, a:
			logging.error( "Server closed connection in ping_wsh")
			logging.error(a.message)
			connection._socket.close()
			logging.error("trying to write to file F")
			file.lockFile()
			addresses = file.readFile()
			for key in addresses:
				if key == remoteAddress:
					addresses[key] = 'F'
					file.writeToFile(addresses)
					file.unlockFile()
					logging.error("wrote to file F")
			if file.lock.is_locked:
				file.unlockFile()
			return
		except Exception, e:
			logging.error( "error in ping_wsh closing connection")
			connection._socket.close()
			logging.error("trying to write to file F")
			file.lockFile()
			addresses = file.readFile()
			for key in addresses:
				if key == remoteAddress:
					addresses[key] = 'F'
					file.writeToFile(addresses)
					file.unlockFile()
					logging.error("wrote to file F")
			logging.error("error occurred in ping_wsh")
			logging.error(e.message)
			if file.lock.is_locked:
				file.unlockFile()
			return

	#1000100100000000 - Ping frame in binary with no data
	#1000101000000000 - Pong frame in binary with no data
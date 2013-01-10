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
		logging.log("key %s", key)
		logging.log("remote address %s", remoteAddress)
		if key == remoteAddress:
			logging.error("znalazl dopasowanie")
			if( addresses[key] != 'T' ):
				logging.error("proba nawiazania polaczenia z nowododanym serwerem")
				connection = PingConnection("/home/dur/Projects/ServerSide/ping_config.conf")
				connection.connect(remoteAddress, 80)
				logging.error("nawiazywanie polaczenia z nowododanym serwerem")
				listener = ListenSocket(connection, Dispatcher())
				listener.setDaemon(True)
				listener.run()
				logging.error("watek wystartowal")
				addresses[key] = 'T'
				file.writeToFile(addresses)
				connectMode = True
			break
	file.unlockFile()

	logging.error("server starting pinging")
	while(True):
		try:
			if( connectMode ):
				connection.send("Ping")
				logging.error("sending ping to connection")
			else:
				request.ws_stream.send_message("Ping")
				logging.error("sending ping to request")
			time.sleep(2)

		except ConnectionTerminatedException, a:
			logging.error( "Server closed connection in ping_wsh")
			connection._socket.close()
			file.lockFile()
			addresses = file.readFile()
			for key in addresses:
				if key == remoteAddress:
					addresses[key] != 'F'
					file.writeToFile(addresses)
					file.unlockFile()
			if file.lock.is_locked:
				file.unlockFile()
			return
		except Exception, e:
			connection._socket.close()
			file.lockFile()
			addresses = file.readFile()
			for key in addresses:
				if key == remoteAddress:
					addresses[key] != 'F'
					file.writeToFile(addresses)
					file.unlockFile()
			logging.error("error occurred in ping_wsh")
			if file.lock.is_locked:
				file.unlockFile()
			return

	#1000100100000000 - Ping frame in binary with no data
	#1000101000000000 - Pong frame in binary with no data
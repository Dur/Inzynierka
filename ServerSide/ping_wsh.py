import Queue
from mod_pywebsocket._stream_base import ConnectionTerminatedException

__author__ = 'dur'
import logging
from FileProcessor import FileProcessor
from PingConnection import PingConnection
from ListenSocket import ListenSocket
from Dispatcher import Dispatcher
import time
NAME = "ping_wsh: "
def web_socket_do_extra_handshake(request):
	pass  # Always accept.


def web_socket_transfer_data(request):
	request.ws_stream.receive_message()
	remoteAddress = request.connection.remote_ip
	request.ws_stream.send_message("Pong")
	logging.error(NAME+ "Server otrzymal ping od " + remoteAddress)
	file = FileProcessor("/home/dur/Projects/ServerSide/addresses.conf")
	connectMode = False
	file.lockFile()
	addresses = file.readFile()
	for key in addresses:
		logging.error(NAME+ "key %s", key)
		logging.error(NAME+ "remote address %s", remoteAddress)
		logging.error(NAME+ "addresses[key] %s", addresses[key])
		if key == remoteAddress:
			logging.error(NAME+ "znalazl dopasowanie")
			if( addresses[key] != 'T' ):
				logging.error(NAME+ "proba nawiazania polaczenia z nowododanym serwerem")
				connection = PingConnection("/home/dur/Projects/ServerSide/ping_config.conf")
				connection.connect(remoteAddress, 80)
				connection.send("Ping")
				logging.error(NAME+ "nawiazywanie polaczenia z nowododanym serwerem")
				addresses[key] = 'T'
				file.writeToFile(addresses)
				connectMode = True
			break
	file.unlockFile()

	queue = Queue.Queue(0)
	logging.error(NAME+ "server starting pinging")
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
				logging.error(NAME+ "sending ping to connection")
			else:
				request.ws_stream.send_message("Ping")
				logging.error(NAME+ "sending ping to request")
			queue.get(True, 2)
			time.sleep(2)
		except Queue.Empty:
			logging.error(NAME + "serwer nie otrzymal odpowiedzi na Ping zamykanie polaczenia")
			if( connectMode ):
				connection._socket.close()
			logging.error(NAME+ "trying to write to file F")
			file.lockFile()
			addresses = file.readFile()
			for key in addresses:
				if key == remoteAddress:
					addresses[key] = 'F'
					file.writeToFile(addresses)
					file.unlockFile()
					logging.error(NAME+ "wrote to file F")
			if file.lock.is_locked:
				file.unlockFile()
			return

		except ConnectionTerminatedException, a:
			logging.error(NAME+ "Server closed connection in ping_wsh")
			logging.error(a.message)
			if( connectMode ):
				connection._socket.close()
			logging.error(NAME+ "trying to write to file F")
			file.lockFile()
			addresses = file.readFile()
			for key in addresses:
				if key == remoteAddress:
					addresses[key] = 'F'
					file.writeToFile(addresses)
					file.unlockFile()
					logging.error(NAME+ "wrote to file F")
			if file.lock.is_locked:
				file.unlockFile()
			return
		except Exception, e:
			logging.error(NAME+ "error in ping_wsh closing connection")
			if( connectMode ):
				connection._socket.close()
			logging.error(NAME+ "trying to write to file F")
			file.lockFile()
			addresses = file.readFile()
			for key in addresses:
				if key == remoteAddress:
					addresses[key] = 'F'
					file.writeToFile(addresses)
					file.unlockFile()
					logging.error(NAME+ "wrote to file F")
			logging.error(e.message)
			if file.lock.is_locked:
				file.unlockFile()
			return

	#1000100100000000 - Ping frame in binary with no data
	#1000101000000000 - Pong frame in binary with no data
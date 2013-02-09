import Queue
from mod_pywebsocket._stream_base import ConnectionTerminatedException
from ModulesLoader import ModulesLoader

__author__ = 'dur'
import logging
from FileProcessor import FileProcessor
from PingConnection import PingConnection
from ListenSocket import ListenSocket
import time

NAME = "ping_wsh: "
PING = "PING"
PONG = "PONG"

def web_socket_do_extra_handshake(request):
	pass  # Always accept.


def web_socket_transfer_data(request):
	loader = ModulesLoader()
	modules = loader.loadModules("/home/dur/Projects/ServerSide/config/modules.ext")
	logging.error(NAME+ "server loaded modules")
	request.ws_stream.receive_message()
	remoteAddress = request.connection.remote_ip
	request.ws_stream.send_message(PONG)
	logging.error(NAME+ "Server otrzymal ping od " + remoteAddress)
	file = FileProcessor("/home/dur/Projects/ServerSide/config/addresses.conf")
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
				connection = PingConnection("/home/dur/Projects/ServerSide/config/ping_config.conf")
				connection.connect(remoteAddress, 80)
				connection.send(PING)
				logging.error(NAME+ "nawiazywanie polaczenia z nowododanym serwerem")
				addresses[key] = 'T'
				file.writeToFile(addresses)
				connectMode = True
			break
	file.unlockFile()

	queue = Queue.Queue(0)

	logging.error(NAME+ "server starting pinging")
	if( connectMode ):
		listener = ListenSocket(connection._stream, queue, modules)
	else:
		listener = ListenSocket(request.ws_stream, queue, modules)
	listener.setDaemon(True)
	listener.start()
	wasError = False
	while(True):
		try:
			if( connectMode ):
				connection.send(PING)
				logging.error(NAME+ "sending ping to connection")
			else:
				request.ws_stream.send_message(PING)
				logging.error(NAME+ "sending ping to request")
			queue.get(True, 2)
			time.sleep(2)
		except Queue.Empty:
			wasError = True
			logging.error(NAME + "serwer nie otrzymal odpowiedzi na Ping zamykanie polaczenia")
		except ConnectionTerminatedException, a:
			wasError = True
			logging.error(NAME+ "Server closed connection in ping_wsh")
		except Exception, e:
			wasError = True
			logging.error(NAME+ "error in ping_wsh closing connection")
			logging.error(NAME + e.message)
		finally:
			if wasError:
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


	#1000100100000000 - Ping frame in binary with no data
	#1000101000000000 - Pong frame in binary with no data
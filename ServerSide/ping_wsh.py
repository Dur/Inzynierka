import Queue
from mod_pywebsocket._stream_base import ConnectionTerminatedException
from ModulesLoader import ModulesLoader
import logging
from ListenSocket import ListenSocket
import time

NAME = "ping_wsh: "
PING = "PING"
PONG = "PONG"
def web_socket_do_extra_handshake(request):
	pass  # Always accept.


def web_socket_transfer_data(request):

	logging.error(NAME+ "Server dostal zgloszenie")
	paramsDictionary = {}
	paramsDictionary["REQUEST"] = request
	paramsDictionary["CLIENT_ADDRESS"]= request.connection.remote_ip
	paramsDictionary["SOCKET"] = request.ws_stream

	paramsDictionary["SOCKET"].receive_message()
	logging.error(NAME+ "Server otrzymal ping od " + paramsDictionary["CLIENT_ADDRESS"])
	paramsDictionary["SOCKET"].send_message(PONG)
	logging.error(NAME+ "Server odpowiedzial do " + paramsDictionary["CLIENT_ADDRESS"])

	loader = ModulesLoader()
	modules = loader.loadModules("/home/dur/Projects/ServerSide/config/modules.ext")
	logging.error(NAME+ "server loaded modules")

	for singleModule in modules["NEW_CONN"]:
		singleModule.execute(paramsDictionary)

	paramsDictionary["QUEUE"] = Queue.Queue(0)

	logging.error(NAME+ "server starting pinging")
	listener = ListenSocket(paramsDictionary, modules)
	listener.setDaemon(True)
	listener.start()
	wasError = False
	while(True):
		try:
			paramsDictionary["SOCKET"].send_message(PING)
			logging.error(NAME+ "sending ping")
			paramsDictionary["QUEUE"].get(True, 2)
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
				for singleModule in modules["HOST_DC"]:
					singleModule.execute(paramsDictionary)
				return


	#1000100100000000 - Ping frame in binary with no data
	#1000101000000000 - Pong frame in binary with no data
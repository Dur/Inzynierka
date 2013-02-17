from mod_pywebsocket._stream_base import ConnectionTerminatedException

__author__ = 'dur'
import logging
import Queue
import time

PING = "PING:PING"
NAME = "PeriodicPing: "

def execute(paramsDictionary, message):
	socket = paramsDictionary["SOCKET"]
	queue = paramsDictionary["QUEUE"]
	pingWaitResponseTime = paramsDictionary["CONFIG_PARAMS"]["pingWaitResponseTime"]
	wasError = False
	try:
		socket.send_message(PING)
		logging.error(NAME+ "sending ping")
		queue.get(True, int(pingWaitResponseTime))

	except Queue.Empty:
		wasError = True
		logging.error(NAME + "serwer nie otrzymal odpowiedzi na Ping zamykanie polaczenia")

	except ConnectionTerminatedException, a:
		wasError = True
		logging.error(NAME+ "Server closed connection")

	except Exception, e:
		wasError = True
		logging.error(NAME+ "error - closing connection")
		logging.error(NAME + e.message)

	finally:
		if wasError:
			raise
			return
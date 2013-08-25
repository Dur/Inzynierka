from mod_pywebsocket._stream_base import ConnectionTerminatedException

__author__ = 'dur'
import utils.Logger as logger
import Queue

PING = "PING:PING"
NAME = "PeriodicPing: "

def execute(paramsDictionary, message):
	socket = paramsDictionary["SOCKET"]
	queue = paramsDictionary["QUEUE"]
	pingWaitResponseTime = int(paramsDictionary["CONFIG_PARAMS"]["pingWaitResponseTime"])
	#logger.logInfo(NAME + "Maksymalny czas oczekiwania na odpowiedz = " + str(pingWaitResponseTime))
	wasError = False
	errorMessage = ""

	try:
		socket.send_message(PING)
		#logger.logInfo(NAME+ "Wysylam ping")
		queue.get(True, int(pingWaitResponseTime))

	except Queue.Empty:
		wasError = True
		errorMessage = "Serwer nie otrzymal odpowiedzi na ping"
		logger.logError(NAME + "serwer nie otrzymal odpowiedzi na Ping zamykanie polaczenia")

	except ConnectionTerminatedException, a:
		wasError = True
		logger.logError(NAME+ "Server zamknal polaczenie")
		errorMessage = "Serwer zamknal polaczenie"

	except Exception, e:
		wasError = True
		logger.logError(NAME+ "error - zamykanie polaczenia")
		logger.logError(NAME + e.message)
		errorMessage = "Wystapil nieznany problem"

	finally:
		if wasError:
			raise Exception(errorMessage)

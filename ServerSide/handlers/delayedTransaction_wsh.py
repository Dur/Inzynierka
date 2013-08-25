from mod_python import apache
from database.utils1 import TicketUtil
from utils.FileProcessors import FileProcessor
from Queue import Queue
import utils.Logger as logger
import time
from utils.KillableListenThread import KillableListenThread

NAME = "delayedTransaction_wsh: "
SKIP = "SKIP"
ABORT = "ABORT"
OK = "OK"
LOCALHOST_NAME = "localhost"
EXPECTED_TICKET = "expectedTicket"
SKIP_TICKETS = "skipTickets"

def web_socket_do_extra_handshake(request):
	pass  # Always accept.

def web_socket_transfer_data(request):

	logger.logInfo(NAME+ "Server dostal zgloszenie")

	paramsDictionary = {}
	paramsDictionary["SOCKET"] = request.ws_stream
	paramsDictionary["HOME_PATH"] = request.get_options()["PROJECT_LOCATION"]
	paramsDictionary["CLIENT_ADDRESS"] = request.connection.remote_ip
	stopQueue = Queue()
	listenThread = KillableListenThread(request.ws_stream, stopQueue)

	ticket = request.ws_stream.receive_message()
	currentTicket = TicketUtil.readTempVars()[EXPECTED_TICKET]
	timeOut = (int(ticket) - int(currentTicket)) * 5
	start = time.time()
	while currentTicket < ticket and time.time() - start < timeOut:
		time.sleep(1)
		currentTicket = TicketUtil.readTempVars()[EXPECTED_TICKET]
	if currentTicket == ticket:
		request.ws_stream.send_message(OK)
		listenThread.start()
		if listenThread.getMessage(5) != OK:
			skip(paramsDictionary, ticket)
	else:
		request.ws_stream.send_message(ABORT)
		skip(paramsDictionary, ticket)
	stopQueue.put("STOP")
	return apache.HTTP_OK

def skip(paramsDictionary, ticket):
	tempProcessor = FileProcessor(paramsDictionary["HOME_PATH"] + "ServerSide/config/tempParams.conf")
	tempProcessor.lockFile()
	params = tempProcessor.readFile()
	currentTicket = params[EXPECTED_TICKET]
	if int(currentTicket) == int(ticket):
		params[EXPECTED_TICKET] = str(int(ticket) + 1)
	else:
		toSkip = params[SKIP_TICKETS]
		toRet = ""
		if(toSkip != None and len(toSkip) != 0):
			for single in toSkip.split(","):
				if int(single)>int(currentTicket):
					toRet= toRet + single + ","
		toRet = toRet + str(ticket)
		params[SKIP_TICKETS] = toRet
	tempProcessor.writeToFile(params)
	tempProcessor.unlockFile()
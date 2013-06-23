from connections.Connection import Connection
from utils.FileProcessors import FileProcessor

__author__ = 'dur'
TICKET_PARAM = "ticketServer"
SKIP_TICKETS = "skipTickets"
EXPECTED_TICKET = "expectedTicket"

def getTicket():
	connection = Connection("/home/dur/Projects/ServerSide/config/connection_config.conf")
	params = readTempVars()
	connection.connect(params[TICKET_PARAM], 80, "/ticket")
	return connection.get_message()

def readTempVars():
	tempProcessor = FileProcessor("/home/dur/Projects/ServerSide/config/tempParams.conf")
	tempProcessor.lockFile()
	params = tempProcessor.readFile()
	tempProcessor.unlockFile()
	return params

def setNextExpectedTicket(currentTicket):
	tempProcessor = FileProcessor("/home/dur/Projects/ServerSide/config/tempParams.conf")
	tempProcessor.lockFile()
	params = tempProcessor.readFile()
	skipped = params[SKIP_TICKETS].split(",")
	newTicket = int(currentTicket) + 1
	while skipped.__contains__(str(newTicket)):
		skipped.remove(str(newTicket))
		newTicket = int(newTicket) + 1
	toRet = ""
	for single in skipped:
		toRet= toRet + str(single) + ","
	toRet = toRet[:-1]
	print(skipped)
	params[EXPECTED_TICKET] = str(newTicket)
	params[SKIP_TICKETS] = toRet
	tempProcessor.writeToFile(params)
	tempProcessor.unlockFile()
	return newTicket

def skipTicket(ticket):
	tempProcessor = FileProcessor("/home/dur/Projects/ServerSide/config/tempParams.conf")
	tempProcessor.lockFile()
	params = tempProcessor.readFile()
	currentTicket = params[EXPECTED_TICKET]
	if int(currentTicket) == int(ticket):
		params[EXPECTED_TICKET] = setNextExpectedTicket()
	else:
		toSkip = params[SKIP_TICKETS]
		toRet = ""
		if(toSkip != None and len(toSkip) != 0):
			array = toSkip.split(",")
			array.append(ticket)
			for single in sortStringsByIntValue(array):
				toRet= toRet + str(single) + ","
			toRet = toRet[:-1]
		else:
			toRet = toRet + str(ticket)
		params[SKIP_TICKETS] = toRet
	tempProcessor.writeToFile(params)
	tempProcessor.unlockFile()

def sortStringsByIntValue(stringArray):
	value = []
	for a in stringArray:
		value.append(int(a))
	return sorted(value)

def getCurrentExpectedTicket():
	params = readTempVars()
	return params[EXPECTED_TICKET]
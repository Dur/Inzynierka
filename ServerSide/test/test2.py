
# TICKET_PARAM = "ticketServer"
#


#logger.logImportant("nowy log")
# tempProcessor = FileProcessor("/home/dur/Projects/ServerSide/config/tempParams.conf")
# tempProcessor.lockFile()
# params = tempProcessor.readFile()
# tempProcessor.unlockFile()

#import utils.Logger as logger
# tempProcessor = FileProcessor("/home/dur/Projects/ServerSide/config/tempParams.conf")
# tempProcessor.lockFile()
# params = tempProcessor.readFile()
# print(params)
# tempProcessor.unlockFile()
#logger.logError("Error message")
from database.utils1 import TicketUtil

TicketUtil.setNextExpectedTicket(1)



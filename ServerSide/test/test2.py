from connections.Connection import Connection
from utils.FileProcessors import FileProcessor

# TICKET_PARAM = "ticketServer"
#
# connection = Connection("/home/dur/Projects/ServerSide/config/connection_config.conf")
# tempProcessor = FileProcessor("/home/dur/Projects/ServerSide/config/tempParams.conf")
# tempProcessor.lockFile()
# params = tempProcessor.readFile()
# tempProcessor.unlockFile()
# connection.connect(params[TICKET_PARAM], 80, "/ticket")
# print(connection.get_message())

tempProcessor = FileProcessor("/home/dur/Projects/ServerSide/config/tempParams.conf")
tempProcessor.lockFile()
params = tempProcessor.readFile()
print(params)
tempProcessor.unlockFile()
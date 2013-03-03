from connections.AppRunner import AppRunner
from database.utils.DatabaseConnector import DatabaseConnector
from utils.FileProcessor import FileProcessor

file = FileProcessor("/home/dur/Projects/ServerSide/config/addresses.conf")
file.lockFile()
addresses = file.readFile()
for key in addresses:
	addresses[key] = 'F'
file.writeToFile(addresses)
file.unlockFile()
runner = AppRunner("/home/dur/Projects/ServerSide/config/startConfig.conf")
runner.connect()

#db = DatabaseConnector("root", "root", "distributed", "localhost")
#db.initConnection()
#print db.executeSQL("select * from datastore")
#db.closeConnection()
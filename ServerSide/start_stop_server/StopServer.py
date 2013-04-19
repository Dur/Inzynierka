from utils.FileProcessors import FileProcessor

__author__ = 'dur'

file = FileProcessor("/home/dur/Projects/ServerSide/config/addresses.conf")
file.lockFile()
addresses = file.readFile()
for key in addresses:
	addresses[key] = 'F'
file.writeToFile(addresses)
file.unlockFile()

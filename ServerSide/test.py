#__author__ = 'dur'
#from FileProcessor import FileProcessor
#import time
#
#org={"aaa":'T', "bbb":'T', "ccc":'T', "ddd":'F',"eee":'T',"fff":'F', "ggg":'F', "hhh":'F'}
#new={"aaa":'T', "bbb":'F', "ccc":'T', "ddd":'T',"eee":'F',"fff":'T', "ggg":'F', "hhh":'F'}
#processor = FileProcessor("/home/dur/Pulpit/aa.txt")
#processor.mergeFile(org, new)
#processor.writeToFile(org)
from threading import Thread


__author__ = 'dur'
from ListenSocket import ListenSocket

from FileProcessor import FileProcessor
from PingConnection import PingConnection
import time
#
#file = FileProcessor("/home/dur/Projects/ServerSide/addresses.conf")
#file.lockFile()
#addresses = file.readFile()
#for key in addresses:
#	addresses[key] = 'T'
#file.writeToFile(addresses)
#file.unlockFile()
#new = {}
#connection = PingConnection("/home/dur/Projects/ServerSide/ping_config.conf")
#while True:
#	file.lockFile()
#	org = file.readFile()
#	for key in org:
#		if( connection.connect(key,80) != -1 ):
#			connection.send("Ping")
#			print connection.get_message()
#			new[key] = 'T'
#		else:
#			new[key] = 'F'
#	file.mergeFile(org, new)
#	file.unlockFile()
#	time.sleep(4)

class testThread(Thread):

	def run(self):
		time.sleep(5)
		print "raising"
		raise Exception("pyk pyk")
		return


try:

	thread = testThread()
	thread.start()
	while(True):
		time.sleep(2)
except Exception, a:
	print a.message
	exit

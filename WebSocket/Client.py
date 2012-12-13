import codecs
import time
from Connection import Connection
import sys

TIME_OUT = 6

class Client(object):

	def __init__(self):
		self

	def ballRolling(self):
		print 'ball rolling'
		print sys.path
		con = Connection()
		con.connect()
		con.send('Read')
		to_end = 0
		while to_end < TIME_OUT:
			message = con.get_message()
			if message != None:
				print "Got %s" %message
			time.sleep(0.5)
			to_end += 0.5
		print "end of waiting"
		return

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
cl = Client()
cl.ballRolling()
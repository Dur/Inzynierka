import codecs
import time
from Connection import Connection
import sys
from TestSender import TestSender

TIME_OUT = 6

class Client(object):

	def __init__(self):
		self

	def ballRolling(self):
		print 'ball rolling'
		print sys.path
		con = Connection()
		con.connect()
		test = TestSender(con)
		test.start()
		while True:
			message = con.get_message()
			print "Got %s" %message
		return

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
cl = Client()
cl.ballRolling()
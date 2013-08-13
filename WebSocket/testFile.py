#!/usr/bin/env python
from threading import Thread
import time

class MyThread(Thread):

	def __init__(self, name, object):
		Thread.__init__(self)
		self.name = name
		print object

	def run(self):
		print("{} started!".format(self.name))              # "Thread-x started!"
		time.sleep(1)                                      # Pretend to work for a second
		print("{} finished!".format(self.name))             # "Thread-x finishsed!"

if __name__ == '__main__':
	for x in range(4):                                     # Four times...
		mythread = MyThread("shakalaka", "boom")
		mythread.start()                                   # ...Start the thread
		time.sleep(.9)
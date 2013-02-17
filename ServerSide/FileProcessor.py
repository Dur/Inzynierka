__author__ = 'dur'
from filelock import FileLock

class FileProcessor:

	fileName = ""
	lock = None

	def __init__(self, file):
		self.fileName = file
		self.lock = FileLock(self.fileName, 10)

	def readFile(self):
		pairs={}
		with open(self.fileName, 'r') as f:
			for singleLine in f:
				singleLine = singleLine.replace('\n','')
				splitedLine = singleLine.split(':')
				pairs[splitedLine[0]] = splitedLine[1]
		return pairs

	def writeToFile(self, pairs):
		with open(self.fileName, 'w') as f:
			for key in pairs:
				line = key + ":" + pairs[key]+'\n'
				f.write(line)
		return

	def lockFile(self):
		self.lock.acquire()

	def unlockFile(self):
		self.lock.release()

__author__ = 'dur'
from utils.filelock import FileLock
NAME = "FileProcessor: "
#import utils.Logger as logger
class FileProcessor:

	fileName = ""
	lock = None

	def __init__(self, file):
		try:
			self.fileName = file
			self.lock = FileLock(self.fileName, 10)
		except Exception, e:
			#logger.logError(NAME + e.message)
			raise Exception(e.message)


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
		if self.lock.is_locked == False:
			raise Exception(NAME + "Nie moge zalozyc blokady na plik")

	def unlockFile(self):
		if self.lock.is_locked:
			self.lock.release()

	def __del__(self):
		if self.lock.is_locked:
			self.lock.release()

	def readFirstLine(self):
		with open(self.fileName, 'r') as f:
			for singleLine in f:
				return singleLine

	def writeSingleLine(self, line):
		with open(self.fileName, 'w') as f:
				f.write(line)
		return

	def appendToFile(self, line):
		with open(self.fileName, 'a') as f:
			f.write(line)
		return


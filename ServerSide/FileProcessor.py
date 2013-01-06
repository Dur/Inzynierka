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
				splitedLine = singleLine.split(';')
				pairs[splitedLine[0]] = splitedLine[1]
		return pairs

	def writeToFile(self, pairs):
		with open(self.fileName, 'w') as f:
			for key in pairs:
				line = key + ";" + pairs[key]+'\n'
				f.write(line)
		return

	def lockFile(self):
		self.lock.acquire()

	def unlockFile(self):
		self.lock.release()


# Merges file. params are two doctionaries
#org={"aaa":'T', "bbb":'T', "ccc":'T', "ddd":'F',"eee":'T',"fff":'F', "ggg":'F', "hhh":'F'}
#new={"aaa":'T', "bbb":'F', "ccc":'T', "ddd":'T',"eee":'F',"fff":'T', "ggg":'F', "hhh":'F'}
#processor = FileProcessor("/home/dur/Pulpit/aa.txt")
#processor.mergeFile(org, new)

	def mergeFile(self, org, new):
		curr={}
		with open(self.fileName, 'r') as f:
			for singleLine in f:
				singleLine = singleLine.replace('\n','')
				splitedLine = singleLine.split(';')
				curr[splitedLine[0]] = splitedLine[1]
		with open(self.fileName, 'w') as f:
			for key in new:
				if curr[key] != new[key]:
					if  org[key] != curr[key]:
						new[key] = curr[key]
				line = key + ";" + new[key]+'\n'
				f.write(line)
		return
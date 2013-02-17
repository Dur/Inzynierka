__author__ = 'dur'

class ConfigurationReader:

	def __init__(self, filePath):
		self.path = filePath

	def readConfigFile(self):
		dictionary=dict()
		with open(self.path, 'r') as f:
			for singleLine in f:
				if not singleLine.startswith("#") and not singleLine.startswith('\n'):
					singleLine = singleLine.replace('\n','')
					splitedLine = singleLine.split('=')
					dictionary[splitedLine[0]] = splitedLine[1]
		return dictionary
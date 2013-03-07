from importlib import import_module

__author__ = 'dur'
class ModulesLoader:

	def loadModules(self, filePath):
		self.modules={}
		with open(filePath, 'r') as f:
			for singleLine in f:
				if( singleLine == '\n' or singleLine.startswith("#")):
					continue
				singleLine = singleLine.replace('\n','')
				splitedLine = singleLine.split(':')
				if splitedLine[0] in self.modules:
					self.modules[splitedLine[0]].append(import_module('UserConf.ExtendedModules.'+splitedLine[1]))
				else:
					self.modules[splitedLine[0]]=[import_module('UserConf.ExtendedModules.'+splitedLine[1])]
		return self.modules
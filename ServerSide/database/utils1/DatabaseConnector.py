from database.ReadTransaction import ReadTransaction

__author__ = 'dur'

import MySQLdb
import logging

# tabela to datastore
#baza danych distributed

OK = 0
ERROR = -1

SELECT_OPERATION = "SELECT"
ERROR_MESSAGE = "Sorry but database is not consistent, please try again later"
OK_MESSAGE = "Command executed successfully"


NAME = "DatabaseConnector: "

class DatabaseConnector:

	login = ""
	password = ""
	databaseName = ""
	host = ""
	cursor = None
	connection = None

	def __init__(self, login, password, databaseName, host):
		self.login = login
		self.password = password
		self.databaseName = databaseName
		self.host = host

	def initConnection(self):
		try:
			logging.error("Trying to connect with credentials: " + self.host + " " + self.login + " " + self.password + " " + self.databaseName)
			self.connection = MySQLdb.connect(self.host, self.login, self.password, self.databaseName)
			self.cursor = self.connection.cursor()
			self.readTransaction = None
			self.writeTransaction = None
			return OK

		except Exception, e:
			logging.error(NAME + "Unable to connect to database " + e.message )
			return ERROR

	def executeSQL(self, command, paramsDictionary):
		try:
			splitedLine = command.split(' ')
			operation = splitedLine[0]
			if operation.upper() != SELECT_OPERATION:
				logging.error(NAME + "Client executes write operation" )
				self.cursor.execute(command)
				return OK_MESSAGE
			else:
				logging.error(NAME + "Client executes read operation" )
				if self.readTransaction == None:
					self.readTransaction = ReadTransaction(paramsDictionary)
				if self.readTransaction.checkDataVersions() == True:
					self.cursor.execute(command)
					return self.cursor.fetchall()
				else:
					return ERROR_MESSAGE
		except MySQLdb.Error, e:
			logging.error(NAME + "%d %s" % (e.args[0], e.args[1]))
			return "%d %s" % (e.args[0], e.args[1])
		except Exception, e:
			logging.error(NAME + "Exception while executing SQL command " + e.message )
			return ERROR

	def closeConnection(self):
		if self.connection != None:
			self.connection.close()
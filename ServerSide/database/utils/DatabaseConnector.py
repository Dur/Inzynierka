from database.utils.ReadTransaction import ReadTransaction

__author__ = 'dur'

import MySQLdb
import logging

# tabela to datastore

OK = 0
ERROR = -1

INSERT_OPERATION = "INSERT"
UPDATE_OPERATION = "UPDATE"
DELETE_OPERATION = "DELETE"
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
		self.writeOperations = {}
		self.writeOperations[DELETE_OPERATION] = DELETE_OPERATION
		self.writeOperations[UPDATE_OPERATION] = UPDATE_OPERATION
		self.writeOperations[INSERT_OPERATION] = INSERT_OPERATION

	def initConnection(self):
		try:
			logging.error("Trying to connect with credentials: " + self.host + " " + self.login + " " + self.password + " " + self.databaseName)
			self.connection = MySQLdb.connect(self.host, self.login, self.password, self.databaseName)
			self.cursor = self.connection.cursor()
			return OK

		except Exception, e:
			logging.error(NAME + "Unable to connect to database " + e.message )
			return ERROR

	def executeSQL(self, command, paramsDictionary):
		try:
			splitedLine = command.split(' ')
			operation = splitedLine[0]
			if operation.upper() in self.writeOperations:
				logging.error(NAME + "Client executes write operation" )
				self.cursor.execute(command)
				return OK_MESSAGE
			else:
				logging.error(NAME + "Client executes read operation" )
				transaction = ReadTransaction(paramsDictionary)
				if transaction.checkDataVersions() == True:
					self.cursor.execute(command)
					return self.cursor.fetchall()
				else:
					return ERROR_MESSAGE

		except Exception, e:
			logging.error(NAME + "Exception while executing SQL command " + e.message )
			return ERROR

	def closeConnection(self):
		if self.connection != None:
			self.connection.close()
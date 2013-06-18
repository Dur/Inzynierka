from database.ReadTransaction import ReadTransaction
from database.WriteTransaction import WriteTransaction

__author__ = 'dur'

import MySQLdb
import logging
import utils.Logger as logger
# tabela to datastore
#baza danych distributed

OK = 0
ERROR = -1

SELECT_OPERATION = "SELECT"
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
			logging.info(NAME + "Proba nawiazania polaczenia dla: " + self.host + " " + self.login + " " + self.password + " " + self.databaseName)
			self.connection = MySQLdb.connect(self.host, self.login, self.password, self.databaseName)
			self.cursor = self.connection.cursor()
			self.readTransaction = None
			self.writeTransaction = None
			logging.info(NAME + "Polaczenie z baza danych nawiazane")
			return OK

		except Exception, e:
			logger.logImportant(NAME + "Nie mozna polaczyc sie z baza danych " + e.message )
			return ERROR

	def executeSQL(self, command, paramsDictionary):
		try:
			splitedLine = command.split(' ')
			operation = splitedLine[0]

			if operation.upper() != SELECT_OPERATION:
				logger.logImportant(NAME + "Klient wykonuje transakcje zapisu" )
				if self.writeTransaction == None:
					self.writeTransaction = WriteTransaction(paramsDictionary)
				return self.writeTransaction.executeTransaction(self.cursor, command)
			else:
				logger.logImportant(NAME + "Klient wykonuje transakcje odczytu" )
				if self.readTransaction == None:
					self.readTransaction = ReadTransaction(paramsDictionary)
				return self.readTransaction.executeTransaction(self.cursor, command)

		except Exception, e:
			logger.logImportant(NAME + "Error w trakcie wykonywania zapytania SQL " + e.message )
			return ERROR

	def executeQueryWithoutTransaction(self, command):
		try:
			self.cursor.execute(command)
			return OK
		except MySQLdb.Error, e:
			self.cursor.execute("rollback")
			logger.logImportant(NAME + "%d %s" % (e.args[0], e.args[1]))
			return "%d %s" % (e.args[0], e.args[1])
		except Exception, e:
			logger.logImportant(NAME + e.message)

	def closeConnection(self):
		if self.connection != None:
			self.connection.close()
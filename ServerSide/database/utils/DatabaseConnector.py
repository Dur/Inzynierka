__author__ = 'dur'

import MySQLdb
import logging

# tabela to datastore

OK = 0
ERROR = -1

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
			return OK

		except Exception, e:
			logging.error(NAME + "Unable to connect to database " + e.message )
			return ERROR

	def executeSQL(self, command):
		try:
			self.cursor.execute(command)
			return self.cursor.fetchall()

		except Exception, e:
			logging.error(NAME + "Exception while executing SQL command " + e.message )
			return ERROR

	def closeConnection(self):
		if self.connection != None:
			self.connection.close()
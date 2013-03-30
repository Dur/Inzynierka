import MySQLdb
from Queue import Queue
from connections.Connection import Connection

#connection = Connection("/home/dur/Projects/ServerSide/config/database_config/transaction_config.conf")
#connection.connect("192.168.56.102", 80)
from database.utils1.DatabaseConnector import DatabaseConnector

#command = "insert into datastore values(3,'test',3)"
#
#aa = "ababa"
#print aa.replace('a', 'c')
#command = command.replace('\'', '\\\'')
#sql = "INSERT INTO " +  "versions" + " VALUES(" + str("1") + ",\'" + command + "\')"
#
#print sql
#
#try:
#	connection = MySQLdb.connect("localhost", "root", "root", "distributed")
#	cursor = connection.cursor()
#	cursor.execute(sql)
#	cursor.execute("commit")
#except MySQLdb.Error, e:
#	print("%d %s" % (e.args[0], e.args[1]))
#except Exception, ee:
#	print ee.message

aa = "22:33:44:66:"
pp = aa.split(":")
for single in pp:
	if single != "":
		print single + " ll"
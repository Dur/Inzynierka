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
# db = MySQLdb.connect("localhost", "root", "root", "distributed")
# cursor = db.cursor()
# cursor.execute("select * from versions where id > " + str(0) + " order by id")
# for version, command in cursor.fetchall():
# 	print version
# 	print command

# import os
#
# os.chdir("/home/dur/Projects")
# os.chdir("..")
# os.chdir("Pulpit")
# filelist = [ f for f in os.listdir(".") if f.endswith(".lock") ]
# for f in filelist:
# 	os.remove(f)

import glob, os

os.chdir("/home/dur/Pulpit")
filelist = glob.glob("*.lock")
for f in filelist:
	os.remove(f)
from Queue import Queue
from connections.Connection import Connection

connection = Connection("/home/dur/Projects/ServerSide/config/database_config/transaction_config.conf")
connection.connect("192.168.56.102", 80)
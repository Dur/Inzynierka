from connections.Connection import Connection

__author__ = 'dur'

conn = Connection("/home/dur/Projects/ServerSide/config/config.conf")
conn.connect("localhost", 80)
conn.send_message("hello")
print conn.get_message()
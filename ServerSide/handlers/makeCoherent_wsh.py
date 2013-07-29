import MySQLdb
import utils.Logger as logger
from mod_python import apache
from utils.ConfigurationReader import ConfigurationReader
from utils.filelock import FileLock

NAME = "makeCoherent_wsh: "
ERROR = -1
END = "END"
LOCK_ERROR = "LOCK_ERROR"

def web_socket_do_extra_handshake(request):
	pass  # Always accept.


def web_socket_transfer_data(request):

	logger.logInfo(NAME+ "Server dostal zgloszenie")

	paramsDictionary = {}
	socket = request.ws_stream
	paramsDictionary["HOME_PATH"] = request.get_options()["PROJECT_LOCATION"]

	configReader = ConfigurationReader(paramsDictionary["HOME_PATH"]+"ServerSide/config/database_config/database.conf")
	dbParamsDict = configReader.readConfigFile()

	login = dbParamsDict["DEFAULT_LOGIN"]
	password = dbParamsDict["DEFAULT_PASSWORD"]

	clientVersion = socket.receive_message()
	logger.logInfo(NAME + "client version " + clientVersion)
	lockFilePath = paramsDictionary["HOME_PATH"]+"ServerSide/config/database_config/dbLock.dat"
	lock = FileLock(lockFilePath,3,.05)
	try:
		lock.acquire()
	except Exception, e:
		logger.logError(NAME + e.message)
		socket.send_message(LOCK_ERROR)
		return apache.HTTP_OK
	try:
		db = MySQLdb.connect(dbParamsDict["HOST"], login, password, dbParamsDict["DATABASE"])
		cursor = db.cursor()
		logger.logInfo(NAME + "polaczenie z baza nawiazane")
		cursor.execute("select * from versions where id > " + str(clientVersion) + " order by id")
		logger.logInfo(NAME + "komenda wyslana do bazy")
		for version, command in cursor.fetchall():
			socket.send_message(str(version))
			socket.send_message(command)
			logger.logInfo(NAME + "Wyslano " + str(version) + " " + command)
		socket.send_message(END)
		logger.logInfo(NAME + "wyslano wiadomosc konczaca")
		return apache.HTTP_OK
	except MySQLdb.Error, e:
		logger.logError("%d %s" % (e.args[0], e.args[1]))
		if lock.is_locked:
			lock.release()
		return apache.HTTP_OK
	except Exception, ee:
		logger.logError(NAME + ee.message)
		if lock.is_locked:
			lock.release()
		return apache.HTTP_OK






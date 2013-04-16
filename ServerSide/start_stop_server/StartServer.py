from connections.AppRunner import AppRunner

path = "/home/dur/Projects/"

runner = AppRunner(path + "ServerSide/config/startConfig.conf")
runner.connect()
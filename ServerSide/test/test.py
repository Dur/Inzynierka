from connections.AppRunner import AppRunner
import os
from subprocess import call

path = "/home/dur/Projects/"

os.chdir(path+"ServerSide/config")
call(['rm', '-f', '-r', '*.lock'])
os.chdir("pass")
call(['rm', '-f', '-r', '*.lock'])
os.chdir("..")
os.chdir("database_config")
call(['rm', '-f', '-r', '*.lock'])
runner = AppRunner(path + "ServerSide/config/startConfig.conf")
runner.connect()
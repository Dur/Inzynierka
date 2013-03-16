from utils.FileProcessor import FileProcessor
import logging
import math

__author__ = 'dur'

NAME = "WriteTransaction: "
LOCALHOST_NAME = "localhost"
PREPARE = "PREPARE"
GLOBAL_COMMIT = "GLOBAL_COMMIT"
ABORT = "ABORT"
GLOBAL_ABORT = "GLOBAL_ABORT"
OK = "OK"

class WriteTransaction:

	paramsDoctionary = {}

__author__ = 'dur'
from FileProcessor import FileProcessor
import time

org={"aaa":'T', "bbb":'T', "ccc":'T', "ddd":'F',"eee":'T',"fff":'F', "ggg":'F', "hhh":'F'}
new={"aaa":'T', "bbb":'F', "ccc":'T', "ddd":'T',"eee":'F',"fff":'T', "ggg":'F', "hhh":'F'}
processor = FileProcessor("/home/dur/Pulpit/aa.txt")
processor.mergeFile(org, new)
#processor.writeToFile(org)
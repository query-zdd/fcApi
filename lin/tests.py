import hashlib
import sys
from sys import argv
input_name = hashlib.md5()
str = "admin@123"
input_name.update(str.encode("utf-8"))
print(input_name.hexdigest())
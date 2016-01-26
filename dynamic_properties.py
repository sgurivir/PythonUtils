import os
import json
import re


class Point(object):
    def __init__(self):
	pass

a = Point()
[a.x, a.y, a.z] = re.findall(r"[-+]?\d*\.*\d+", "Total: 40645 success: 34830 failure: 5815")

print a.x
print a.y

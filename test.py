import os
import json

class Point(object):
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

def idoalot(*vertices):
	for i in range(0, len(vertices)-1):
		print vertices[i], vertices[i+1]

def covert_tuples_to_points(tuples):
    points = []
    for tuple in tuples:
        (x, y) = tuple
        points.append(Point(x,y))

    return points

def convert_list_of_points_to_str(points):
   print str(points)

def multiple_lists_to_method(header_map, parameter_map):
   for k in header_map:
	print "header_map: " + k + ":" + header_map.get(k)

   for k in parameter_map:
	print "parameter_map: " + k + ":" + parameter_map.get(k)

def json_parse(message):
   response_json = json.loads(message)
   print response_json["status"]
   if response_json["status"] == "OK":
	print "ok"
		
#idoalot((2,3), (4,5), (6,7), (8,9))

#print  [(1,2) , (3,4) , (5,6)]
#print covert_tuples_to_points([(1,2) , (3,4) , (5,6)])
#convert_list_of_points_to_str([(1,2) , (3,4) , (5,6)])

#multiple_lists_to_method({'a': 'b', 'c':'d'},
#			 {'e': 'f', 'g':'h'})

#print os.path.expanduser("~/")

print json_parse('{"rid":"d1b40690-51cd-11e5-97ce-a590f1ae83e4","status":"OK"}')

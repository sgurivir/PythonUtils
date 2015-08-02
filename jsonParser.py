import sys
import json


def getJson(i, j):
    return json.dumps({
        'dingdongBell': False,
        'A': {
            'B': True,
            'C': True,
            'D': False
        },
        'E': {
            'openMode': i,
            'serverId': j,
            'DDD': False,
            'EEE': "xyz",
            'YYY': "abc",
        }
    })

'''Json Parser'''
class JsonUtil:
  @staticmethod
  def parse(message):
    print message
    env=json.loads(message)
    print env['A']['B']

  @staticmethod
  def encode(i,j, file_name):
      with open(file_name, "w") as f:
          f.write(getJson(i,j))
          f.flush()

def main():
  JsonUtil.parse(getJson(2,3))
  JsonUtil.encode(5,6, "/tmp/x.json")

main()

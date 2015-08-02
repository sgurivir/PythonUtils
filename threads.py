import sys
import threading

from time import sleep
from threading import Thread, Lock

total = 0
lock = threading.Lock()

'''Producer'''
class Producer(Thread):
  def __init__(self, val):
    Thread.__init__(self)
    self.val = val
    self.name = 'Producer'

  def run(self):
    global total
    lock.acquire()
    print("In producer thread : " + str(self.val) )
    my_total = total
    sleep(0.1)
    total = my_total + self.val * 2
    lock.release()


'''Consumer'''
class Consumer(Thread):
  def __init__(self, val):
    Thread.__init__(self)
    self.name = 'Consumer'
    self.val = val

  def run(self):
    global total
    lock.acquire()
    print("In consumer thread : " + str(self.val) )
    my_total = total
    sleep(0.8)
    total = my_total - self.val
    lock.release()
          
def main():
  producers = []
  consumers = []

  for i in [1,2,3,4,5]:
    producers.append(Producer(i))
    consumers.append(Consumer(i))
  
  map(lambda x: x.start(), producers)
  map(lambda x: x.start(), consumers)
  
  map(lambda x: x.join(), producers)
  map(lambda x: x.join(), consumers)
  
  global total
  print "Sum of all numbers : " + str(total)
  
main()

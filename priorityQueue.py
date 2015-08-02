import Queue
import threading
import time
import random

exitFlag = 0
queueLock = threading.Lock()
queue = Queue.Queue(120)
NUM_WORKERS = 10
workers = []

class Worker(threading.Thread) :
  def __init__(self, thread_id):
    threading.Thread.__init__(self)
    self.thread_id = thread_id
    
  def run(self):
    while not exitFlag:
      queueLock.acquire()
      
      if queue.empty():
        queueLock.release()
        return
        
      data = queue.get()
      queueLock.release()
      
      if data:
        print "processing data : " + str(data)
      #time.sleep(random.randint(1,3))
      
print "Adding elements to queue"
for i in range(1,100):
  queue.put(i)

print "Creating workers"
for i in range(1 , NUM_WORKERS):
  worker = Worker(i)
  workers.append( worker )
  worker.start()

print "Waiting for queue to drain"
while not queue.empty():
  pass

exitFlag = 1

for worker in workers:
  worker.join()
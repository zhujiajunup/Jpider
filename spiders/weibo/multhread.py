from collections import deque
import queue
import threading
from time import sleep
q = queue.Queue()
result = deque()
num_worker_threads = 10
threads = []
def do_work(n):
    return n+2

def workder():
    while True:
        item = q.get()
        if item is None:
            print('break')
            break
        print(do_work(item))
        q.task_done()
        sleep(10)
        q.put(12)

def worker1():
    while True:
        print(1)
        sleep(10)

def worker2():
    while True:
        print(2)

t1 = threading.Thread(target=worker1)
t2 = threading.Thread(target=worker2)
t1.start()
t2.start()

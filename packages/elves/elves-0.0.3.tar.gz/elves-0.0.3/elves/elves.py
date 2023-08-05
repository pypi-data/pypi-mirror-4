'''
elves -- Python Threading For Human
'''
import threading
import Queue
from functools import partial

last_elves = None

class Elf(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            job = self.queue.get()
            job()
            self.queue.task_done()

class Elves():
    def __init__(self, num):
        self.num = num
        self.queue = Queue.Queue()
        self.threads = []

    def run(self):
        for i in range(self.num):
            self.threads.append(Elf(self.queue))
            self.threads[-1].setDaemon(True)
            self.threads[-1].start()

    def put(self, func, *args, **kwargs):
        self.queue.put(partial(func, *args, **kwargs))

    def join(self):
        self.queue.join()


def run(num, func=None, *args, **kwargs):
    global last_elves
    elves = Elves(num)
    elves.run()
    last_elves = elves
    if func is not None:
        for i in range(num):
            elves.put(func, *args, **kwargs)
    return last_elves

def put(func, *args, **kwargs):
    last_elves.put(func, *args, **kwargs)

def join():
    last_elves.join()

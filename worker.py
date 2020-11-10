#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor
import threading

# TODO save message queue before exit
# TODO switch to adhoc executor to handle exceptions better
class Queue:

  def __init__(self, size):
    self.size = size
    self.queue = []

    self.executor = ThreadPoolExecutor(max_workers = size)

  def push(self, fn, *args, **kwargs):
    self.queue.append([fn, args, kwargs])
    self.executor.submit(fn, *args, **kwargs)

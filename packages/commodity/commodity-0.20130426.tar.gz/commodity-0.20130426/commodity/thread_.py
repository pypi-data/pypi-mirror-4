# -*- coding:utf-8; tab-width:4; mode:python -*-

import os
import time
import select
from threading import Thread
import Queue
import logging

from .type_ import checked_type

all = ['ReaderThread',
       'ThreadFunc',
       'start_new_thread',
       'SimpleThreadPool']


def ReaderThread(fin, fout):
    if fout is None:
        return DummyReaderThread()

    return ActualReaderThread(fin, fout)


class DummyReaderThread(object):
    def flush(self):
        pass


class ActualReaderThread(Thread):
    class Timeout(Exception):
        pass

    def __init__(self, fdin, fdout):
        super(ActualReaderThread, self).__init__()
        self.fdin = fdin
        self.fdout = fdout
        assert not fdout.closed, fdout
        self.start()
        time.sleep(0.01)

    def _read_in(self):
        ready = select.select([self.fdin], [], [], 0.2)[0]
        if not ready:
            raise self.Timeout

        return os.read(self.fdin.fileno(), 2048)

    def run(self):
        while 1:
            try:
                data = self._read_in()
                if not data:
                    break

                self.fdout.write(data)

            except self.Timeout:
                continue

    def flush(self):
        Thread.join(self, 2)
        # print self, self.isAlive()
        self.fdout.write(self.fdin.read())
        self.fdout.flush()


class ThreadFunc(Thread):
    """
    Execute given function in a new thread. It provides return value (or exception) as
    object atribbutes.
    """

    def __init__(self, target, *args, **kargs):
        self.target = target
        self.args = args
        self.kargs = kargs
        super(ThreadFunc, self).__init__()
        self.result = self.exception = None
        self.start()
        time.sleep(0.01)

    def run(self):
        try:
            self.result = self.target(*self.args, **self.kargs)
        except Exception, e:
            self.exception = e


def start_new_thread(target, *args, **kargs):
    """Execute given function in a new thread. It returns a :class:`ThreadFunc` object.
    """
    return ThreadFunc(target, *args, **kargs)


class SimpleThreadPool:
    """A generic and simple thread pool. Function return value are received by means of
    callbacks.

    >>> pool = SimpleThreadPool(4)
    >>> pool.add(somefunc, (arg1, arg2), somecallback)
    >>> [...]
    >>> pool.join()

    Also implements a parallel :py:func:`map` for an argument sequence for a function executing each
    on a different thread:

    >>> pool = SimpleThreadPool(4)
    >>> pool.map(math.sqrt, ((2, 4, 5, 9))
    (1.4142135623730951, 2.0, 2.23606797749979, 3.0)

    >>> pool.map(math.pow, [(2, 2), (3, 2), (3, 4)])
    (4, 9, 81)
    """
    def __init__(self, numThreads):
        self.tasks = Queue.Queue()
        self.threads = [SimpleThreadPool.Worker(self.tasks) for x in range(numThreads)]

    def add(self, func, args=(), callback=lambda x: x):
        assert callable(func)
        self.tasks.put((func, args, callback))

    def map(self, func, *sequences):
        if len(sequences) == 1:
            it = zip(sequences[0])
        else:
            it = zip(*sequences)

        holders = []

        for args in it:
            holder = SimpleThreadPool.Holder()
            holders.append(holder)
            self.add(func, args, holder)

        self.join()

        return tuple(x.value for x in holders)

    def join(self):
        self.tasks.join()

    class Worker(Thread):
        def __init__(self, tasks):
            Thread.__init__(self)
            self.tasks = tasks
            self.daemon = True
            self.start()

        def run(self):
            while 1:
                self.run_next()

        def run_next(self):
            func, args, callback = self.tasks.get()

            logging.debug("thread %s taken %s", self, func)
            result = func(*args)
            self.tasks.task_done()

            callback(result)

    class Holder:
        def __init__(self):
            self.value = None

        def __call__(self, arg):
            self.value = arg

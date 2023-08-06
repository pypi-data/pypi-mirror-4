#!/usr/bin/env python

import argparse
import threading
import multiprocessing

class ThreadMap(object):
    """
    """
    
    def __init__(self, thread_num=multiprocessing.cpu_count()):
        """
        
        Arguments:
        - `thread_num`:
        """
        self._thread_num = thread_num
        self._lock = threading.Lock()

    def _worker(self):
        """
        
        Arguments:
        - `self`:
        """

        self._lock.acquire()

        while self._count < len(self._arglist):
            current = self._count
            self._count += 1
            self._lock.release()
            self._results[current] = self._func(self._arglist[current])
            self._lock.acquire()
        self._lock.release()

    def map(self, func, arglist):
        """
        
        Arguments:
        - `self`:
        - `func`:
        - `arglist`:
        """

        self._arglist = arglist
        self._func = func
        self._count = 0
        self._results = [None]*len(arglist)

        self._threads = list()
        for i in xrange(self._thread_num):
            self._threads.append(threading.Thread(target=self._worker))
            self._threads[-1].start()
            
        for i in self._threads:
            i.join()

        return self._results

def _main():
    import time
    parser = argparse.ArgumentParser(description="Multi-thread map example")
    options = parser.parse_args()

    def testfunc(a):
        print 'start', a
        time.sleep(1)
        print 'finish', a
        return a*2

    threadmap = ThreadMap()
    results = threadmap.map(testfunc, range(100))
    print results
    
    pass
    
    
if __name__ == '__main__':
        _main()
        

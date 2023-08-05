import time
from threading import Thread, Event
from Queue import Queue, Empty, Full
import warnings

from multiprocessing import Process as Thread
from multiprocessing import Queue, Event

from IPython import embed


class PylabPlot(Thread):
    def __init__(self, timeout=60, block=False, maxsize=1, _debug=False):
        r"""
        Parameters
        ----------
        timeout : float
           Kill the thread if no activity for this many seconds.
        block : bool, float
           If `False`, the do not block the computation thread on update -- if
           the queue is full, then force it to drop the oldest item.  If
           `None`, then block the computation thread untill plotting gets up to
           date, otherwise, block for this many seconds before forcing the data
           onto queue (dropping the oldest).
        maxsize : int
           Maximum number of items to cache in the queue.
        """
        from matplotlib import pyplot as plt
        self.plt = plt
        self._debug = _debug
        if self._debug:
            print "Initializing thread"
        self.timeout = timeout
        if block is True:
            block = None
        self.block = block
        self.queue = Queue(maxsize=maxsize)
        self.event = Event()
        Thread.__init__(self)
        self.dead = False
        self.running = False
        self.start()

    def stop(self):
        self.running = False
        self.event.set()

    def update_no_wait(self, *v, **kw):
        if self.dead:
            warnings.warn("Plot thread is dead... ignoring update command.")
            return
        if self._debug:
            print "Updateing Queue without waiting."
        try:
            self.queue.put((v, kw), block=False)
        except Full:
            # Remove an item, then put this one.
            try:     # draw might be called in the meantine...
                self.queue.get(block=False)
            except Empty:
                pass
            self.queue.put((v, kw), block=False)  # This should not fail
        self.event.set()

    def update(self, *v, **kw):
        if self.dead:
            warnings.warn("Plot thread is dead... ignoring update command.")
            return
        if self._debug:
            print "Updateing Queue"

        if self.block is False:
            self.update_no_wait(*v, **kw)
        else:
            try:
                self.queue.put((v, kw), block=True, timeout=self.block)
                self.event.set()
            except Full:
                # Don't raise an error in main thread
                self.update_no_wait(*v, **kw)
        
    def run(self):
        self.plt.clf()
        self.running = True
        if self._debug:
            print "Starting thread"
        while self.running:
            self.event.wait(timeout=self.timeout)
            self.event.clear()
            if self.queue.empty():
                self.running = False
                if self._debug:
                    print "Timout reached..."
            else:
                while not self.queue.empty():
                    try:
                        v, kw = self.queue.get(block=False)
                    except Empty:
                        pass
                    if self._debug:
                        print "Drawing..."
                    self.draw(*v, **kw)
                    if self._debug:
                        print "Done drawing!"

        if self._debug:
            print "Finishing thread"
        self.dead = True


def go():
    import numpy as np
    from mmf import mdb

    class Plot(PylabPlot):
        def draw(self, x, y):
            self.plt.ioff()
            self.plt.clf()
            self.plt.plot(x, y)
            print y
            self.plt.ion()
            self.plt.draw()
            time.sleep(0.5)     # Pretend this is slow

    mdb()
    p = Plot(block=True, _debug=True)
    
    raw_input("Position plot window, and press enter to run...")
    x = np.linspace(0, 2*np.pi, 10)
    dt = 0.001
    t = 0
    for n in xrange(100000):
        t += dt
        y = np.sin(x - t)
        p.update(x=x, y=y)

if __name__ == "__main__":
    go()

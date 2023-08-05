r"""Example computation Client."""
import cPickle
import socket
import time

import threading
from Queue import Queue


_CLIENTCOMMAND = """
import cPickle
import asyncplot.client
Plotter = cPickle.loads(%(Plotter)s)
c = asyncplot.client.Client(Plotter=Plotter, host=%(host)s, port=%(port)i)
c.run()
"""


class Client(object):

    client_command = _CLIENTCOMMAND

    def __init__(self, Plotter, host=None, port=None):
        import server           # Do this here to prevent recursive dependence
        if host is None:
            host = server.PlotSocketServer._HOST
        if port is None:
            port = server.PlotSocketServer._PORT
        self.host = host
        self.port = port
        self.plot = Plotter()
        self._BUF_SIZE = 2**12

    def get_data(self):
        tic = time.time()
        sock = self.connect()
        datasz = -1
        data = []
        while datasz != 0:
            data.append(sock.recv(self._BUF_SIZE))
            datasz = len(data[-1])
            #print "tmpdata from Server is %i bytes long." % (datasz,)

        #print "close client socket and shutdown. "
        sock.close()
        #sock.shutdown(1)

        res = ''.join(data)
        print("Getting data %g" % (time.time() - tic,))
        return res

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #print "Trying to connect to port %i..." % (self.port,)
        sock.connect((self.host, self.port))
        #print "Connected to port %i." % (self.port,)
        return sock
        
    def run(self):
        try:
            self.is_alive = True
            while self.is_alive:
                data = self.get_data()            
                tic = time.time()
                v, kw = cPickle.loads(data)
                print("Loading pickle %g" % (time.time() - tic,))
                tic = time.time()
                self.plot.draw(*v, **kw)
                print("Plotting %g" % (time.time() - tic,))
        finally:
            self.is_alive = False


class ThreadedClient(Client):
    r"""This version acquires the data from the server in a separate thread
    which queues the data for the plotter.
    """
    _YEAR = 60*60*24*365
    def __init__(self, Plotter, host=None, port=None, queue_size=1):
        Client.__init__(self, Plotter=Plotter, host=host, port=port)
        self.queue = Queue(maxsize=queue_size)

    def data_thread(self):
        while self.is_alive:
            try:
                data = cPickle.loads(self.get_data())
                print "Queue put..."
                self.queue.put(data, block=True)
                print "Queue put. Done."
            except:
                # Should add a message here indicating a potential problem in
                # connecting to the server, and a timeout.  This presently
                # allows for the server to disconnect while keeping the client
                # running, or starting the client before the server.
                pass

    def run(self):
        data_thread = threading.Thread(target=self.data_thread)
        self.is_alive = True
        data_thread.start()
        try:
            while self.is_alive:
                tic = time.time()
                print "Queue get..."

                # We add a long timeout here so that this can be interrupted
                # with Ctrl-C.  See
                # http://bugs.python.org/issue1360
                v, kw = self.queue.get(block=True, timeout=self._YEAR)
                print "Queue get. Done."
                self.plot.draw(*v, **kw)
                print("Plotting %g" % (time.time() - tic,))
        finally:
            self.is_alive = False
            
            # Empty the queue to make sure that the data thread does not block
            # because of a full queue
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                except:
                    pass
            print "Joining data_thread..."
            data_thread.join()
            print "Joining data_thread. Done."


def run_client_example():
    #create the Client instance and pass the Plot object, then call
    #run().
    class Plot(object):
        def __init__(self):
            from matplotlib import pyplot as plt
            self.plt = plt

        def draw(self, x, y):
            plt = self.plt
            plt.ioff()
            plt.clf()
            plt.plot(x, y)
            #print y
            plt.ion()
            plt.draw()
            #time.sleep(0.5)     # Pretend this is slow

    c = Client(Plot=Plot)
    #raw_input('adjust plot and press return')
    c.run()


if __name__ == "__main__":
    run_client_example()

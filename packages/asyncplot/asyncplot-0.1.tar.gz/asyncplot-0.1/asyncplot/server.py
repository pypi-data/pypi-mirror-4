r"""Threaded Socket Server"""

import cPickle
import socket
import subprocess
import threading
import SocketServer
import client

import mmf


class PlotRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        self.request.sendall(self.server._get_data())
        #self.request.shutdown(socket.SHUT_RDWR)
        #self.request.close()


class PlotSocketServer(SocketServer.ThreadingMixIn,
                       SocketServer.TCPServer):
    r"""Simple threaded socket server.  Listens on the specified port, and
    launches Socket threads on connection.

    Call :meth:`update` to update the plot data.

    To Do
    -----
    * Add timeouts.
    """
    _PORT = 9999
    _HOST = ''

    def __init__(self, host=_HOST, port=_PORT):
        self.lock = threading.Lock()  # RLock()??
        self.have_data = threading.Event()
        self.data = None
        self.daemon_threads = True       # Don't keep python alive.
        self.allow_reuse_address = True  # Allow port reuse after termination.
        SocketServer.TCPServer.__init__(self, (host, port),
                                        PlotRequestHandler)

    def _get_data(self, block=True):
        r"""The object is pickled here."""
        self.have_data.wait()
        with self.lock:
            return cPickle.dumps(self.data)

    def update(self, *v, **kw):
        with self.lock:
            self.data = (v, kw)
        self.have_data.set()    # This is very slow!


class Server(threading.Thread):
    r"""If you pass `spawn_client_command`, then a plot client will be spawned
    in a subprocess.
    """
    def __init__(self,
                 Plotter=None,
                 host=PlotSocketServer._HOST,
                 port=PlotSocketServer._PORT,
                 client_cmd=["ipython", "--pylab", "-c"],
                 wait_for_client=False):
        r"""
        Parameters
        ----------
        Plotter : class
           If provided, then this class will be used to draw the plot.  It
           should define a constructor `__init__` and a method `draw()`. The
           constructor should open a plot window(s) so that the used can
           position the(m) before starting the calculation.  This class must be
           picklable (i.e. it must be defined at a top-level of an importable
           module) , and will be called in a separate process.
        wait_for_client : Bool
           If `True`, then pause server to allow the user to adjust plot
           windows.
        """
        self.Plotter = Plotter
        self.client_cmd = client_cmd
        self.wait_for_client = wait_for_client
        self.server = PlotSocketServer(host=host, port=port)
        threading.Thread.__init__(self, target=self.server.serve_forever)
        self.daemon = True               # Don't keep python alive.

    def _start_client(self):
        client_process = None
        if self.Plotter is not None:
            host, port = self.server.server_address
            client_code = client.Client.client_command % dict(
                Plotter=repr(cPickle.dumps(self.Plotter)),
                host=repr(host),
                port=port)
            client_cmd = self.client_cmd + [client_code]
            client_process = subprocess.Popen(client_cmd,
                                                   # I/O??????
                                                   )
            return client_process
        
    def __enter__(self):
        self.start()
        self.client_process = self._start_client()
        if self.wait_for_client:
            raw_input("Adjust plot windows and press return to continue...")

        return self.server

    def __exit__(self, type, value, traceback):
        self.server.shutdown()      # This does not close the socket
        if self.client_process is not None:
            self.client_process.terminate()
        self.server.server_close()  # This actually closes the socket
        return value is None


class PlotClient(object):
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


def example_server():
    import time
    import numpy as np
    x = np.linspace(0, 2*np.pi, 100)
    t = 0
    dt = 0.01
    tic = time.time()
    # Ideal code:
    #with Server(client=PlotClient, wait_for_client=True) as s:
    with Server(client_cmd=['ipython', '--pylab=osx', 'client.py'],
                wait_for_client=True) as s:
        for n in xrange(1000000):
            if n % 100000 == 0:
                print n, time.time() - tic
                tic = time.time()
            t += dt
            y = np.sin(x + t)
            s.update(x, y)

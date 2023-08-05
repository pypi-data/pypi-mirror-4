r"""Server that uses threading."""

__all__ = ['Plot', 'Client', 'Server']

import time
from threading import Thread
import socket
import cPickle

class Plot(object):
    def __init__(self):
        from matplotlib import pyplot as plt
        self.plt = plt

    def draw(self, *v, **kw):
        r"""Overload this to effect the actual drawing.  All arguments must be
        pickelable.  This will be called on the client"""
        raise NotImplementedError

    def update(self, *v, **kw):
        r"""Call this with the same arguments required by the overloaded draw
        method.  This will be called on the server."""
        raise NotImplementedError


class Server(Plot, Thread):
    def __init__(self, host='', port=9999):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        print "Server listening on port %i" % (port, )
        self.args = None

        Thread.__init__(self)
        Plot.__init__(self)

    def run(self):
        print "Waiting for connection..."
        self.sock.listen(1)
        conn, addr = self.sock.accept()
        print "Connected by %s" % (str(addr), )

        while True:
            data = conn.recv(1024)
            print "Got request %s" % (data, )
            if data.startswith('get'):
                while self.args is None:
                    # wait for data... should use an Event
                    time.sleep(0.1)
                conn.sendall(cPickle.dumps(self.args))
                self.args = None
                print "Send plot data"
            elif not data or data.startswith("quit"):
                print "Received 'quit' message from Client"
                break

        print "close client connection"
        conn.close()
        print "Done"

    def update(self, *v, **kw):
        self.args = (v, kw)


class Client(object):
    def __init__(self, Plot, host='localhost', port=9999):
        self.host = host
        self.port = port
        self.plot = Plot()
        self.plot.plt.clf()

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "Trying to connect to port %i..." % (self.port,)
        sock.connect((self.host, self.port))
        print "Connected to port %i." % (self.port,)
        BUF_SIZE = 4096
        while True:
            try:
                sock.send('get')
                data = sock.recv(BUF_SIZE)
                print "data from Server is %i bytes long." % (len(data),)
                v, kw = cPickle.loads(data)
                self.plot.draw(*v, **kw)
            except KeyboardInterrupt:
                sock.send('quit')
                print "Sent 'quit' to Server."
                break
        print "close client socket and shutdown. "
        sock.close()
        sock.shutdown(1)


if __name__ == '__main__':
    s = Server()
    s.start()

.. -*- rst -*- -*- restructuredtext -*-

.. This file should be written using the restructure text
.. conventions.  It will be displayed on the bitbucket source page and
.. serves as the documentation of the directory.



Async Plotter
=============

Simple two-process client/server plotting with the following features:

* Plotting does not slow down calculations.
* User maintains control of the calculation (i.e. KeyboardInterrupts work).
* Auto-launch client from the server.

  * The user defines the plotting code in a (picklable) class, and
    provides the class to the Server() constructor.  The Server passes the pickled Plotter
    to the client when the client process is launched in a new python interpreter. 
    The python interpreter command line options for the client are passed to the Server 
    constructor at the time of instantiation. Default values are: 
    (ex. ["ipython", "--pylab=osx", "-c"])


To Do
=====

Prototype for asynchronous plotting with separate processes using sockets

Still Needs:

* Comprehensive testing
* Logging (print debug messages in debug mode for checking network problems)
* Profile performance.
* Configuration (hostname, port specification etc.)

I think that these have been dealt with, but they need testing:

* socket buffer overflow (recv)
* cleanup thread and socket command line termination
* error handling. ex. when a client disconnects then server listen continues,
  network errors
* multiple clients (plotting)


Other Design Approaches
=======================

Threading Solution
==================
The simplest approach is a multi-thread approach.  In principle, one can run the
computations in the main thread and plotting in a separate thread.  This
solution is sketched in ``thread.py`` but fails with most matplotlib_ backends
due to their requirement of running in the main thread.  A quick work-around is
to run the computation in a secondary thread, but this precludes the user being
able to interrupt the computation.

A nice feature of the python GIL is that one can be fairly confident about
sharing data (a careful solution would require locks etc.)

Multiprocessing Solution
========================
This same solution should work with multiprocessing_, but this fails on my
development platform (Mac OS X 10.5) with the following error::

   The process has forked and you cannot use this CoreFoundation  
   functionality safely. You MUST exec().
   Break on  
   __THE_PROCESS_HAS_FORKED_AND_YOU_CANNOT_USE_THIS_COREFOUNDATION_FUNCTIONALITY___YOU_MUST_EXEC__() to debug.

Separate Processes
==================
It seems that the most robust solution is to have the calculation and plotters
run in completely separate processes.  This has an added benefit:

* User can plot remotely.

One issue that needs to be addressed here (and in the multiprocessing_ solution)
is the copying of data.  One common use-case is that the plotter may be slower
than the computation.  Thus, intermediate data may be discarded and should not
be sent across the network.


Additional Approaches
=====================
It seems that one should be able to use IPython_ to do this, but I have not
found a simple way to do this yet.

.. _matplotlib: http://matplotlib.org/
.. _IPython: http://ipython.org/
.. _multiprocessing: http://docs.python.org/2/library/multiprocessing.html

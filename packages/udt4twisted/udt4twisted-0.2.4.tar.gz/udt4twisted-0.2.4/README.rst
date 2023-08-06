=========
 Summary
=========

This package provides integration of udt as a transport protocol in twisted.
It works by replacing the default epoll reactor with a modified one. Also, it
provides top-level api(taken mostly from tcp.py) for listening and
connecting to udt transports.

=======
 Usage
=======

#) Basically use it like you will use TCP in twisted, but all sockets
   will be in SOCK_DGRAM mode only. Also :code:`write()` has ttl and
   inorder options.

#) Check examples/

#) When using twistd or trial, put: -r udtepoll

===============
 Prerequisites
===============


#) PyUDT
#) twisted


=======
 Notes
=======

#) Tests from twisted pass only in internet/ and protocol/,
   for the others they just seem to "hang" (something to do
   with flags, probably)

#) More options related purely to udt should be included.(e.g. controlling
   socket creation, buffers, timeouts)

#) UDT does not provide separate error events, instead these will be catched
   on an attempt read or write. This means that connectionLost will NOT be
   called as soon as the connection is lost for example.

#) It is highly recommended to use the latest revision at the udt-git repo
   https://sourceforge.net/p/udt/git/ (if it doesn't break
   compatibility with PyUDT).

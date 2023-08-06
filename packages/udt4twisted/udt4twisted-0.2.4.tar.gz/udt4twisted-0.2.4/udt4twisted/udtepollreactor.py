"""
An UDT::epoll() implementation.
For use with the UDT protocol.
"""
from __future__ import division, absolute_import
import errno
import sys
from zope.interface import implementer
from zope.interface import Interface, Attribute
from twisted.internet.interfaces import IReactorFDSet
from twisted.python import log
from twisted.internet import posixbase, base
from twisted.internet.epollreactor import EPollReactor, _ContinuousPolling
from twisted.internet import threads
from twisted.internet.main import CONNECTION_DONE, CONNECTION_LOST
import udt4
from udt4 import pyudt, accept, sendmsg, recvmsg, UDT_RCVDATE, UDTException
from udt4.pyudt import UdtSocket
from udt4twisted import udt
from udt4 import EASYNCRCV, ECONNLOST
import socket as s
import gc

class IReactorUDT(Interface):
    """
    UDT transport interface.
    """
    def listenUDT(port,
                  protocol,
                  interface='',
                  maxPacketSize=8192,
                  backlog=50):
        """
        Connects a given DatagramProtocol to the given numeric UDT port.

        @return: object which provides L{IListeningPort}.
        """

    def connectUDT(host,
                   port,
                   factory,
                   timeout,
                   bindAddress):
        """
        Connects a given ClientFactory to a remote host.

        @return: object which provides L{IListeningPort}.
        """

@implementer(IReactorFDSet)
class _UDTContinuousPolling(_ContinuousPolling):
    _POLL_DISCONNECTED = udt4.ECONNLOST
    _POLL_IN = udt4.UDT_EPOLL_IN
    _POLL_OUT = udt4.UDT_EPOLL_OUT


@implementer(IReactorFDSet, IReactorUDT)
class UDTEPollReactor(EPollReactor):
    _POLL_DISCONNECTED = udt4.ECONNLOST
    _POLL_IN = udt4.UDT_EPOLL_IN
    _POLL_OUT = udt4.UDT_EPOLL_OUT

    def __init__(self):
        """
        Initialize epoll object, udt library
        and adds event trigger to clean the latter after shutdown.
        """
        udt4.startup()
        self._poller = udt4.UDTepoll()
        self._reads = {}
        self._writes = {}
        self._selectables = {}
        self._udtsockets = {}
        self._continuousPolling = _UDTContinuousPolling(self)
        posixbase.PosixReactorBase.__init__(self)
        self.addSystemEventTrigger("after", "shutdown", udt4.cleanup)

    def _isUDT(self, xer):
        """
        Private method that, based on selectable instance, decides
        if something is an udt socket
        """
        if isinstance(xer, udt.Port) or isinstance(xer, udt.Connection):
            return True
        else:
            return False

    def _add(self, xer, primary, other, selectables, event, antievent):
        """
        Private method for adding a descriptor from the event loop.

        It takes care of adding it if  new or modifying it if already added
        for another state (read -> read/write for example).
        """
        if isinstance(xer, udt.Port):
            fd = xer.socket.UDTSOCKET.UDTSOCKET
        else:
            fd = xer.fileno()
        if fd not in primary:
            flags = event
            # epoll_ctl can raise all kinds of IOErrors, and every one
            # indicates a bug either in the reactor or application-code.
            # Let them all through so someone sees a traceback and fixes
            # something.  We'll do the same thing for every other call to
            # this method in this file.
            if fd in other:
                flags |= antievent
                #FIXME do nothing
                if self._isUDT(xer):
                    # self._poller.remove_usock(fd)
                    # self._poller.add_usock(fd, flags)
                    pass
                else:
                    self._poller.remove_ssock(fd)
                    self._poller.add_ssock(fd, flags)
                #self._poller.modify(fd, flags)
            else:
                if self._isUDT(xer):
                    self._poller.add_usock(fd, flags)
                else:
                    self._poller.add_ssock(fd, flags)
                log.msg("ADDING:{0} with flags:{1}".format(fd, flags))

            # Update our own tracking state *only* after the epoll call has
            # succeeded.  Otherwise we may get out of sync.
            selectables[fd] = xer
            primary[fd] = 1

    def addReader(self, reader):
        """
        Add a FileDescriptor for notification of data available to read.
        """
        try:
            self._add(reader, self._reads, self._writes, self._selectables,
                      self._POLL_IN, self._POLL_OUT)
        except IOError as e:
            if e.errno == errno.EPERM:
                # epoll(7) doesn't support certain file descriptors,
                # e.g. filesystem files, so for those we just poll
                # continuously:
                self._continuousPolling.addReader(reader)
            else:
                raise


    def addWriter(self, writer):
        """
        Add a FileDescriptor for notification of data available to write.
        """
        try:
            self._add(writer, self._writes, self._reads, self._selectables,
                      self._POLL_OUT, self._POLL_IN)
        except IOError as e:
            if e.errno == errno.EPERM:
                # epoll(7) doesn't support certain file descriptors,
                # e.g. filesystem files, so for those we just poll
                # continuously:
                self._continuousPolling.addWriter(writer)
            else:
                raise

    def removeReader(self, reader):
        """
        Remove a Selectable for notification of data available to read.
        """
        if self._continuousPolling.isReading(reader):
            self._continuousPolling.removeReader(reader)
            return
        self._remove(reader, self._reads, self._writes, self._selectables,
                     self._POLL_IN, self._POLL_OUT)


    def removeWriter(self, writer):
        """
        Remove a Selectable for notification of data available to write.
        """
        if self._continuousPolling.isWriting(writer):
            self._continuousPolling.removeWriter(writer)
            return
        self._remove(writer, self._writes, self._reads, self._selectables,
                      self._POLL_OUT, self._POLL_IN)

    def _remove(self, xer, primary, other, selectables, event, antievent):
        """
        Private method for removing a descriptor from the event loop.

        It does the inverse job of _add, and also add a check in case of the fd
        has gone away.
        """
        if isinstance(xer, udt.Port):
            fd = xer.socket.UDTSOCKET.UDTSOCKET
        else:
            fd = xer.fileno()
        if fd == -1:
            for fd, fdes in selectables.items():
                if xer is fdes:
                    break
            else:
                return
        if fd in primary:
            if fd in other:
                #FIXME for now remove and add again
                flags = antievent
                # See comment above modify call in _add.
                if self._isUDT(xer):
                    #FIXME this breaks when server socket stops listening
                    # self._poller.remove_usock(fd)
                    # self._poller.add_usock(fd, flags)
                    pass
                else:
                    self._poller.remove_ssock(fd)
                    self._poller.add_ssock(fd, flags)
                #self._poller.modify(fd, flags)
            else:
                flags = event
                if self._isUDT(xer):
                    del selectables[fd]
                else:
                    del selectables[fd]
                # See comment above _control call in _add.
                if self._isUDT(xer):
                    self._poller.remove_usock(fd, flags)
                else:
                    #FIXME Apparently flags are not parsed in this method
                    self._poller.remove_ssock(fd)
                log.msg("REMOVING:{0} with flags:{1}".format(fd, flags))
            del primary[fd]

    def _handleSystemSocketSet(self, set, event):
        _drdw = self._doReadOrWrite
        for fd in set:
            try:
                selectable = self._selectables[fd]
            except KeyError:
                pass
            else:
                log.callWithLogger(selectable, _drdw, selectable, fd,
                                   event)
    def _handleUDTSocketSet(self, set, event):
        _drdw = self._doReadOrWrite
        for fd in set:
            try:
                selectable = self._selectables[fd.UDTSOCKET]
            except KeyError:
                pass
            else:
                log.callWithLogger(selectable, _drdw, selectable, fd,
                                   event)

    tests = True
    sock = None

    def doPoll(self, timeout):
        """
        Poll the poller for new events.
        """

        if timeout is None:
            timeout = -1  # Wait indefinitely.

        try:
            #doesn't work with floats :/
            l = self._poller.wait(True, True, int(timeout*1000), True, True)
        except UDTException as ue:
            if ue[0] == 6003:
                return
        #handle system sockets
        sread, swrite = l[2:]
        #print sread, swrite
        self._handleSystemSocketSet(sread, self._POLL_IN)
        self._handleSystemSocketSet(swrite, self._POLL_OUT)

        #handle UDT sockets
        uread, uwrite = l[:2]
        #print uread, uwrite
        self._handleUDTSocketSet(uread, self._POLL_IN)
        self._handleUDTSocketSet(uwrite, self._POLL_OUT)

    def _doReadOrWrite(self, selectable, fd, event):
        """
        fd is available for read or write, do the work and raise errors if
        necessary.
        """
        why = None
        inRead = False
        if event & self._POLL_DISCONNECTED and not (event & self._POLL_IN):
            if fd in self._reads:
                inRead = True
                why = CONNECTION_DONE
            else:
                why = CONNECTION_LOST
        else:
            try:
                if selectable.fileno() == -1:
                    why = _NO_FILEDESC
                else:
                    if event & self._POLL_IN:
                        # Handle a read event.
                        why = selectable.doRead()
                        inRead = True
                    if not why and event & self._POLL_OUT:
                        # Handle a write event, as long as doRead didn't
                        # disconnect us.
                        why = selectable.doWrite()
                        inRead = False
                        # if self._isUDT(selectable):
                        #     gc.collect()

            except:
                # Any exception from application code gets logged and will
                # cause us to disconnect the selectable.
                why = sys.exc_info()[1]
                log.err()
        if why:
            self._disconnectSelectable(selectable, why, inRead)



    def listenUDT(self,
                  port,
                  protocol,
                  interface='',
                  maxPacketSize=8192,
                  backlog=50):

        p = udt.Port(port, protocol, interface,
                     maxPacketSize, self, backlog)
        p.startListening()
        return p

    def connectUDT(self,
                   host,
                   port,
                   protocol,
                   timeout=30,
                   bindAddress=None):

        c = udt.Connector(host, port, protocol, timeout, bindAddress, self)
        c.connect()
        return c



    doIteration = doPoll



def install():
    """
    Install the epoll() reactor.
    """
    p = UDTEPollReactor()
    from twisted.internet.main import installReactor
    installReactor(p)


__all__ = ["UDTEPollReactor", "install"]

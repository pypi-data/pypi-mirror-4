import sys
import time
import struct
import socket
from zope.interface import implementer
from twisted.internet.defer import inlineCallbacks, returnValue, deferredGenerator
from twisted.internet import fdesc
from twisted.python.compat import _PY3
from twisted.internet import base, defer, address, udp, tcp
from twisted.internet.task import deferLater
from twisted.python import log, failure, _reflectpy3 as reflect
from twisted.python._utilpy3 import unsignedID
from twisted.python.runtime import platformType
from twisted.internet import abstract, error, interfaces, main
import udt4 as udt
from   udt4 import pyudt
from udt4 import EASYNCRCV, ECONNLOST
from socket import AI_PASSIVE
from errno import EWOULDBLOCK, EINTR, EMSGSIZE, ECONNREFUSED, EAGAIN
from twisted.python.compat import lazyByteSlice
from collections import deque
import gc
_sockErrReadIgnore = [EAGAIN, EINTR, EWOULDBLOCK]
_sockErrReadRefuse = [ECONNREFUSED]

if _PY3:
    def _concatenate(bObj, offset, bArray):
        # Python 3 lacks the buffer() builtin and the other primitives don't
        # help in this case.  Just do the copy.  Perhaps later these buffers can
        # be joined and FileDescriptor can use writev().  Or perhaps bytearrays
        # would help.
        return bObj[offset:] + b"".join(bArray)
else:
    def _concatenate(bObj, offset, bArray):
        # Avoid one extra string copy by using a buffer to limit what we include
        # in the result.
        return buffer(bObj, offset) + b"".join(bArray)


@implementer(interfaces.ITCPTransport, interfaces.ISystemHandle)
class Connection(abstract.FileDescriptor, tcp._AbortingMixin):
    """
    Superclass of all socket-based FileDescriptors.

    This is an abstract superclass of all objects which represent a UDT socket.

    @ivar logstr: prefix used when logging events related to this connection.
    @type logstr: C{str}
    """
    messageBuffer = deque()
    def _closeSocket(self, orderly):
        try:
            self.socket.close()
        except UDTException as ue:
            pass

    def __init__(self, skt, protocol, reactor=None):
        abstract.FileDescriptor.__init__(self, reactor=reactor)
        self.socket = skt
        self.socket.setblocking(False)
        self.fileno = skt.fileno
        self.protocol = protocol

    def getHandle(self):
        """Return the socket for this connection."""
        return self.socket

    def doRead(self):
        """
        Calls self.protocol.dataReceived with all available data.
        This reads up to self.bufferSize bytes of data from its socket, then
        calls self.dataReceived(data) to process it.  If the connection is not
        lost through an error in the physical recvmsg(),
        this function will return the result of the dataReceived call.
        """
        try:
            data = udt.recvmsg(self.socket.UDTSOCKET, self.bufferSize)
        except udt.UDTException as ue:
            if ue[0] == EASYNCRCV:
                #restart socket
                ein = self.reactor._POLL_IN
                self.reactor._poller.remove_usock(self.socket.UDTSOCKET)
                self.reactor._poller.add_usock(self.socket.UDTSOCKET, ein)
                return
            else:
                return main.CONNECTION_LOST

        return self.protocol.dataReceived(data)


    def _dataReceived(self, data):
        if not data:
            return main.CONNECTION_DONE
        rval = self.protocol.dataReceived(data)
        if rval is not None:
            offender = self.protocol.dataReceived
            warningFormat = (
                'Returning a value other than None from %(fqpn)s is '
                'deprecated since %(version)s.')
            warningString = deprecate.getDeprecationWarningString(
                offender, versions.Version('Twisted', 11, 0, 0),
                format=warningFormat)
            deprecate.warnAboutFunction(offender, warningString)
        return rval


    def writeSomeData(self, data, ttl=-1, inorder=True):
        """
        Write given data to this UDT connection.
        For now it will send all the data in the buffer.
        """
        try:
            return udt.sendmsg(self.socket.UDTSOCKET,
                               data, len(data), ttl, inorder)
        except udt.UDTException as ue:
            if ue[0] == EASYNCRCV:
                return self.writeSomeData(data, ttl, inorder)
            elif ue[0] == ECONNLOST:
                return main.CONNECTION_LOST

    def write(self, data, ttl=-1, inorder=True):
        """Reliably write some data.

        The data is buffered until the underlying file descriptor is ready
        for writing. If there is more than C{self.bufferSize} data in the
        buffer and this descriptor has a registered streaming producer, its
        C{pauseProducing()} method will be called. Also options for ttl and
        inorder will be stored and passed to producer.
        """
        if isinstance(data, unicode): # no, really, I mean it
            raise TypeError("Data must not be unicode")
        if not self.connected or self._writeDisconnected:
            return
        if data:
            self.messageBuffer.append([data, ttl, inorder])
            #self._maybePauseProducer()
            #self.startWriting()
            #Really start writable event
            try:
                self.reactor._poller.add_usock(self.socket.UDTSOCKET,
                                               self.reactor._POLL_OUT)
            except udt.UDTException as ue:
                log.msg("Error while writing:{0}".format(ue))
                self.abortConnection()


    _messagesAtOnce = 1024

    def splitAndSend(self):
        """
        Split and send messages to the other side.
        """
        for i in xrange(self._messagesAtOnce):
            try:
                message, ttl, inorder = self.messageBuffer.popleft()
            except IndexError:
                break
            l = self.writeSomeData(message, ttl, inorder)
            if isinstance(l, Exception) or l < 0:
                return l
            #FIXME Producers are probably NOT working
            # If there is nothing left to send,
            if l == main.CONNECTION_LOST:
                self.loseConnection()
                return main.CONNECTION_LOST
            elif self.disconnecting:
                # But if I was previously asked to
                #let the connection die, do
                # so.
                return self._postLoseConnection()
            elif self._writeDisconnecting:
                # I was previously asked to half-close the connection.  We
                # set _writeDisconnected before calling handler, in case the
                # handler calls loseConnection(), which
                #will want to check for
                # this attribute.
                self._writeDisconnected = True
                result = self._closeWriteConnection()
                return result

        return None
        

    def doWrite(self):
        """
        Called when data can be written. It will send all messages recorded
        in the buffer in a non-blocking way.
        @return: C{None} on success, an exception or a negative integer on
            failure.

        @see: L{twisted.internet.interfaces.IWriteDescriptor.doWrite}.
        """

        # Send as much data as you can.
        if len(self.messageBuffer) == 0:
            return None
        result = self.splitAndSend()
        if len(self.messageBuffer) == 0:
            #self.stopWriting()
            #Really stop writable event
            self.reactor._poller.remove_usock(self.socket.UDTSOCKET)
            self.reactor._poller.add_usock(self.socket.UDTSOCKET,
                                           self.reactor._POLL_IN)
        return result


    def _closeWriteConnection(self):
        try:
            getattr(self.socket, self._socketShutdownMethod)(1)
        except socket.error:
            pass
        p = interfaces.IHalfCloseableProtocol(self.protocol, None)
        if p:
            try:
                p.writeConnectionLost()
            except:
                f = failure.Failure()
                log.err()
                self.connectionLost(f)


    def readConnectionLost(self, reason):
        raise NotImplementedError()
        p = interfaces.IHalfCloseableProtocol(self.protocol, None)
        if p:
            try:
                p.readConnectionLost()
            except:
                log.err()
                self.connectionLost(failure.Failure())
        else:
            self.connectionLost(reason)



    def connectionLost(self, reason):
        """See abstract.FileDescriptor.connectionLost().
        """
        # Make sure we're not called twice, which can happen e.g. if
        # abortConnection() is called from protocol's dataReceived and then
        # code immediately after throws an exception that reaches the
        # reactor. We can't rely on "disconnected" attribute for this check
        # since twisted.internet._oldtls does evil things to it:
        if not hasattr(self, "socket"):
            return
        abstract.FileDescriptor.connectionLost(self, reason)
        self._closeSocket(not reason.check(error.ConnectionAborted))
        protocol = self.protocol
        del self.protocol
        del self.socket
        del self.fileno
        protocol.connectionLost(reason)


    logstr = "Uninitialized"

    def logPrefix(self):
        """Return the prefix to log with when I own the logging thread.
        """
        return self.logstr

class Server(Connection):
    """
    Serverside socket-stream connection class.

    This is a serverside network connection transport; a socket which came from
    an accept() on a server.
    """
    _base = Connection

    _addressType = address.IPv4Address

    def __init__(self, sock, protocol, client, server, sessionno, reactor):
        """
        Server(sock, protocol, client, server, sessionno)
        Initialize it with a socket, a protocol, a descriptor for my peer (a
        tuple of host, port describing the other end of the connection), an
        instance of Port, and a session number.
        """
        Connection.__init__(self, sock, protocol, reactor)
        self.server = server
        self.client = client
        self.sessionno = sessionno
        self.hostname = client[0]

        logPrefix = self._getLogPrefix(self.protocol)
        self.logstr = "%s,%s,%s" % (logPrefix,
                                    sessionno,
                                    self.hostname)
        if self.server is not None:
            self.repstr = "<%s #%s on %s>" % (self.protocol.__class__.__name__,
                                              self.sessionno,
                                              self.server._realPortNumber)
        self.startReading()
        self.connected = 1

    def __repr__(self):
        """
        A string representation of this connection.
        """
        return self.repstr


    @classmethod
    def _fromConnectedSocket(cls, fileDescriptor, addressFamily, factory,
                             reactor):
        """
        Create a new L{Server} based on an existing connected I{SOCK_STREAM}
        socket.

        Arguments are the same as to L{Server.__init__}, except where noted.

        @param fileDescriptor: An integer file descriptor associated with a
            connected socket.  The socket must be in non-blocking mode.  Any
            additional attributes desired, such as I{FD_CLOEXEC}, must also be
            set already.

        @param addressFamily: The address family (sometimes called I{domain})
            of the existing socket.  For example, L{socket.AF_INET}.

        @return: A new instance of C{cls} wrapping the socket given by
            C{fileDescriptor}.
        """
        raise NotImplementedError()
        addressType = address.IPv4Address
        if addressFamily == socket.AF_INET6:
            addressType = address.IPv6Address
        skt = socket.fromfd(fileDescriptor, addressFamily, socket.SOCK_STREAM)
        addr = skt.getpeername()
        protocolAddr = addressType('TCP', addr[0], addr[1])
        localPort = skt.getsockname()[1]

        protocol = factory.buildProtocol(protocolAddr)
        if protocol is None:
            skt.close()
            return

        self = cls(skt, protocol, addr, None, addr[1], reactor)
        self.repstr = "<%s #%s on %s>" % (
            self.protocol.__class__.__name__, self.sessionno, localPort)
        protocol.makeConnection(self)
        return self


    def getHost(self):
        """
        Returns an L{IPv4Address} or L{IPv6Address}.

        This indicates the server's address.
        """
        host, port = self.socket.getsockname()[:2]
        return self._addressType('UDP', host, port)


    def getPeer(self):
        """
        Returns an L{IPv4Address} or L{IPv6Address}.

        This indicates the client's address.
        """
        return self._addressType('UDP', *self.client[:2])

@implementer(interfaces.IListeningPort)
class Port(base.BasePort):
    """
    A UDT server port, listening for connections.

    When a connection is accepted, this will call a factory's buildProtocol
    with the incoming address as an argument, according to the specification
    described in L{twisted.internet.interfaces.IProtocolFactory}.

    If you wish to change the sort of transport that will be used, the
    C{transport} attribute will be called with the signature expected for
    C{Server.__init__}, so it can be replaced.

    @ivar deferred: a deferred created when L{stopListening} is called, and
        that will fire when connection is lost. This is not to be used it
        directly: prefer the deferred returned by L{stopListening} instead.
    @type deferred: L{defer.Deferred}

    @ivar disconnecting: flag indicating that the L{stopListening} method has
        been called and that no connections should be accepted anymore.
    @type disconnecting: C{bool}

    @ivar connected: flag set once the listen has successfully been called on
        the socket.
    @type connected: C{bool}

    @ivar _preexistingSocket: If not C{None}, a L{socket.socket} instance which
        was created and initialized outside of the reactor and will be used to
        listen for connections (instead of a new socket being created by this
        L{Port}).
    """

    socketType = socket.SOCK_DGRAM
    transport = Server

    sessionno = 0
    interface = ''
    backlog = 50

    _type = 'UDT'

    # Actual port number being listened on, only set to a non-None
    # value when we are actually listening.
    _realPortNumber = None

    # An externally initialized socket that we will use, rather than creating
    # our own.
    #TODO: this will not be supported soon
    _preexistingSocket = None

    addressFamily = socket.AF_INET
    _addressType = address.IPv4Address

    def __init__(self,
                 port,
                 factory,
                 interface='localhost',
                 maxPacketSize=8192,
                 reactor=None,
                 backlog=50,
                 ):
        """
        Initialize with a numeric port to listen on.
        """
        base.BasePort.__init__(self, reactor=reactor)
        self.port = port
        self.factory = factory
        self.backlog = backlog
        if interface == '':
            self.interface = "127.0.0.1"
        else:
            self.interface = socket.gethostbyname_ex(interface)[2][0]
        self._connectedAddr = None
        self.addresses = {}

    @classmethod
    def _fromListeningDescriptor(cls, reactor, fd, addressFamily, factory):
        """
        Create a new L{Port} based on an existing listening I{SOCK_DGRAM}
        socket.

        Arguments are the same as to L{Port.__init__}, except where noted.

        @param fd: An integer file descriptor associated with a listening
            socket.  The socket must be in non-blocking mode.  Any additional
            attributes desired, such as I{FD_CLOEXEC}, must also be set already.

        @param addressFamily: The address family (sometimes called I{domain}) of
            the existing socket.  For example, L{socket.AF_INET}.

        @return: A new instance of C{cls} wrapping the socket given by C{fd}.
        """
        port = socket.fromfd(fd, addressFamily, cls.socketType)
        interface = port.getsockname()[0]
        self = cls(None, factory, None, interface, reactor)
        self._preexistingSocket = port
        return self


    def __repr__(self):
        if self._realPortNumber is not None:
            return "<%s of %s on %s>" % (self.__class__,
                self.factory.__class__, self._realPortNumber)
        else:
            return "<%s of %s (not listening)>" % (self.__class__, self.factory.__class__)

    def createInternetSocket(self):
        s = pyudt.UdtSocket(self.addressFamily,
                            self.socketType,
                            AI_PASSIVE)
        s.setblocking(False)
        return s

    def _bindSocket(self):
        """
        Bind socket to an address.
        """
        try:
            skt = self.createInternetSocket()
            skt.bind((self.interface, self.port))
        except socket.error as le:
            raise error.CannotListenError(self.interface, self.port, le)

        # Make sure that if we listened on port 0, we update that to
        # reflect what the OS actually assigned us.
        self._realPortNumber = skt.getsockname()[1]
        self.connected = 1
        self.socket = skt
        self.fileno = skt.fileno


    def startListening(self):
        """Create and bind my socket, and begin listening on it.

        This is called on unserialization, and must be called after creating a
        server to begin listening on the specified port.
        """


        if self._preexistingSocket is None:
            # Create a new socket and make it listen
            self._bindSocket()
            #udp.Port.startListening(self)
            self.socket.listen(self.backlog)
        else:
            raise NotImplementedError()
        # Make sure that if we listened on port 0, we update that to
        # reflect what the OS actually assigned us.

        log.msg("%s starting on %s" % (
                self._getLogPrefix(self.factory), self._realPortNumber))

        # The order of the next 5 lines is kind of bizarre.  If no one
        # can explain it, perhaps we should re-arrange them.
        self.factory.doStart()
        self.numberAccepts = 100
        self.startReading()


    def _buildAddr(self, address):
        host, port = address[:2]
        return self._addressType('UDP', host, port)


    def doRead(self):
        """Called when my socket is ready for reading.
        This accepts a connection and calls self.protocol() to handle the
        wire-level protocol.
        """
        try:
            if platformType == "posix":
                numAccepts = self.numberAccepts
            else:
                # win32 event loop breaks if we do more than one accept()
                # in an iteration of the event loop.
                numAccepts = 1
            for i in range(numAccepts):
                # we need this so we can deal with a factory's buildProtocol
                # calling our loseConnection
                if self.disconnecting:
                    return
                try:
                    skt, addr = self.socket.accept()
                    log.msg("ACCEPT FD:{0} ADDR:{1}".format(skt,
                                                            addr))
                except udt.UDTException as (enum, message):
                    if enum == EASYNCRCV:
                        self.numberAccepts = i
                        break
                    else:
                        log.msg("Could not accept new connections!")
                        break
                    raise
                #FIXME
                #fdesc._setCloseOnExec(skt.fileno())
                protocol = self.factory.buildProtocol(self._buildAddr(addr))
                if protocol is None:
                    skt.close()
                    continue
                s = self.sessionno
                self.sessionno = s+1
                transport = self.transport(skt,
                                           protocol,
                                           addr, self, s, self.reactor)
                protocol.makeConnection(transport)
            else:
                self.numberAccepts = self.numberAccepts+20
        except:
            # Note that in TLS mode, this will possibly catch SSL.Errors
            # raised by self.socket.accept()
            #
            # There is no "except SSL.Error:" above because SSL may be
            # None if there is no SSL support.  In any case, all the
            # "except SSL.Error:" suite would probably do is log.deferr()
            # and return, so handling it here works just as well.
            log.deferr()

    def loseConnection(self, connDone=failure.Failure(main.CONNECTION_DONE)):
        """
        Stop accepting connections on this port.

        This will shut down the socket and call self.connectionLost().  It
        returns a deferred which will fire successfully when the port is
        actually closed, or with a failure if an error occurs shutting down.
        """
        self.disconnecting = True
        self.stopReading()
        if self.connected:
            self.deferred = deferLater(
                self.reactor, 0, self.connectionLost, connDone)
            return self.deferred

    stopListening = loseConnection

    def _logConnectionLostMsg(self):
        """
        Log message for closing port
        """
        log.msg('(%s Port %s Closed)' % (self._type, self._realPortNumber))


    def connectionLost(self, reason):
        """
        Cleans up the socket.
        """
        self._logConnectionLostMsg()
        self._realPortNumber = None

        base.BasePort.connectionLost(self, reason)
        self.connected = False
        self.socket.close()
        del self.socket
        del self.fileno

        try:
            self.factory.doStop()
        finally:
            self.disconnecting = False


    def logPrefix(self):
        """Returns the name of my class, to prefix log entries with.
        """
        return reflect.qual(self.factory.__class__)


    def getHost(self):
        """
        Return an L{IPv4Address} or L{IPv6Address} indicating the listening
        address of this port.
        """
        host, port = self.socket.getsockname()[:2]
        return self._addressType('UDP', host, port)

class Client(Connection, tcp._BaseBaseClient):
    """
    A transport for a UDT protocol.
    Do not create these directly; use L{IReactorTCP.connectTCP}.
    """
    _addressType = address.IPv4Address
    _base = Connection
    _commonConnection = Connection
    addressFamily = socket.AF_INET
    socketType = socket.SOCK_DGRAM

    def _stopReadingAndWriting(self):
        """
        Implement the POSIX-ish (i.e.
        L{twisted.internet.interfaces.IReactorFDSet}) method of detaching this
        socket from the reactor for L{_BaseBaseClient}.
        """
        if hasattr(self, "reactor"):
            # this doesn't happen if we failed in __init__
            self.stopReading()
            self.stopWriting()

    def _collectSocketDetails(self):
        """
        Clean up references to the socket and its file descriptor.

        @see: L{_BaseBaseClient}
        """
        del self.socket, self.fileno



    def _finishInit(self, whenDone, skt, error, reactor):
        """
        Called by subclasses to continue to the stage of initialization where
        the socket connect attempt is made.

        @param whenDone: A 0-argument callable to invoke once the connection is
            set up.  This is C{None} if the connection could not be prepared
            due to a previous error.

        @param skt: The socket object to use to perform the connection.
        @type skt: C{socket._socketobject}

        @param error: The error to fail the connection with.

        @param reactor: The reactor to use for this client.
        @type reactor: L{twisted.internet.interfaces.IReactorTime}
        """
        if whenDone:
            self._commonConnection.__init__(self, skt, None, reactor)
            reactor.callLater(0, whenDone)
        else:
            reactor.callLater(0, self.failIfNotConnected, error)


    def createInternetSocket(self):
        s = pyudt.UdtSocket(self.addressFamily, self.socketType)
        s.setblocking(False)
        #FIXME
        #fdesc._setCloseOnExec(s.fileno())
        return s

    def getHost(self):
        """
        Returns an L{IPv4Address}.

        This indicates the address from which I am connecting.
        """
        return self._addressType('UDP', *self.socket.getsockname()[:2])


    def getPeer(self):
        """
        Returns an L{IPv4Address}.

        This indicates the address that I am connected to.
        """
        # an ipv6 realAddress has more than two elements, but the IPv6Address
        # constructor still only takes two.
        return self._addressType('UDP', *self.realAddress[:2])


    def __repr__(self):
        s = '<%s to %s at %x>' % (self.__class__, self.addr, unsignedID(self))
        return s

    def __init__(self, host, port, bindAddress, connector, reactor=None,
                 timeout=-1):
        # BaseClient.__init__ is invoked later
        self.connector = connector
        self.addr = (host, port)
        self.timeout = timeout
        self.reactor = reactor

        whenDone = self.resolveAddress
        err = None
        skt = None

        if abstract.isIPAddress(host):
            self._requiresResolution = False
        else:
            self._requiresResolution = True
        try:
            skt = self.createInternetSocket()
        except udt.UDTException as ue:
            err = error.ConnectBindError(ue[0], ue[1])
            whenDone = None
        if whenDone and bindAddress is not None:
            try:
                bindinfo = bindAddress
                skt.bind(bindinfo)
            except udt.UDTException as ue:
                err = error.ConnectBindError(ue[0], ue[1])
                whenDone = None
        self._finishInit(whenDone, skt, err, reactor)

    def doConnect(self):
        """
        Initiate the outgoing connection attempt.
        @note: Applications do not need to call this method; it will be invoked
            internally as part of L{IReactorTCP.connectTCP}.
        """
        self.doWrite = self.doConnect
        self.doRead = self.doConnect
        if not hasattr(self, "connector"):
            # this happens when connection failed but doConnect
            # was scheduled via a callLater in self._finishInit
            return

        status = self.socket.getsockopt(udt.UDT_STATE)
        if (status != udt.UDTSTATUS_CONNECTED) and \
                (status != udt.UDTSTATUS_INIT):
            # self.failIfNotConnected(error.getConnectError((
            #             status)))
            #FIXME works for now
            self.stopConnecting()
            return
        elif status == udt.UDTSTATUS_CONNECTED:
            #Check for errors
            #We're connected, finish the connection
            del self.doWrite
            del self.doRead
            # we first stop and then start, to reset
            #any references to the old doRead
            self.startReading()
            self._connectDone()
            return

        # doConnect gets called twice.  The first time we actually need to
        # start the connection attempt.  The second time we don't really
        # want to (SO_ERROR above will have taken care of any errors, and if
        # it reported none, the mere fact that doConnect was called again is
        # sufficient to indicate that the connection has succeeded), but it
        # is not /particularly/ detrimental to do so.  This should get
        # cleaned up some day, though.
        try:
            connectResult = self.socket.connect(self.realAddress)
        except udt.UDTException as ue:
            connectResult = ue[0]

        #TODO
        if connectResult:
            if connectResult in (EASYNCRCV,):
                #We're starting to connect to each other
                self.startReading()
                # self.startWriting()
                return
            else:
                self.failIfNotConnected(error.getConnectError((
                            connectResult, connectResult)))
                return
        else:
            #FIXME but it works for now
            opt = self.socket.getsockopt(udt.UDT_STATE)
            if opt == udt.UDTSTATUS_CONNECTING:
                #add monitoring to the reactor
                self.startReading()
                self.startWriting()
                self.reactor._poller.add_usock(self.socket.UDTSOCKET,
                                               self.reactor._POLL_OUT)
            elif opt == udt.UDTSTATUS_CONNECTED:
                #Check for errors
                #We're connected, finish the connection
                del self.doWrite
                del self.doRead
                # we first stop and then start, to reset
                #any references to the old doRead
                self.startReading()
                self._connectDone()
                return

    def _connectDone(self):
        """
        This is a hook for when a connection attempt has succeeded.

        Here, we build the protocol from the
        L{twisted.internet.protocol.ClientFactory} that was passed in, compute
        a log string, begin reading so as to send traffic to the newly built
        protocol, and finally hook up the protocol itself.
        """
        self.protocol = self.connector.buildProtocol(self.getPeer())
        self.connected = 1
        logPrefix = self._getLogPrefix(self.protocol)
        self.logstr = "%s,client" % logPrefix
        self.startReading()
        self.protocol.makeConnection(self)

    def doWrite(self):
        try:
            state = self.socket.getsockopt(udt.UDT_STATE)
        except udt.UDTException as ue:
            self.connected = False
            self.failIfNotConnected(ue)
        else:
            if (state == udt.UDTSTATUS_CONNECTED) and (self.connected == False):
                self._connectDone()
                self.stopReading()
                self.stopWriting()
                self.startReading()
                #self.startWriting()
                return
            Connection.doWrite(self)


class Connector(base.BaseConnector):
    """
    A L{Connector} provides of L{twisted.internet.interfaces.IConnector} for
    all POSIX-style reactors.

    @ivar _addressType: the type returned by L{Connector.getDestination}.
        Either L{IPv4Address} or L{IPv6Address}, depending on the type of
        address.
    @type _addressType: C{type}
    """
    _addressType = address.IPv4Address

    def __init__(self, host, port, factory, timeout, bindAddress, reactor=None):
        self.host, self.port = host, port
        self.bindAddress = bindAddress
        self.timeout = timeout
        base.BaseConnector.__init__(self, factory, timeout, reactor)


    def _makeTransport(self):
        """
        Create a L{Client} bound to this L{Connector}.

        @return: a new L{Client}
        @rtype: L{Client}
        """
        return Client(self.host, self.port,
                      self.bindAddress, self, self.reactor, self.timeout)


    def getDestination(self):
        """
        @see: L{twisted.internet.interfaces.IConnector.getDestination}.
        """
        return self._addressType('UDP', self.host, self.port)

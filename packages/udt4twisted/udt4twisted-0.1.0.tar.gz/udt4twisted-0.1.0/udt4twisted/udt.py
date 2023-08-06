import sys
import time
import struct
import socket
from zope.interface import implementer
from twisted.internet import fdesc
from twisted.internet import base, defer, address, udp, tcp
from twisted.python import log, failure
from twisted.internet import abstract, error, interfaces
import udt4 as udt
from   udt4 import pyudt
from udt4 import EASYNCRCV, ECONNLOST
from socket import AI_PASSIVE
from errno import EWOULDBLOCK, EINTR, EMSGSIZE, ECONNREFUSED, EAGAIN
import gc
_sockErrReadIgnore = [EAGAIN, EINTR, EWOULDBLOCK]
_sockErrReadRefuse = [ECONNREFUSED]

def find_key(dic, val):
    """
    From http://www.daniweb.com/software-development/python/ \
    code/217019/search-a-python-dictionary-both-ways
    return the key of dictionary dic given the value
    """
    return [k for k, v in dic.iteritems() if v == val][0]


@implementer(
    interfaces.IListeningPort, interfaces.IUDPTransport,
    interfaces.ISystemHandle)
class Port(udp.Port):
    """
    UDT port, listening for packets.
    """
    maxThroughput = 256 * 2048

    def __init__(self,
                 port,
                 proto,
                 interface='localhost',
                 maxPacketSize=8192,
                 reactor=None,
                 backlog=50,
                 ):
        """
        Initialize with a numeric port to listen on.
        """
        base.BasePort.__init__(self, reactor)
        self.port = port
        self.protocol = proto
        self.maxPacketSize = maxPacketSize
        if interface == '':
            self.interface = "127.0.0.1"
        else:
            self.interface = socket.gethostbyname_ex(interface)[2][0]
        self.setLogStr()
        self._connectedAddr = None
        self.backlog = backlog
        self.addresses = {}


    def getHandle(self):
        """
        Return a socket object.
        """
        return pyudt.UdtSocket

    def createInternetSocket(self):
        s = pyudt.UdtSocket(self.addressFamily,
                            self.socketType,
                            AI_PASSIVE)
        s.setblocking(False)
        #s.setsockopt(udt.
        #FIXME
        #fdesc._setCloseOnExec(s.UDTSOCKET.udtsocket)
        return s

    def _connectDone(self):
        self.connected = 1
        logPrefix = self._getLogPrefix(self.protocol)
        self.logstr = "%s,client" % logPrefix
        self.startReading()
        self.protocol.makeConnection(self)


    def connect(self, host, port):
        """
        Connect to a remote host.
        """
        if self._connectedAddr:
            raise RuntimeError("already connected, reconnecting is not currently supported")
        if not abstract.isIPAddress(host):
            raise ValueError("please pass only IP addresses, not domain names")
        self._connectedAddr = (host, port)
        self.doConnect()

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

        log.msg("%s starting on %s" % (
                self._getLogPrefix(self.protocol), self._realPortNumber))

        self.connected = 1
        self.socket = skt
        self.fileno = skt.fileno

    def startListening(self):
        """
        Create and bind my socket, and begin listening on it.

        This is called on unserialization, and must be called after creating a
        server to begin listening on the specified port.
        """
        udp.Port.startListening(self)
        self.socket.listen(self.backlog)


    def doRead(self, fd=None, addr=None):
        """
        Called when my socket is ready for reading.
        """
        try:
            #print "recv from:", fd, " size:", self.maxPacketSize
            data = udt.recvmsg(fd, self.maxPacketSize)
            if addr == None:
                addr = self.addresses[fd.UDTSOCKET][1]
        except udt.UDTException as ue:
            #print ue
            return ue
        except socket.error as se:
            pass
        else:
            #read += len(data)
            try:
                self.protocol.datagramReceived(data, addr)
            except:
                log.err()
    def write(self, datagram, addr=None, ttl=-1, inorder=True):
        """
        Write datagram to address.
        @type datagram: C{str}
        @param datagram: The datagram to be sent.

        @type addr: C{tuple} containing C{str} as first element and C{int} as
            second element, or C{None}
        @param addr: A tuple of (I{stringified dotted-quad IP address},
            I{integer port number}); can be C{None} in connected mode.
        """
        if not self._connectedAddr:
            assert addr != None
            if not addr[0].replace(".", "").isdigit() and addr[0] != "<broadcast>":
                warnings.warn("Please only pass IPs to write(), not hostnames",
                              DeprecationWarning, stacklevel=2)
        try:
            if self._connectedAddr:
                udt.sendmsg(self.socket.UDTSOCKET, datagram, len(datagram),
                            ttl, inorder)
                return
            socket = [v[0] for k, v in self.addresses.iteritems() if  v[1] == addr][0]
            return udt.sendmsg(socket, datagram, len(datagram), ttl, inorder)
        except KeyError:
            print "No key found!"
        except udt.UDTException as ue:
            print ue
            if ue[0] == ECONNLOST:
                del self.reactor._udtsockets[socket.UDTSOCKET]
                self.stopListening()


    def _connectToProtocol(self):
        self.protocol.makeConnection(self)
        self.startReading()



class Connector(Port):

    def doConnect(self, fd=None):
        if not fd:
            self.socket = self.createInternetSocket()
            self.fileno = self.socket.fileno
            self.socket.connect_ex(self._connectedAddr)
            self._connectDone()
            return

        self._read(fd, self._connectedAddr)

    def doRead(self, fd=None):
        why = Port.doRead(self, self.socket.UDTSOCKET, self._connectedAddr)
        #FIXME
        if why:
            if (why[0] == ECONNLOST):
                self.stopListening()
        return why

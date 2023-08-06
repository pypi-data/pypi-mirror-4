from twisted.application.reactors import Reactor
from twisted.application.service import ServiceMaker

udtepoll = Reactor('udtepoll', 'udt4twisted.udtepollreactor',
                   'UDT epoll reactor.')


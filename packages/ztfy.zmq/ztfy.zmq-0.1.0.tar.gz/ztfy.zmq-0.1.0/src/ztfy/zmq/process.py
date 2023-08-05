### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT ulthar.net>
# Copyright (c) 2009-2012 Stefan Scherfke 
#
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################


# import standard packages
import multiprocessing
import zmq
from zmq.eventloop import ioloop, zmqstream

# import Zope3 interfaces

# import local interfaces
from ztfy.zmq.interfaces import IZMQProcess

# import Zope3 packages
from zope.interface import implements

# import local packages



class ZMQProcess(multiprocessing.Process):
    """
    This is the base for all processes and offers utility methods
    for setup and creating new streams.
    """

    implements(IZMQProcess)

    socket_type = zmq.REP

    def __init__(self, bind_addr, handler):
        super(ZMQProcess, self).__init__()

        self.context = None
        """The ØMQ :class:`~zmq.Context` instance."""

        self.loop = None
        """PyZMQ's event loop (:class:`~zmq.eventloop.ioloop.IOLoop`)."""

        self.bind_addr = bind_addr
        self.rep_stream = None
        self.handler = handler

    def setup(self):
        """Creates a :attr:`context` and an event :attr:`loop` for the process."""
        self.context = zmq.Context()
        self.loop = ioloop.IOLoop.instance()
        self.rep_stream, _ = self.stream(self.socket_type, self.bind_addr, bind=True)
        self.initStream()

    def initStream(self):
        """Initialize response stream"""
        self.rep_stream.on_recv(self.handler(self, self.rep_stream, self.stop))

    def run(self):
        """Sets up everything and starts the event loop."""
        self.setup()
        self.loop.start()

    def stop(self):
        """Stops the event loop."""
        self.loop.stop()

    def stream(self, sock_type, addr, bind, callback=None, subscribe=b''):
        """
        Creates a :class:`~zmq.eventloop.zmqstream.ZMQStream`.

        :param sock_type: The ØMQ socket type (e.g. ``zmq.REQ``)
        :param addr: Address to bind or connect to formatted as *host:port*,
                *(host, port)* or *host* (bind to random port).
                If *bind* is ``True``, *host* may be:

                - the wild-card ``*``, meaning all available interfaces,
                - the primary IPv4 address assigned to the interface, in its
                numeric representation or
                - the interface name as defined by the operating system.

                If *bind* is ``False``, *host* may be:

                - the DNS name of the peer or
                - the IPv4 address of the peer, in its numeric representation.

                If *addr* is just a host name without a port and *bind* is
                ``True``, the socket will be bound to a random port.
        :param bind: Binds to *addr* if ``True`` or tries to connect to it
                otherwise.
        :param callback: A callback for
                :meth:`~zmq.eventloop.zmqstream.ZMQStream.on_recv`, optional
        :param subscribe: Subscription pattern for *SUB* sockets, optional,
                defaults to ``b''``.
        :returns: A tuple containg the stream and the port number.

        """
        sock = self.context.socket(sock_type)

        # addr may be 'host:port' or ('host', port)
        if isinstance(addr, (str, unicode)):
            addr = addr.split(':')
        host, port = addr if len(addr) == 2 else (addr[0], None)

        # Bind/connect the socket
        if bind:
            if port:
                sock.bind('tcp://%s:%s' % (host, port))
            else:
                port = sock.bind_to_random_port('tcp://%s' % host)
        else:
            sock.connect('tcp://%s:%s' % (host, port))

        # Add a default subscription for SUB sockets
        if sock_type == zmq.SUB:
            sock.setsockopt(zmq.SUBSCRIBE, subscribe)

        # Create the stream and add the callback
        stream = zmqstream.ZMQStream(sock, self.loop)
        if callback:
            stream.on_recv(callback)

        return stream, int(port)

### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT ulthar.net>
# Copyright (c) 2009-2012 Stefan Scherfke 
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
from zmq.utils import jsonapi as json

# import Zope3 interfaces

# import local interfaces
from ztfy.zmq.interfaces import IZMQMessageHandler

# import Zope3 packages
from zope.interface import implements

# import local packages



class ZMQMessageHandler(object):
    """
    Base class for message handlers for a :class:`ztfy.zmq.process.Process`.

    Inheriting classes only need to implement a handler function for each
    message type.
    """

    implements(IZMQMessageHandler)

    handler = None

    def __init__(self, process, stream, stop, handler=None, json_load= -1):
        # ZMQ parent process
        self.process = process
        self._json_load = json_load
        # Response stream
        self.rep_stream = stream
        self._stop = stop
        # Response handler
        self.rep_handler = handler or self.handler()
        self.rep_handler.process = process

    def __call__(self, msg):
        """
        Gets called when a messages is received by the stream this handlers is
        registered at. *msg* is a list as returned by
        :meth:`zmq.core.socket.Socket.recv_multipart`.
        """
        # Try to JSON-decode the index "self._json_load" of the message
        i = self._json_load
        msg_type, data = json.loads(msg[i])
        msg[i] = data

        # Get the actual message handler and call it
        if msg_type.startswith('_'):
            raise AttributeError('%s starts with an "_"' % msg_type)

        rep = getattr(self.rep_handler, msg_type)(*msg)
        self.rep_stream.send_json(rep)

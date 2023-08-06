### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT ulthar.net>
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

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.interface import Interface, Attribute

# import local packages

from ztfy.zmq import _


class IZMQProcess(Interface):
    """ZeroMQ process interface"""

    socket_type = Attribute(_("Socket type"))

    def setup(self):
        """Initialize process context and events loop and initialize stream"""

    def stream(self, sock_type, addr, bind, callback=None, subscribe=b''):
        """Create ZMQStream"""

    def initStream(self):
        """initialize response stream"""

    def start(self):
        """Start the process"""

    def stop(self):
        """Stop the process"""


class IZMQMessageHandler(Interface):
    """ZeroMQ message handler"""

    handler = Attribute(_("Concrete message handler"))

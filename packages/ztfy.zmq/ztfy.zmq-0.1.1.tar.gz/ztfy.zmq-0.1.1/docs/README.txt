.. contents::

Introduction
============

ZTFY.zmq is a small ZTFY integration of ZeroMQ library.

It provides two main classes which are:

 - ZMQProcess, which is a ZMQ listening process, based on multiprocessing package.

 - ZMQMessageHandler, which is a simple ZMQ messages handler which delegates it's functionality
   to a ZMQ agnostic handling class.

When creating a new ZMQProcess instance, you only have to specify it's listening address and it's messages
handler.

Default ZMQ process is based on request/response (REQ/REP) messages, but this can easily be overriden in
custom subclasses.

Most of this package main concepts are based on **Stefan Scherfke** work. Thanks to him!

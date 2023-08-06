# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from twisted.internet import defer
from twisted.internet.protocol import Protocol
from twisted.internet.ssl import ClientContextFactory
from twisted.web._newclient import ResponseFailed, ResponseDone
from twisted.python.failure import Failure
from zope.interface import implements
from twisted.web.iweb import IBodyProducer, UNKNOWN_LENGTH
import json

class UnknownError(Exception):
    def __init__(self, obj=None):
        self._obj = obj

    def __str__(self):
        return str(self._obj)

class WebClientContextFactory(ClientContextFactory):
    def getContext(self, hostname, port):
        return ClientContextFactory.getContext(self)

class DataProducer(object):
    implements(IBodyProducer)
    Chunksize = 1024

    def __init__(self, body):
        self.body = body
        self.length = len(body)
        self._pos = 0
        self._consuming = True
        self._running = False
        self._deferred = None
        self._consumer = None

    def startProducing(self, consumer):
        self._deferred = defer.Deferred()
        self._consumer = consumer

        from twisted.internet import reactor
        reactor.callLater(0, self._write)

        return self._deferred

    def _write(self):
        if self._consuming:
            if self._pos < self.length:
                chunk = DataProducer.Chunksize
                if self._pos+chunk > self.length:
                    chunk = self.length-self._pos
                # print "write", self.body[self._pos:self._pos+chunk]
                self._consumer.write(self.body[self._pos:self._pos+chunk])
                self._pos += chunk

            if self._pos == self.length:
                self._deferred.callback(None)
            else:
                from twisted.internet import reactor
                reactor.callLater(0, self._write)

    def pauseProducing(self):
        self._consuming = False

    def resumeProducing(self):
        self._consuming = True
        from twisted.internet import reactor
        reactor.callLater(0, self._write)

    def stopProducing(self):
        self._consuming = False
        self._deferred.callback(None)

class RawProtocol(Protocol):
    def __init__(self, finished, length):
        self._finished = finished
        self._remaining = length 

        if length == UNKNOWN_LENGTH:
            self._unknownLength = True
            self._remaining = -1
        else:
            self._unknownLength = False

        self._data = ''

    def dataReceived(self, bytes):
        if self._remaining > 0 or self._unknownLength:
            self._data += bytes
            self._remaining -= len(bytes)

    def receiveFinished(self):
        if self._finished:
            try:
                self._finished.callback(self._data)
            except (Exception,Failure) as e:
                self._finished.errback(e)
                self._finished = None

    def connectionLost(self, reason):
        if reason.type == ResponseDone and (self._unknownLength or self._remaining == 0):
            self.receiveFinished()
        else:
            self._finished.errback(reason)
            self._finished = None

class JSONProtocol(RawProtocol):
    def __init__(self, finished, length):
        RawProtocol.__init__(self, finished, length)

    def receiveFinished(self):
        if self._finished:
            try:
                obj = json.loads(self._data)
                self._finished.callback(obj)
            except (Exception,Failure) as e:
                self._finished.errback(e)
                self._finished = None

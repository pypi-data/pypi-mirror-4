# -*- coding: utf-8 -*-
#
# by Steven Hazel

from monocle.twisted_stack.eventloop import reactor
from twisted.internet.protocol import Factory, Protocol, ClientFactory, ServerFactory
from twisted.internet import ssl
from twisted.internet.error import TimeoutError

from monocle import _o, Return, launch
from monocle.callback import Callback
from monocle.stack.network import Connection, ConnectionLost


class _Connection(Protocol):
    def __init__(self):
        self.read_cb = None
        self.connect_cb = None

    def attach(self, connection):
        self._write_flushed = connection._write_flushed
        self._closed = connection._closed

    # functions to support Protocol

    def connectionMade(self):
        self.max_buffer_size = 104857600
        self.buffer = ""
        self.transport.pauseProducing()
        if hasattr(self.factory, "handler"):
            connection = Connection(self)
            self.attach(connection)
        self.transport.registerProducer(self, False)
        if hasattr(self.factory, "handler"):
            self.factory.handler(connection)
        if self.connect_cb:
            cb = self.connect_cb
            self.connect_cb = None
            cb(None)

    def dataReceived(self, data):
        self.transport.pauseProducing()
        self.buffer += data
        if len(self.buffer) >= self.max_buffer_size:
            # Reached maximum read buffer size
            self.disconnect()
            return
        read_cb = self.read_cb
        self.read_cb = None
        read_cb(None)

    def connectionLost(self, reason):
        self._closed(reason.value)

    # functions to support IPullProducer

    def resumeProducing(self):
        if self._write_flushed:
            self._write_flushed()

    def stopProducing(self):
        # we just wait for the connection lost event
        pass

    # functions to support the StackConnection interface

    def write(self, data):
        self.transport.write(data)

    def resume(self):
        self.read_cb = Callback()
        self.transport.resumeProducing()

    def reading(self):
        return self.read_cb is not None

    def closed(self):
        return not (self.transport and
                    self.transport.connected and
                    not self.transport.disconnecting)

    def disconnect(self):
        if self.transport:
            self.transport.unregisterProducer()
            self.transport.loseConnection()


class Service(object):
    def __init__(self, handler, port, bindaddr="", backlog=128):
        self.factory = Factory()
        self.factory.protocol = _Connection
        @_o
        def _handler(s):
            try:
                yield launch(handler, s)
            finally:
                s.close()
        self.factory.handler = _handler
        self.port = port
        self.bindaddr = bindaddr
        self.backlog = backlog
        self.ssl_options = None
        self._twisted_listening_port = None

    def _add(self):
        if self.ssl_options is not None:
            cf = ssl.DefaultOpenSSLContextFactory(self.ssl_options['keyfile'],
                                                  self.ssl_options['certfile'])
            self._twisted_listening_port = reactor.listenSSL(
                self.port, self.factory, cf,
                backlog=self.backlog,
                interface=self.bindaddr)
        else:
            self._twisted_listening_port = reactor.listenTCP(
                self.port, self.factory,
                backlog=self.backlog,
                interface=self.bindaddr)

    @_o
    def stop(self):
        df = self._twisted_listening_port.stopListening()
        if df:
            yield df


class SSLService(Service):

    def __init__(self, handler, port, bindaddr="", backlog=128,
                 ssl_options=None):
        if ssl_options is None:
            ssl_options = {}
        Service.__init__(self, handler, port, bindaddr, backlog)
        self.ssl_options = ssl_options


class SSLContextFactory(ssl.ClientContextFactory):

    def __init__(self, ssl_options):
        self.ssl_options = ssl_options

    def getContext(self):
        ctx = ssl.ClientContextFactory.getContext(self)
        if 'certfile' in self.ssl_options:
            ctx.use_certificate_file(self.ssl_options['certfile'])
        if 'keyfile' in self.ssl_options:
            ctx.use_privatekey_file(self.ssl_options['keyfile'])
        return ctx


class Client(Connection):
    def __init__(self, *args, **kwargs):
        Connection.__init__(self, *args, **kwargs)
        self.ssl_options = None
        self._connection_timeout = "unknown"

    def clientConnectionFailed(self, connector, reason):
        if reason.type == TimeoutError:
            msg = ("connection timed out after %s seconds" %
                   self._connection_timeout)
        else:
            msg = reason.value
        self._closed(msg)

    @_o
    def connect(self, host, port):
        self._connection_timeout = self.timeout
        self._stack_conn = _Connection()
        self._stack_conn.attach(self)
        self._stack_conn.connect_cb = Callback()
        factory = ClientFactory()
        factory.protocol = lambda: self._stack_conn
        factory.clientConnectionFailed = self.clientConnectionFailed
        if self.ssl_options is not None:
            reactor.connectSSL(host, port, factory,
                               SSLContextFactory(self.ssl_options),
                               timeout=self._connection_timeout)
        else:
            reactor.connectTCP(host, port, factory,
                               timeout=self._connection_timeout)
        yield self._stack_conn.connect_cb


class SSLClient(Client):

    def __init__(self, ssl_options=None):
        if ssl_options is None:
            ssl_options = {}
        Connection.__init__(self)
        self.ssl_options = ssl_options


def add_service(service):
    return service._add()

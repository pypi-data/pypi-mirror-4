"""
Tests for persisted endpoints.
"""
from twisted.internet import endpoints
from twisted.trial import unittest

from maxims import endpoints as me


class _EndpointTests(object):
    """
    Base endpoint tests.
    """
    def setUp(self):
        self.endpoint = self.endpointClass(description=self.description)


    def test_cached(self):
        """
        Tests that calling ``instantiate`` several times gets the same
        result.
        """
        one, two = self.endpoint.instantiate(), self.endpoint.instantiate()
        self.assertIdentical(one, two)



class ClientEndpointTests(_EndpointTests, unittest.TestCase):
    """
    Tests for client endpoints.
    """
    endpointClass, description = me.ClientEndpoint, "tcp:x:1"

    def test_instantiate(self):
        """
        Creates a client endpoint, checks it's of the expected type, and
        verifies its attributes.
        """
        ep = self.endpoint.instantiate()
        self.assertTrue(isinstance(ep, endpoints.TCP4ClientEndpoint))
        self.assertEqual(ep._host, "x")
        self.assertEqual(ep._port, 1)


    def test_connect(self):
        """
        Tests using the stored endpoint directly to connect.

        This checks that the ``connect`` method gets called with the
        correct factory and that the return value is correctly passed
        through.
        """
        self.endpoint._cachedEndpoint = m = _MockClientEndpoint()
        factory = object()
        connectReturnValue = self.endpoint.connect(factory)
        self.assertIdentical(m.factory, factory)
        self.assertIdentical(m.connectReturnValue, connectReturnValue)



class ServerEndpointTests(_EndpointTests, unittest.TestCase):
    """
    Tests for server endpoints.
    """
    endpointClass, description = me.ServerEndpoint, "tcp:1"

    def test_instantiate(self):
        """
        Creates a server endpoint, checks it's of the expected type, and
        verifies its attributes.
        """
        ep = me.ServerEndpoint(description="tcp:1").instantiate()
        self.assertTrue(isinstance(ep, endpoints.TCP4ServerEndpoint))
        self.assertEqual(ep._port, 1)


    def test_listen(self):
        """
        Tests using the stored endpoint directly to listen.

        This checks that the ``connect`` method gets called with the
        correct factory and that the return value is correctly passed
        through.
        """
        self.endpoint._cachedEndpoint = m = _MockServerEndpoint()
        factory = object()
        listenReturnValue = self.endpoint.listen(factory)
        self.assertIdentical(m.factory, factory)
        self.assertIdentical(m.listenReturnValue, listenReturnValue)



class _MockClientEndpoint(object):
    def __init__(self):
        self.factory = None
        self.connectReturnValue = object()


    def connect(self, factory):
        self.factory = factory
        return self.connectReturnValue



class _MockServerEndpoint(object):
    def __init__(self):
        self.factory = None
        self.listenReturnValue = object()


    def listen(self, factory):
        self.factory = factory
        return self.listenReturnValue

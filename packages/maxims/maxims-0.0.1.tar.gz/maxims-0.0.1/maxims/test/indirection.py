"""
Tools for testing things that use the powerup indirection.
"""
import mock

from axiom import store


class ActivationTests(object):
    """
    Tests that powerup indirectors create a real implementation to indirect
    to on activation.
    """
    def setUp(self):
        self.store = store.Store()


    def test_activate(self):
        with mock.patch(self.implementationLocation) as m:
            p = self.makePersistedObject(self.store)
            m.assert_called_once_with(*self._expectedCallArgs(p))
            self.assertIdentical(p.indirected, m.return_value)



class PowerupTests(object):
    """
    Tests that the persisted object works as a powerup.
    """
    def setUp(self):
        self.store = store.Store()
        self.persisted = self.makePersistedObject(self.store)
        self.store.powerUp(self.persisted)


    def test_indirect(self):
        """
        Tests that adapting to the interface gets the indirected object.
        """
        inMemory = self.interface(self.store)
        self.assertIdentical(self.persisted.indirected, inMemory)


    def test_instanceOfImplementation(self):
        """
        Tests that the in-memory object is an instance of the implementation.
        """
        inMemory = self.interface(self.store)
        self.assertTrue(isinstance(inMemory, self.implementation))


    def test_sameImplementation(self):
        """
        Tests that multiple adaptations result in the same instance.
        """
        one, two = self.interface(self.store), self.interface(self.store)
        self.assertIdentical(one, two)

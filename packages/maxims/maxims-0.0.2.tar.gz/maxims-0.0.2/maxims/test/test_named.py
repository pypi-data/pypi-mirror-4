from axiom import store
from maxims import named
from twisted.trial import unittest
from zope import interface as zi


class StoredByNameTests(unittest.TestCase):
    def setUp(self):
        self.store = store.Store()


    def _remember(self):
        return named.remember(self.store, Example, IExample)


    def _forget(self):
        return named.forget(self.store, Example, IExample)


    def test_remember(self):
        """
        Tries to remember an Example.
        """
        self._remember()
        example = IExample(self.store)
        self.assertIdentical(type(example), Example)
        self.assertIdentical(example.store, self.store)


    def test_forget(self):
        """
        Remembers an example, then forgets it, and asserts it was forgotten.
        """
        self._remember()
        self._forget()
        self.assertRaises(TypeError, IExample, self.store)


    def test_forgetBeforeRemember(self):
        """
        Tests that an error is raised when attempting to forget an
        item that was never remembered.
        """
        self.assertRaises(ValueError, self._forget)



class IExample(zi.Interface):
    def exemplify():
        """
        Exemplifies.
        """


@zi.implementer(IExample)
class Example(object):
    def __init__(self, store):
        self.store = store


    def exemplify(self):
        """
        Exemplifies the self.
        """

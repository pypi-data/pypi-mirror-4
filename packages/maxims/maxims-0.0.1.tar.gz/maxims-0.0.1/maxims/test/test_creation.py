from axiom import attributes, errors, item, store
from datetime import timedelta
from epsilon import extime

from twisted.trial import unittest

from maxims import creation



class SimpleItem(item.Item):
    activations = attributes.integer(default=0)


    def activate(self):
        self.activations += 1



def _getCreationTime(item):
    """
    Gets the _CreationTime object for the given item.

    The difference between this and ``creationTime`` is that this exposes
    the ``_CreationTime`` object, whereas the latter only shows the creation
    time.
    """
    CT = creation._CreationTime
    return item.store.findUnique(CT, CT.createdItem == item)



class _CreationTimeTests(object):
    """
    Assertions for creation time tests.
    """
    _DELTA = timedelta(seconds=.1)


    def assertCreationTimeStored(self, item):
        cT = _getCreationTime(item)
        self.assertApproximates(cT.timestamp, extime.Time(), self._DELTA)
        self.assertIdentical(creation.creationTime(item), cT.timestamp)


    def assertCreationTimeNotStored(self, item):
        self.assertRaises(errors.ItemNotFound, creation.creationTime, item)



class LogCreationTests(_CreationTimeTests, unittest.TestCase):
    """
    Tests for the function that logs the creation of new objects.
    """
    def test_simple(self):
        simpleItem = SimpleItem(store=store.Store())
        self.assertCreationTimeNotStored(simpleItem)
        creation.logCreation(simpleItem)
        self.assertCreationTimeStored(simpleItem)


    def test_multipleActivations(self):
        """
        Tests that the time does not get updated when the item gets
        activated twice.
        """
        testStore = store.Store()

        simpleItem = SimpleItem(store=testStore)
        creation.logCreation(simpleItem)
        old = _getCreationTime(simpleItem).timestamp

        testStore.objectCache.uncache(simpleItem.storeID, simpleItem)
        testStore.getItemByID(simpleItem.storeID)
        new = _getCreationTime(simpleItem).timestamp
        self.assertEqual(old, new)



@creation.creationLogged
class CreationLoggedItem(item.Item):
    """
    An item that automatically has its creation logged when it is added to a
    store.
    """
    dummy = attributes.boolean()



class CreationLoggedTests(_CreationTimeTests, unittest.TestCase):
    def test_simple(self):
        """
        Tests that an item marked with the decorator gets its creation logged
        when it is added to a store.
        """
        loggedItem = CreationLoggedItem()
        # assertCreationTimeNotStored makes no sense here: store is None
        loggedItem.store = store.Store()
        self.assertCreationTimeStored(loggedItem)

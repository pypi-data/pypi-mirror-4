"""
Tests for powerup indirection tools.
"""
from axiom import attributes, iaxiom, item, store
from maxims import indirection
from twisted.trial import unittest
from zope import interface


class ILaser(interface.Interface):
    """
    A laser.
    """
    def pew(target):
        """
        Evaporates the target.
        """



@indirection.powerupIndirector(ILaser)
class StoredLaser(item.Item):
    """
    A laser in storage.
    """
    indirected = attributes.inmemory()
    damage = attributes.integer()

    def activate(self):
        """
        Takes the laser out of storage.
        """
        self.indirected = Laser(self.damage)



@interface.implementer(ILaser)
class Laser(object):
    """
    A laser.
    """
    def __init__(self, damage):
        self.damage = damage


    def pew(self, target):
        target.damageTaken += self.damage



class Critter(object):
    """
    A critter that can be attacked by a laser.
    """
    def __init__(self):
        self.damageTaken = 0



class InterfaceTests(unittest.TestCase):
    def test_implementsPowerupIndirector(self):
        """
        Tests that item classes decorated with the powerup indirector
        decorator implement ``IPowerupIndirector`` interface.
        """
        self.assertTrue(iaxiom.IPowerupIndirector.implementedBy(StoredLaser))


    def test_interface(self):
        """
        Tests that item classes decorated with the powerup indirector
        decorator have the passed interface as a powerup interface.
        """
        self.assertIn(ILaser, StoredLaser.powerupInterfaces)



class PowerupTests(unittest.TestCase):
    """
    Tests that the stored laser can be installed as a powerup.
    """
    def setUp(self):
        self.store = store.Store()
        self.storedLaser = StoredLaser(store=self.store, damage=100)
        self.store.powerUp(self.storedLaser)


    def test_indirector(self):
        """
        Tests that the indirected powering up works.
        """
        critter = Critter()
        ILaser(self.store).pew(critter)
        self.assertEqual(critter.damageTaken, 100)


    def test_identicalPowerups(self):
        """
        Tests that the indirector consistently indirects to the same element.
        """
        self.assertIdentical(ILaser(self.store), ILaser(self.store))

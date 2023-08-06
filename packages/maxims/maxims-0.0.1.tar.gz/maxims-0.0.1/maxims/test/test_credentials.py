"""
Tests for stored credentials.
"""
from twisted.cred import credentials
from twisted.trial import unittest

from maxims import credentials as mc


class UsernamePasswordTests(unittest.TestCase):
    """
    Tests for a storable username and password pair.
    """
    def test_interface(self):
        """
        Tests that the item implements the correct interface.
        """
        I, C = credentials.IUsernamePassword, mc.UsernamePassword
        self.assertTrue(I.implementedBy(C))


    def test_simple(self):
        """
        Tests that attributes can be accessed as expected.
        """
        username, password = "username", "password"
        up = mc.UsernamePassword(username=username, password=password)
        self.assertEqual(up.username, username)
        self.assertEqual(up.password, password)

"""
Support for credentials stored using txscrypt.
"""
from __future__ import absolute_import

from axiom import attributes, item
from twisted.cred import credentials, error as ce
from twisted.internet import defer
from txscrypt import wrapper as txsw
from zope import interface


@interface.implementer(credentials.IUsernameHashedPassword)
class UsernameScryptedPassword(item.Item):
    """
    A username and a securely stored password.
    """
    powerupInterfaces = [credentials.IUsernameHashedPassword]

    username = attributes.bytes(allowNone=False)
    _encrypted = attributes.bytes(allowNone=False)

    def checkPassword(self, password):
        """
        Checks that the provided password is the same as the one used to
        create this set of credentials.
        """
        return txsw.checkPassword(self._encrypted, password)


    @classmethod
    def storePassword(cls, username, password, **kwargs):
        """
        Creates an ``IUsernameHashedPassword`` with the given username and
        an encrypted key securely derived from the given password.

        The ``kwargs`` are passed on to txscrypt's ``computeKey``.
        """
        d = txsw.computeKey(password, **kwargs)

        @d.addCallback
        def buildItem(encrypted):
            return cls(username=username, _encrypted=encrypted)

        return d


    @classmethod
    def addPowerupFor(cls, empowered, username, password, **kwargs):
        """
        Adds a ``IUsernameHashedPassword`` powerup for the ``empowered``
        implementation that will verify against the given credentials.

        The ``kwargs`` are passed on to ``storePassword``.
        """
        d = cls.storePassword(username, password, **kwargs)

        @d.addCallback
        def powerUp(usernameHashedPassword):
            usernameHashedPassword.store = empowered.store
            empowered.powerUp(usernameHashedPassword)
            return usernameHashedPassword

        return d

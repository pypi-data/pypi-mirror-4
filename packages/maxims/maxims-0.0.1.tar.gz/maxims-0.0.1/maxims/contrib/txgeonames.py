"""
A persisted txgeonames client.
"""
from __future__ import absolute_import

from axiom import attributes, item
from maxims import indirection
from txgeonames import client, interface


@indirection.powerupIndirector(interface.IGeonamesClient)
class PersistedGeonamesClient(item.Item):
    """
    A persisted Geonames client.

    This can be installed as a powerup like so::

        client = PersistedGeonamesClient(store=s, username=u"demo")
        empowered.powerup(client)

    Please note that changes to the username will only take effect after the
    next time this object is loaded from a store.
    """
    indirected = attributes.inmemory()
    username = attributes.text(allowNone=False)

    def activate(self):
        """
        Creates an in-memory Geonames client.
        """
        self.indirected = client.GeonamesClient(self.username)

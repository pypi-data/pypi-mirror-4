"""
Persistence for txeasymail.
"""
from __future__ import absolute_import

from axiom import attributes, item
from maxims import indirection
from txeasymail import mailer, interface


@indirection.powerupIndirector(interface.IMailer)
class PersistedMailer(item.Item):
    """
    A persisted mailer.
    """
    endpoint = attributes.reference()
    credentials = attributes.reference()
    indirected = attributes.inmemory()

    def activate(self):
        endpoint = self.endpoint.instantiate()
        self.indirected = mailer.Mailer(endpoint, self.credentials)

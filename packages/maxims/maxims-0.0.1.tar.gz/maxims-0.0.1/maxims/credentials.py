"""
Stored credentials.
"""
from axiom import attributes, item
from twisted.cred import credentials
from zope import interface


@interface.implementer(credentials.IUsernamePassword)
class UsernamePassword(item.Item):
    """
    A stored username and password.

    Since the password is stored in plaintext, this is primarily useful for
    credentials you use, not for credentials you check against.
    """
    username = attributes.bytes(allowNone=False)
    password = attributes.bytes(allowNone=False)

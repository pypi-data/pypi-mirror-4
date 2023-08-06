"""
Tools for powerup indirection.
"""
from axiom import iaxiom
from zope import interface as zi


def powerupIndirector(interface):
    """
    A decorator for a powerup indirector from a single interface to a single
    in-memory implementation.

    The in-memory implementation that is being indirected to must be created
    in the ``activate`` callback, and then assigned to ``self.indirected``,
    which is an ``inmemory`` attribute.
    """
    def decorator(cls):
        zi.implementer(iaxiom.IPowerupIndirector)(cls)
        cls.powerupInterfaces = [interface]
        cls.indirect = _indirect
        return cls

    return decorator


def _indirect(self, _interface):
    """
    Returns the ``indirected`` attribute.
    """
    return self.indirected

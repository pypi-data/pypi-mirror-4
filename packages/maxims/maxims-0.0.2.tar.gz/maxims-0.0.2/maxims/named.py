from axiom import attributes, iaxiom, item
from twisted.python.reflect import fullyQualifiedName, namedAny
from zope import interface as zi


@zi.implementer(iaxiom.IPowerupIndirector)
class _StoredByName(item.Item):
    """
    A powerup indirector for something that is stored by name.
    """
    className = attributes.bytes(allowNone=False)

    def indirect(self, interface):
        return interface(namedAny(self.className)(self.store))



def remember(empowered, powerupClass, interface):
    className = fullyQualifiedName(powerupClass)
    powerup = _StoredByName(store=empowered.store, className=className)
    empowered.powerUp(powerup, interface)


def forget(empowered, powerupClass, interface):
    className = fullyQualifiedName(powerupClass)
    withThisName = _StoredByName.className == className
    items = empowered.store.query(_StoredByName, withThisName)

    if items.count() == 0:
        template = "No named powerups for {} (interface: {})".format
        raise ValueError(template(powerupClass, interface))

    for stored in items:
        empowered.powerDown(stored, interface)
        stored.deleteFromStore()

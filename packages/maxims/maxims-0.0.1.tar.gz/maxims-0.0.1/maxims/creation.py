from axiom import attributes, item
from epsilon import extime


class _CreationTime(item.Item):
    """
    An item that remembers the creation time of another item.
    """
    createdItem = attributes.reference(allowNone=False)
    timestamp = attributes.timestamp(defaultFactory=extime.Time)



def logCreation(item):
    """
    Logs the creation of the given item as having happened right now.
    """
    _CreationTime(store=item.store, createdItem=item)


def creationTime(item):
    """
    Returns the creation time of the given item.
    """
    forThisItem = _CreationTime.createdItem == item
    return item.store.findUnique(_CreationTime, forThisItem).timestamp


def creationLogged(itemClass):
    """
    A decorator that makes the given item class automatically have its
    creation time logged when its instances are added to a store for the
    first time.
    """
    itemClass.stored = logCreation
    return itemClass

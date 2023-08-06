""" Custom events
"""
from zope.interface import implements
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent import ObjectModifiedEvent

class IObjectInitializedEvent(IObjectModifiedEvent):
    """An object is being initialised, i.e. populated for the first time
    """

class ObjectInitializedEvent(ObjectModifiedEvent):
    """ An object is being initialised, i.e. populated for the first time
    """
    implements(IObjectInitializedEvent)

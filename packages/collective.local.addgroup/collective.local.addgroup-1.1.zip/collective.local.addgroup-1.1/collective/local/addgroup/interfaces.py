from zope.interface import Interface
from zope import schema
from zope.component.interfaces import IObjectEvent


class IAddNewGroup(Interface):
    """Include a add new group link to the sharing tab.
    """


class IGroupRemoved(IObjectEvent):
    """Event notified when a group is removed from the list.
    """

    groupid = schema.TextLine(title=u"Group id")

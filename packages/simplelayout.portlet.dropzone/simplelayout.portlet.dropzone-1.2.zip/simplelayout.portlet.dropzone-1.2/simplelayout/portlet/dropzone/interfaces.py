from zope.interface import Interface, Attribute
from zope.viewlet.interfaces import IViewletManager

class ISlotBlock(Interface):
    """ This marker Interface descripes the slot to fill (portlet)"""

class IPortletColumn(Interface):
    """ This marker is for portlet columns"""

class ISimpleLayoutListingPortletViewlet(Interface):
    """ marker interface """

class ISimpleViewletPortletListingProvider(IViewletManager):
    """special viewletmanager for blocks in portlets
    """

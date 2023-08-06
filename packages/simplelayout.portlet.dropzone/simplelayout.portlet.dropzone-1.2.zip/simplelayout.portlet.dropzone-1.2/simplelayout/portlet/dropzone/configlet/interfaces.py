from zope.interface import Interface
from zope import schema

from simplelayout.portlet.dropzone import websiteMessageFactory as _


class ISimplelayoutConfigurationPortlet(Interface):
    """This interface defines the portlet size conf."""

    small_size_portlet = schema.Int(title=_(u"Small size (portlet)"),
                            description=_(u'enter value (px)'),
                            default= 35,
                            required=True)

    middle_size_portlet = schema.Int(title=_(u"Middle size (portlet)"),
                            description=_(u'enter value (px)'),
                            default= 80,
                            required=True)

    full_size_portlet = schema.Int(title=_(u"Full/big size (portlet)"),
                            description=_(u'enter value (px)'),
                            default= 170,
                            required=True)

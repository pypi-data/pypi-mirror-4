from zope.i18nmessageid import MessageFactory
websiteMessageFactory = MessageFactory('simplelayout.portlet.dropzone')



#updates constants
import update_sl_const

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

from simplelayout.base.viewlets.viewlets import SimpleLayoutListingViewlet

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.interface import implements

from simplelayout.portlet.dropzone.interfaces import (
    ISimpleLayoutListingPortletViewlet)

class SimplelayoutPortletListingViewlet(SimpleLayoutListingViewlet):
    render = ViewPageTemplateFile('listing_portlet.pt')
    implements(ISimpleLayoutListingPortletViewlet)

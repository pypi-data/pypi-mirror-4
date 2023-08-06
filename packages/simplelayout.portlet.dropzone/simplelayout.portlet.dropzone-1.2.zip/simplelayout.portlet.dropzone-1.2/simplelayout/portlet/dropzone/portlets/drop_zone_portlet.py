from zope.interface import implements
from zope.component import getAdapters, queryMultiAdapter
from Products.CMFCore.utils import getToolByName
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.viewlet.interfaces import IViewletManager, IViewlet
from zope.contentprovider.tales import addTALNamespaceData
from simplelayout.portlet.dropzone.interfaces import (
    ISimpleLayoutListingPortletViewlet, ISlotBlock)


class ISimplelayoutDropZonePortlet(IPortletDataProvider):
    """
    marker Interface for portlet
    """


class Assignment(base.Assignment):
    """Portlet assignment.
    """
    implements(ISimplelayoutDropZonePortlet)
    @property
    def title(self):
        return "Simplelayout DropZone Portlet"


class Renderer(base.Renderer):
    """Portlet renderer
    """

    render = ViewPageTemplateFile('drop_zone_portlet.pt')


    def update(self):
        context = self.context


    def blockRenderer(self,name="simplelayout.portlet.listing"):

        manager = queryMultiAdapter((self.context, self.request, self),
                                    IViewletManager, name)
        viewlet_adapters = getAdapters(
            (manager.context, manager.request, manager.__parent__, manager),
            IViewlet)

        if manager is None:
            return ''
        addTALNamespaceData(manager, self.context)
        manager.update()
        return manager.render()

    def getBlockPortlets(self):
        return self.context.getFolderContents(
            {'object_provides':[ISlotBlock.__identifier__]})

    @property
    def available(self):
        mtool = getToolByName(self.context,'portal_membership')
        if self.getBlockPortlets():
            return True
        if mtool.checkPermission('Modify portal content', self.context):
            return True
        return False


class AddForm(base.NullAddForm):
    def create(self):
        return Assignment()

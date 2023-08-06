from interfaces import ISlotBlock, IPortletColumn
from configlet.interfaces import ISimplelayoutConfigurationPortlet


SLOT_INTERFACES_MAP = {'slotblock' : ISlotBlock, }

COLUMN_INTERFACES_MAP = {'portletcolumn' : IPortletColumn, }

IMAGE_SIZE_MAP_PER_INTERFACE = {
    IPortletColumn : dict(small_size = 'small_size_portlet',
                          middle_size = 'middle_size_portlet',
                          full_size = 'full_size_portlet'), }

CONFIGLET_INTERFACE_MAP = {
    'sl-portlet-config': ISimplelayoutConfigurationPortlet, }

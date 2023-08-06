from simplelayout.base.config import (
    SLOT_INTERFACES_MAP as orig_slot_ifaces,
    COLUMN_INTERFACES_MAP as orig_column_ifaces,
    IMAGE_SIZE_MAP_PER_INTERFACE as orig_size_map,
    CONFIGLET_INTERFACE_MAP as orig_config_iface_map)


from config import SLOT_INTERFACES_MAP,  COLUMN_INTERFACES_MAP, \
                   IMAGE_SIZE_MAP_PER_INTERFACE, CONFIGLET_INTERFACE_MAP


orig_slot_ifaces.update(SLOT_INTERFACES_MAP)
orig_column_ifaces.update(COLUMN_INTERFACES_MAP)
orig_size_map.update(IMAGE_SIZE_MAP_PER_INTERFACE)
orig_config_iface_map.update(CONFIGLET_INTERFACE_MAP)

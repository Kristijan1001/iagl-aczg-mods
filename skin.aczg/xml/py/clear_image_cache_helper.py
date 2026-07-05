# -*- coding: utf-8 -*-

import xbmcvfs

try:
    some_target = "special://userdata/addon_data/service.listitem.helper/img/"
    target_is_present = xbmcvfs.exists(some_target)
    if target_is_present:
        xbmcvfs.rmdir(some_target,True)
except:
    pass
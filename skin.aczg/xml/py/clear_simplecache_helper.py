# -*- coding: utf-8 -*-

import xbmc
import xbmcvfs
import xbmcgui

try:
    are_you_sure = xbmcgui.Dialog().yesno("Simple Cache Module","Clearing \"Simple Cache Module\" cache. Continue?")
    if are_you_sure:
        some_file = "special://userdata/addon_data/script.module.simplecache/simplecache.db"
        file_is_present = xbmcvfs.exists(some_file)
        if file_is_present:
            xbmcvfs.delete(some_file)
            xbmc.executebuiltin('Notification("Simple Cache Module",Cache cleared,5000,DefaultIconWarning.png)')
        else:
            xbmc.executebuiltin('Notification("Simple Cache Module",Cache already empty,5000,DefaultIconWarning.png)')
except:
    pass
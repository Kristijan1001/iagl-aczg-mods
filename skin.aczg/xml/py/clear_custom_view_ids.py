# -*- coding: utf-8 -*-

import xbmc
import xbmcgui

try:
    are_you_sure = xbmcgui.Dialog().yesno("Confluence ZEITGEIST","Resetting all View IDs to default values. Continue?")
    if are_you_sure:
        xbmc.executebuiltin('Skin.SetString(ForcePresetViewsMoviesCategories,)')
        xbmc.executebuiltin('Skin.SetString(ForcePresetViewsTvShowsCategories,)')
        xbmc.executebuiltin('Skin.SetString(ForcePresetViewsMusicPicturesCategories,)')
        xbmc.executebuiltin('Skin.SetString(ForcePresetViewsGlobalMiscCategories,)')
        xbmc.executebuiltin('Notification(Skin settings,All View IDs have been reset,5000,DefaultIconWarning.png)')
except:
    pass
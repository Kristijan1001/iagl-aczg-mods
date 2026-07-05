# -*- coding: utf-8 -*-

import xbmc
import xbmcgui

try:
    are_you_sure = xbmcgui.Dialog().yesno("Confluence ZEITGEIST","Resetting all custom sub menu paths to default values. Continue?")
    if are_you_sure:
        xbmc.executebuiltin('Skin.Reset(CustomSubMenusMoviesPath)')
        xbmc.executebuiltin('Skin.Reset(CustomSubMenusTvShowsPath)')
        xbmc.executebuiltin('Skin.Reset(CustomSubMenusMusicPath)')
        xbmc.executebuiltin('Notification(Skin settings,Custom sub menu paths have been reset,5000,DefaultIconWarning.png)')
except:
    pass
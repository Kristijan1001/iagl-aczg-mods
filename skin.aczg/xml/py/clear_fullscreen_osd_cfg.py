# -*- coding: utf-8 -*-

import xbmc
import xbmcgui

try:
    are_you_sure = xbmcgui.Dialog().yesno("Confluence ZEITGEIST","Resetting Fullscreen OSD to default values. Continue?")
    if are_you_sure:
        xbmc.executebuiltin('Skin.Reset(ReducedFullScreenInfoOSDVideoResolution)')
        xbmc.executebuiltin('Skin.Reset(ReducedFullScreenInfoOSDAudioCodec)')
        xbmc.executebuiltin('Skin.Reset(ReducedFullScreenInfoOSDAudioSubLanguage)')
        xbmc.executebuiltin('Skin.Reset(ReducedFullScreenInfoOSDAudioChannels)')
        xbmc.executebuiltin('Skin.Reset(ReducedFullScreenInfoEndTime)')
        xbmc.executebuiltin('Skin.Reset(ReducedFullScreenInfoOSDArtworkDisable)')
        xbmc.executebuiltin('Notification(Skin settings,Fullscreen OSD has been reset,5000,DefaultIconWarning.png)')
except:
    pass
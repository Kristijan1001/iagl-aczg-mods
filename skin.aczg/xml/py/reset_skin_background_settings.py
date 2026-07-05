# -*- coding: utf-8 -*-

import xbmc
import xbmcgui

try:
    are_you_sure = xbmcgui.Dialog().yesno("Confluence ZEITGEIST","Resetting background to default.[CR][CR]Continue?")
    if are_you_sure:
        
        xbmc.executebuiltin('Skin.Reset(BackgroundsAutoPreviewOnSelectDisable)')
        xbmc.executebuiltin('Skin.Reset(UseCustomBackground)')
        xbmc.executebuiltin('Skin.Reset(BackgroundDarkenStrength)')
        
        uiColorVariant = xbmc.getInfoLabel('Skin.String(uiColorVariant)')
        
        if not uiColorVariant:
            xbmc.executebuiltin('Skin.Reset(BackgroundType)')
        elif uiColorVariant == "1":
            xbmc.executebuiltin('Skin.SetString(BackgroundType,14)')
        elif uiColorVariant == "2":
            xbmc.executebuiltin('Skin.SetString(BackgroundType,15)')
        
        xbmc.executebuiltin('Notification(Skin settings,Background has been reset to default,5000,DefaultIconWarning.png)')
except:
    pass
# -*- coding: utf-8 -*-

import xbmc
import xbmcgui

try:
    are_you_sure = xbmcgui.Dialog().yesno("Confluence ZEITGEIST","[COLOR=redwarning]Warning:[/COLOR]  Resetting all Skin settings to default.[CR][CR]Are you really sure to continue?")
    if are_you_sure:
        xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.SetSettingValue","id":1,"params":{"setting":"lookandfeel.skintheme","value":"SKINDEFAULT"}}')
        xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.SetSettingValue","id":1,"params":{"setting":"lookandfeel.skincolors","value":"SKINDEFAULT"}}')
        xbmc.executebuiltin("Skin.ResetSettings()")
        xbmc.sleep(2500)
        xbmc.executebuiltin('Notification(Skin settings,Skin settings have been reset to default values,5000,DefaultIconWarning.png)')
except:
    pass
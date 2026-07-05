# -*- coding: utf-8 -*-

import xbmc, xbmcgui, sys, os

variant = ""

args = sys.argv
for arg in args:
    if arg != os.path.basename(__file__):
        
        if arg.startswith('variant='):
            variant = arg[8:]



uiColorVariantName = ""

if variant == '':
    uiColorVariantName             = 'Kodi Blue'
    
    uiColorVariantBackground       = ''
    uiColorVariantBackgroundName   = 'Frosted Glass · Sunrise'
    
elif variant == '1':
    uiColorVariantName             = 'Perfect Pink'
    
    uiColorVariantBackground       = '14'
    uiColorVariantBackgroundName   = 'Frosted Glass · Perfect Pink'
    
elif variant == '2':
    uiColorVariantName             = 'Electric Violet'
    
    uiColorVariantBackground       = '15'
    uiColorVariantBackgroundName   = 'Frosted Glass · Electric Violet'



if uiColorVariantName != "":
    
    uiColorVariantNameTheme = 'SKINDEFAULT' if variant == '' else uiColorVariantName
    
    xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.SetSettingValue","id":1,"params":{"setting":"lookandfeel.skintheme","value":"'+uiColorVariantNameTheme+'"}}')
    xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.SetSettingValue","id":1,"params":{"setting":"lookandfeel.skincolors","value":"'+uiColorVariantNameTheme+'"}}')
    
    try:
        are_you_sure = xbmcgui.Dialog().yesno("Confluence ZEITGEIST","Color scheme has been set to [COLOR=blue]"+uiColorVariantName+"[/COLOR][CR][CR]Should we also change your background to the matching[CR][COLOR=blue]"+uiColorVariantBackgroundName+"[/COLOR] [LIGHT]?[/LIGHT]")
        if are_you_sure:
            xbmc.executebuiltin('Skin.SetString(UseCustomBackground,)')
            xbmc.executebuiltin('Skin.SetString(BackgroundDarkenStrength,1)')
            xbmc.executebuiltin('Skin.SetString(BackgroundType,'+uiColorVariantBackground+')')
        xbmc.executebuiltin('SetFocus(109)')
    except:
        pass
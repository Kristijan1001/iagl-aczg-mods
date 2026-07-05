# -*- coding: utf-8 -*-

import xbmc
import xbmcgui

skinzoom = '-26'
xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Settings.SetSettingValue", "params": {"setting":"lookandfeel.skinzoom","value":'+skinzoom+'}, "id": 1}')
xbmcgui.Window(10000).setProperty('CinemaHelper.GetSettingValue.lookandfeel.skinzoom',skinzoom)
xbmc.executebuiltin('Skin.SetString(lookandfeel.skinzoom,'+skinzoom+')')
xbmc.sleep(300)
xbmc.executebuiltin('ReloadSkin()')
xbmc.sleep(150)

isUhdScreenStringSuffix = '_uhd' if xbmc.getCondVisibility('[ !String.IsEmpty(Window(10000).Property(CH.HiResScreen)) + String.IsEqual(Window(10000).Property(CH.RunningAmlogicBuild),False) ]') else ''

xbmc.executebuiltin('Notification(Cinemascope Mode  [B]$VAR[String_Enabled][/B],[B]$INFO[Skin.String(CinemascopeMask)][/B] Mask   Skin-Zoom -26%,2000,dialogs/scope/ScopeMode'+isUhdScreenStringSuffix+'.png)')

if xbmc.getCondVisibility('String.IsEqual(Window(10000).Property(CH.RunningAmlogicBuild),True) + Player.HasMedia + Player.HasVideo'):
	xbmc.executebuiltin('Seek(-2)')
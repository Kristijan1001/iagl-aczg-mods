# -*- coding: utf-8 -*-

import xbmc, xbmcgui

SetId = xbmc.getInfoLabel("ListItem.SetId")

if SetId:
    xbmcgui.Window(10000).setProperty('MovieSetDBID_TMP',str(SetId))
    xbmc.executebuiltin('Dialog.Close(all)')
    xbmc.sleep(300)
    xbmc.executebuiltin('ActivateWindow(Videos,"videodb://movies/sets/'+SetId+'/?setid='+SetId+'",return)')

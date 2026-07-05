# -*- coding: utf-8 -*-

import xbmc, xbmcgui

try:
    show_changelog = xbmcgui.Dialog().yesno("Confluence ZEITGEIST updated","","$LOCALIZE[15067][LIGHT]$INFO[Window(Home).Property(NewVersionInfoTimeout_Label)][/LIGHT]","$VAR[String_Whats_New]")
    
    if show_changelog:
        xbmc.executebuiltin('ActivateWindow(1186)')
    
except:
    pass
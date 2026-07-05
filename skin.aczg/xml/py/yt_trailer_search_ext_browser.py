# -*- coding: utf-8 -*-

import xbmc
import sys
if sys.version_info.major == 2:# Python 2
    import urllib
else:
    import urllib.parse
import xbmcgui
import os

try:
    if not xbmc.getCondVisibility("Player.HasMedia") or xbmcgui.Dialog().yesno("Trailer Search","Kodi is playing media at the moment.[CR][CR]Stop playback and open Web Browser?"):
        
        OSDinfodialogButtonActive = xbmcgui.Window(10000).getProperty('OSDinfodialogButtonActive')
        
        if not OSDinfodialogButtonActive:
            xbmc.executebuiltin('AlarmClock(DialogVideoInfoTrailerSearchResetButtonFocus,SetFocus(8),00:00:01,silent)')
        else:
            xbmc.executebuiltin("SetFocus(888)")
        
        
        xbmc.executebuiltin("PlayerControl(Stop)")
        
        
        url_base = 'https://www.youtube.com/results?search_query='
        
        param_base = '&sp='
        param_filter_video_under_4min = 'EgQQARgB'
        
        language_string = ' '+sys.argv[3] if sys.argv[3] else ''
        year_string     = ' '+sys.argv[2] if sys.argv[2] else ''
        
        search_string = sys.argv[1] + ' Trailer' + language_string + year_string
        
        search_string = urllib.quote_plus(search_string) if sys.version_info.major == 2 else urllib.parse.quote_plus(search_string)# Python 2/3
        
        url_final = url_base + search_string + param_base + param_filter_video_under_4min
        
        webBrowserType = int(xbmc.getInfoLabel("Skin.String(TrailerSearchWebBrowserType)")) if xbmc.getInfoLabel("Skin.String(TrailerSearchWebBrowserType)") else 0
        
        is_Windows = xbmc.getCondVisibility("System.Platform.Windows")
        is_Android = xbmc.getCondVisibility("System.Platform.Android") or 'ANDROID_STORAGE' in os.environ
        is_Linux   = xbmc.getCondVisibility("System.Platform.Linux") and not is_Android
        is_OSX     = xbmc.getCondVisibility("System.Platform.OSX")
        is_iOS     = xbmc.getCondVisibility("System.Platform.iOS")
        is_tvOS    = xbmc.getCondVisibility("System.Platform.tvOS")
        is_webOS   = xbmc.getCondVisibility("System.Platform.webOS")
        
        if not webBrowserType:
            
            if is_Windows:
                import webbrowser
                webbrowser.open(url_final)
            elif is_Android:
                TrailerSearchWebBrowserAndroid = str(xbmc.getInfoLabel("Skin.String(TrailerSearchWebBrowserAndroid)")) if xbmc.getInfoLabel("Skin.String(TrailerSearchWebBrowserAndroid)") else ""
                
                if not TrailerSearchWebBrowserAndroid:
                    xbmc.executebuiltin("StartAndroidActivity(com.android.browser,android.intent.action.VIEW,,"+url_final+")")
                else:
                    xbmc.executebuiltin("StartAndroidActivity("+str(TrailerSearchWebBrowserAndroid)+",android.intent.action.VIEW,,"+url_final+")")
            elif is_OSX:
                xbmc.executebuiltin("System.Exec(open "+url_final+")")
            elif is_Linux:
                xbmc.executebuiltin("System.Exec(xdg-open "+url_final+")")
            elif is_iOS or is_tvOS:
                from ctypes import *
                import webbrowser
                webbrowser.open(url_final)
            
        else:
            
            if is_Windows:
                
                webBrowserCustomPath = xbmc.getInfoLabel("Skin.String(TrailerSearchWebBrowserCustomPath)")
                
                if webBrowserCustomPath:
                    webBrowserCustomPath = webBrowserCustomPath.replace('\\','\\\\')
                    import subprocess
                    subprocess.call(webBrowserCustomPath + ' ' + url_final)
                
            elif is_Android:
                
                TrailerSearchWebBrowserAndroidCustomID = str(xbmc.getInfoLabel("Skin.String(TrailerSearchWebBrowserAndroidCustomID)"))
                
                if TrailerSearchWebBrowserAndroidCustomID:
                    xbmc.executebuiltin("StartAndroidActivity("+str(TrailerSearchWebBrowserAndroidCustomID)+",android.intent.action.VIEW,,"+url_final+")")
                
except:
    pass

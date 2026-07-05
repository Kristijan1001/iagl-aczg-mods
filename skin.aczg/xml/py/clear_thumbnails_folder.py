# -*- coding: utf-8 -*-

import xbmc
import xbmcvfs
import xbmcgui
import sys
import os
import shutil

try:
    are_you_sure = xbmcgui.Dialog().yesno("Confluence ZEITGEIST",'[COLOR=redwarning]Warning:[/COLOR]  Deleting Kodi "userdata/Thumbnails/" folder.[CR]Kodi will be shut down afterwards. Continue?')
    if are_you_sure:
        
        some_target = "special://home/userdata/Thumbnails"
        some_target_s = some_target + '/'
        
        if sys.version_info.major == 2:# Python 2
          some_target = xbmc.translatePath(some_target).decode('utf-8')
          some_target_s = xbmc.translatePath(some_target_s).decode('utf-8')
        else:
          some_target = xbmcvfs.translatePath(some_target)
          some_target_s = xbmcvfs.translatePath(some_target_s)
        
        target_is_present = xbmcvfs.exists(some_target_s)
        
        if target_is_present:
            
            shutil.rmtree(some_target_s, ignore_errors=True)
            xbmcvfs.rmdir(some_target_s, force=True)
            
            xbmc.executebuiltin('Notification(Kodi,"userdata/Thumbnails/" deleted. Exiting Kodi now...,5000,DefaultIconWarning.png)')
            
            ShutdownScreenDisabled = xbmc.getCondVisibility("Skin.HasSetting(ShutdownScreenDisabled)")
            if not ShutdownScreenDisabled:
                xbmc.executebuiltin("SetProperty(ShutdownInProgressText,Exit,home)")
            
            xbmc.sleep(5000)
            
            ElecSystem = xbmc.getCondVisibility("System.HasAddon(service.libreelec.settings)") or xbmc.getCondVisibility("System.HasAddon(service.coreelec.settings)")
            
            if ElecSystem:
                os.system("systemctl restart kodi")
            else:
                xbmc.executebuiltin('Quit')
            
        else:
            xbmc.executebuiltin('Notification(Kodi,"userdata/Thumbnails/" already empty,5000,DefaultIconWarning.png)')
        
except:
    pass
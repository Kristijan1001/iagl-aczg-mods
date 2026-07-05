# -*- coding: utf-8 -*-

import xbmc, xbmcgui, time

try:
    
    if xbmcgui.Window(10000).getProperty('NewVersionInfoTimeout_Stopped'):
        xbmcgui.Window(10000).clearProperty('NewVersionInfoTimeout_Stopped')
    
    if not xbmcgui.Window(10000).getProperty('NewVersionInfoTimeout_Stopped'):
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout','10')
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout_Label',' (10s)')
        time.sleep(1)
    if not xbmcgui.Window(10000).getProperty('NewVersionInfoTimeout_Stopped'):
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout','9')
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout_Label',' (9s)')
        time.sleep(1)
    if not xbmcgui.Window(10000).getProperty('NewVersionInfoTimeout_Stopped'):
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout','8')
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout_Label',' (8s)')
        time.sleep(1)
    if not xbmcgui.Window(10000).getProperty('NewVersionInfoTimeout_Stopped'):
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout','7')
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout_Label',' (7s)')
        time.sleep(1)
    if not xbmcgui.Window(10000).getProperty('NewVersionInfoTimeout_Stopped'):
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout','6')
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout_Label',' (6s)')
        time.sleep(1)
    if not xbmcgui.Window(10000).getProperty('NewVersionInfoTimeout_Stopped'):
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout','5')
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout_Label',' (5s)')
        time.sleep(1)
    if not xbmcgui.Window(10000).getProperty('NewVersionInfoTimeout_Stopped'):
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout','4')
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout_Label',' (4s)')
        time.sleep(1)
    if not xbmcgui.Window(10000).getProperty('NewVersionInfoTimeout_Stopped'):
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout','3')
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout_Label',' (3s)')
        time.sleep(1)
    if not xbmcgui.Window(10000).getProperty('NewVersionInfoTimeout_Stopped'):
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout','2')
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout_Label',' (2s)')
        time.sleep(1)
    if not xbmcgui.Window(10000).getProperty('NewVersionInfoTimeout_Stopped'):
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout','1')
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout_Label',' (1s)')
        time.sleep(1)
    if not xbmcgui.Window(10000).getProperty('NewVersionInfoTimeout_Stopped'):
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout','0')
        xbmcgui.Window(10000).setProperty('NewVersionInfoTimeout_Label',' (0s)')
        time.sleep(0.5)
    
    if not xbmcgui.Window(10000).getProperty('NewVersionInfoTimeout_Stopped'):
        xbmc.executebuiltin('Dialog.Close(YesNoDialog)')
    
except:
    pass
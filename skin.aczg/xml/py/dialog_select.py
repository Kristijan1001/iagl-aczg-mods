# -*- coding: utf-8 -*-

import xbmc, xbmcgui, os, sys



title = ''
dialog_select_input_list = []
dialog_select_input_list_values = []


skip_further_options_and_values = False
args = sys.argv
for arg in args:
    if arg != os.path.basename(__file__):
        
        if arg.startswith('header='):
            title = arg[7:]
        
        if arg.startswith('setting='):
            setting = arg[8:]
        
        if arg.startswith('option=') and arg[7:] and not skip_further_options_and_values:
            dialog_select_input_list.append(arg[7:])
        elif arg.startswith('option=') and not arg[7:] and not skip_further_options_and_values:
            skip_further_options_and_values = True
        
        if arg.startswith('value=') and not skip_further_options_and_values:
            dialog_select_input_list_values.append(arg[6:])



if setting == "weather_location":
    skin_string_setting = xbmcgui.Window(12600).getProperty('Location')
else:
    skin_string_setting = xbmc.getInfoLabel('Skin.String('+setting+')')



preselect_item = -1



for i in range(len(dialog_select_input_list)):
    
    if setting == "weather_location":
        if skin_string_setting and dialog_select_input_list[i] == skin_string_setting:
            preselect_item = i
            break
    else:
        if dialog_select_input_list_values[i] == skin_string_setting:
            preselect_item = i
            break



if len(dialog_select_input_list) >= 1:
    select_dialog = xbmcgui.Dialog().select(title, dialog_select_input_list, preselect=preselect_item)
    
    
    
    if not select_dialog is None and select_dialog >= 0:
        
        out_string = dialog_select_input_list_values[select_dialog]
        
        
        if skin_string_setting != out_string:
            
            if setting != "weather_location":
                xbmc.executebuiltin('Skin.SetString('+setting+',"'+str(out_string)+'")')
            
            if setting == "uiColorVariant":
                xbmc.executebuiltin('RunScript("special://skin/xml/py/uicolor_set.py","variant='+out_string+'")')
            
            if setting == "weather_location":
                if xbmc.getCondVisibility('Window.IsActive(Home)') and not xbmc.getCondVisibility('Window.IsActive(Weather)') and out_string != "edit":
                    xbmc.executebuiltin('ActivateWindow(Weather)')
                
                if out_string != "edit":
                    xbmc.executebuiltin('SetProperty(Locations,,weather)')
                    xbmc.executebuiltin('SetProperty(Location1,,weather)')
                
                if out_string == "1":
                    xbmc.executebuiltin('Weather.LocationSet(1)')
                elif out_string == "2":
                    xbmc.executebuiltin('Weather.LocationSet(2)')
                elif out_string == "3":
                    xbmc.executebuiltin('Weather.LocationSet(3)')
                elif out_string == "4":
                    xbmc.executebuiltin('Weather.LocationSet(4)')
                elif out_string == "5":
                    xbmc.executebuiltin('Weather.LocationSet(5)')
                elif out_string == "6":
                    xbmc.executebuiltin('Weather.LocationSet(6)')
                elif out_string == "7":
                    xbmc.executebuiltin('Weather.LocationSet(7)')
                elif out_string == "8":
                    xbmc.executebuiltin('Weather.LocationSet(8)')
                elif out_string == "9":
                    xbmc.executebuiltin('Weather.LocationSet(9)')
                elif out_string == "10":
                    xbmc.executebuiltin('Weather.LocationSet(10)')
                elif out_string == "edit":
                    WeatherPlugin = xbmc.getInfoLabel('Weather.Plugin')
                    if WeatherPlugin:
                        xbmc.executebuiltin('SetProperty(Weather_Addon_Settings_Edit_Locations,True,home)')
                        xbmc.executebuiltin('Addon.OpenSettings('+WeatherPlugin+')')
            
            if setting == "Kodi_Videos_Default_Select_Action":
                
                if out_string != "":
                    import simplejson
                    jsonQuery = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Settings.SetSettingValue", "params": {"setting":"myvideos.selectaction","value":'+out_string+'}, "id": 1}')
                    jsonQuery = unicode(jsonQuery, 'utf-8', errors='ignore') if sys.version_info.major == 2 else jsonQuery# Python 2/3
                    jsonQuery = simplejson.loads(jsonQuery)

# -*- coding: utf-8 -*-

import xbmc
import sys
if sys.version_info.major == 2:# Python 2
    import urllib
else:
    import urllib.parse

try:
    language_string = ' '+sys.argv[3] if sys.argv[3] else ''
    year_string     = ' '+sys.argv[2] if sys.argv[2] else ''
    
    search_string = sys.argv[1] + ' Trailer' + language_string + year_string
    
    search_string = urllib.quote_plus(search_string) if sys.version_info.major == 2 else urllib.parse.quote_plus(search_string)# Python 2/3
    
    xbmc.executebuiltin('ActivateWindow(Videos,"plugin://plugin.video.youtube/kodion/search/query/?q='+search_string+'",return)')
    
except:
    pass

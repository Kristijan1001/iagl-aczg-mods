# -*- coding: utf-8 -*-

import xbmc

args = sys.argv
for arg in args:
    try:
        params[arg.split("=")[0].lower()] = "=".join(arg.split("=")[1:]).strip()
    except:
        params = {}
    pass

verticalshift = 0.00
zoom          = 1.00

jsonQuery = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Player.SetViewMode", "params":{"viewmode": {"verticalshift":'+str(verticalshift)+', "zoom":'+str(zoom)+', "pixelratio":1.00}}, "id":1}')

jsonQuery = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Player.SetViewMode", "params":{"viewmode": "normal"}, "id":1}')

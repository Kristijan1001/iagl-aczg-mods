# -*- coding: utf-8 -*-

import xbmc

# negative value means delayed audio
audiodelay = 0.0

jsonQuery = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Player.SetAudioDelay", "params":{"playerid":1, "offset":'+str(audiodelay)+'}, "id":1}')

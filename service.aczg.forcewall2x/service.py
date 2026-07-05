# -*- coding: utf-8 -*-
#
# ACZG Force Wall 2X
# Re-asserts a chosen view in the Videos window every time the folder path
# changes, so Kodi's per-path view memory can't reset it.
# The view is configurable in this add-on's settings (default: Wall 2X / 500).

import xbmc
import xbmcgui
import xbmcaddon

VIDEO_WINDOW_ID = 10025      # WINDOW_VIDEO_NAV (the "Videos" window, where IAGL browses)
DEFAULT_VIEW_ID = 500        # Wall 2X

addon = xbmcaddon.Addon()
monitor = xbmc.Monitor()

last_key = None
last_view = None


def get_config():
    try:
        enabled = addon.getSettingBool('enabled')
    except Exception:
        enabled = True
    try:
        view_id = addon.getSettingInt('view_id')
    except Exception:
        view_id = DEFAULT_VIEW_ID
    if not view_id:
        view_id = DEFAULT_VIEW_ID
    return enabled, view_id


while not monitor.abortRequested():
    try:
        enabled, view_id = get_config()

        # If the target view changed in settings, re-apply on next folder.
        if view_id != last_view:
            last_view = view_id
            last_key = None

        if enabled and xbmcgui.getCurrentWindowId() == VIDEO_WINDOW_ID:
            path = xbmc.getInfoLabel('Container.FolderPath')
            num = xbmc.getInfoLabel('Container.NumItems')
            # Act once per folder, only after the list has populated.
            if path and num not in ('', '0') and path != last_key:
                xbmc.executebuiltin('Container.SetViewMode(%d)' % view_id)
                last_key = path
        else:
            # Left the Videos window (or disabled); allow re-applying on return.
            last_key = None
    except Exception:
        pass

    if monitor.waitForAbort(0.3):
        break

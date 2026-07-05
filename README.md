# Kodi mods — IAGL (aria2) + Confluence ZEITGEIST skin + force-view service

Personal Kodi 21 (Omega) setup with custom modifications. Three components:

| Folder | What it is |
| --- | --- |
| [`plugin.program.iagl/`](plugin.program.iagl) | Internet Archive Game Launcher **v4.0.6, modified** — rewritten downloader backend using aria2. |
| [`service.aczg.forcewall2x/`](service.aczg.forcewall2x) | Small **new** service add-on that locks the Videos window to a chosen view. |
| [`skin.aczg/`](skin.aczg) | Confluence **ZEITGEIST** skin, **modified** (labels under covers, IAGL home button, forced Wall 2X, sidebar add-on-settings button). |

---

## 1. IAGL — aria2 download backend (the big one)

Stock IAGL splits each file into 2 MB byte-range chunks, downloads them with a thread pool, and stitches them together **with no integrity check**. On large files (e.g. 5 GB PS2 CHDs) a single dropped/short chunk gets silently stitched in, producing a corrupt file that fails to load (`chd_open ... decompression error`).

This fork replaces that with **aria2c** as the download engine:

- **Resumable** downloads with automatic retry (`--max-tries`, `--continue`).
- **Size verification** — if the finished file doesn't match the server's `Content-Length`, it is deleted and reported as a failure instead of kept.
- Proper redirect handling and **archive.org login cookies** forwarded to aria2 (`--header=Cookie:`) for restricted items.
- Kodi progress dialog (name / size / speed) and working **Cancel**.
- **Automatic fallback** to the original chunk downloader if `aria2c.exe` is ever missing.

Changed files:
- `resources/lib/download.py` — new `get_aria2_path()` and `download_with_aria2()`; the per-file loop calls aria2 first and only falls back to the old path if the binary is absent.
- `resources/settings.xml` — Download Threads slider maximum raised from **12 → 100** (note: aria2 caps at 16 connections/server; the value maps to aria2 connections).
- `resources/bin/aria2c.exe` — bundled aria2 **1.37.0** (win64).

> Note: aria2 is GPLv2; see https://github.com/aria2/aria2

## 2. service.aczg.forcewall2x

Kodi remembers a view per folder, so IAGL's view kept resetting when moving between categories. This background service re-applies a chosen view in the Videos window (id 10025) on every folder change.

- Configurable via **Settings → Add-ons → My add-ons → Services → ACZG Force Wall 2X → Configure**.
- View dropdown uses the skin's real view IDs (Wall 2X = 500 default, plus Wall 3X/4X/5X, Fanart, List, Modern, Seasons, Episodes) and an on/off toggle.

## 3. skin.aczg (Confluence ZEITGEIST) changes

- `xml/_ViewsFileMode_walls.xml` — **titles always shown under the cover in Wall 2X**, both the focused tile and unfocused tiles (stock hid them on poster art).
- `xml/Home.xml` — the home-menu **"Favourites" button converted to "IAGL"** (label + games icon), launching the add-on via `RunAddon(plugin.program.iagl)`.
- `xml/MyVideoNav.xml` — `<onload>Container.SetViewMode(500)</onload>` to force Wall 2X on window entry, and an **"Addon settings"** button added to the sidebar (visible while browsing a plugin, opens the current add-on's settings).

---

## Install

Copy each folder into your Kodi `addons` directory (portable install shown):

```
…\Kodi\portable_data\addons\plugin.program.iagl
…\Kodi\portable_data\addons\service.aczg.forcewall2x
…\Kodi\portable_data\addons\skin.aczg
```

Restart Kodi. Enable **ACZG Force Wall 2X** under Services if it isn't auto-enabled. Select the **Confluence ZEITGEIST** skin.

## Credits / upstreams

- **IAGL** — Zach Morris — https://github.com/zach-morris/plugin.program.iagl (GPL)
- **aria2** — https://github.com/aria2/aria2 (GPLv2)
- **Confluence ZEITGEIST** skin — original authors of the ACZG skin

All original licenses are retained in the respective folders. These are personal modifications shared as-is, with no warranty.

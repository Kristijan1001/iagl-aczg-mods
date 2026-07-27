# -*- coding: utf-8 -*-
# Minerva Archive integration for IAGL.
# Browses minerva-archive.org and plays games THROUGH IAGL's own pipeline
# (download folder, if_game_exists, extraction, launcher, history, favorites,
# covers) by mapping each Minerva system to the matching IAGL game-list.
# Only the download engine is swapped: libtorrent (via the system-Python worker).
import os, re, html, sys, sqlite3, subprocess, shutil, json, hashlib
from pathlib import Path
import urllib.request, urllib.parse
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs

SITE = "https://minerva-archive.org"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
ARCHIVE_EXT = ('.zip', '.7z')
ARCADE_COLLECTIONS = ('FinalBurn Neo', 'MAME')
MAME_SNAP_BASE = "https://raw.githubusercontent.com/AntoPISA/MAME_SnapTitles/main/snap/"

COLLECTIONS = [
    ("No-Intro", "/browse/No-Intro/"),
    ("Redump", "/browse/Redump/"),
    ("MAME - ROMs (merged)", "/browse/MAME/ROMs (merged)/"),
    ("FinalBurn Neo", "/browse/FinalBurn Neo/"),
]

_PY_CANDIDATES = [
    r"C:\Users\Kristijan1001\AppData\Local\Programs\Python\Python313\python.exe",
]

# Minerva system (normalized) -> IAGL game-list label (normalized) for cases
# that don't substring-match automatically.
_ALIASES = {
    'segamegadrivegenesis': 'segagenesis',
    'segamegadrive': 'segagenesis',
    'nintendonintendoentertainmentsystem': 'nintendoentertainmentsystem',
    'segamastersystemmarkiii': 'segamastersystem',
    'nintendofamilycomputerdisksystem': 'nintendofamicomdisksystem',
}


def _norm(s):
    return re.sub(r'[^a-z0-9]', '', (s or '').lower())


class minerva(object):
    def __init__(self, config=None, cm=None, db=None, pp=None, ln=None, plugin=None):
        self.config = config
        self.cm = cm
        self.db = db
        self.pp = pp
        self.ln = ln
        self.plugin = plugin
        self.addon = xbmcaddon.Addon()
        self.addon_path = xbmcvfs.translatePath(self.addon.getAddonInfo('path'))
        self.worker = os.path.join(self.addon_path, 'resources', 'lib', 'minerva_worker.py')
        self.iagl_db = str(self.config.files.get('db'))
        self.data_dir = os.path.dirname(self.iagl_db)
        self._labels = None
        self._mame_map = None
        self._base_cache = {}

    # ---------- system -> IAGL game-list mapping ----------
    def _gl_labels(self):
        if self._labels is None:
            self._labels = []
            try:
                con = sqlite3.connect(self.iagl_db)
                self._labels = [r[0] for r in con.execute("SELECT label FROM game_list") if r[0]]
                con.close()
            except Exception as exc:
                xbmc.log(msg='IAGL: minerva label load error %s' % exc, level=xbmc.LOGERROR)
        return self._labels

    def _map_system(self, system):
        target = _norm(system)
        nlabels = {}
        for label in self._gl_labels():
            nl = _norm(label)
            if nl and nl not in nlabels:
                nlabels[nl] = label
        if target in _ALIASES and _ALIASES[target] in nlabels:
            return nlabels[_ALIASES[target]]
        if target in nlabels:
            return nlabels[target]
        best, best_len = None, 0
        for nl, label in nlabels.items():
            if (nl in target or target in nl) and len(nl) > best_len:
                best, best_len = label, len(nl)
        return best

    def _sample_uid(self, label):
        try:
            con = sqlite3.connect(self.iagl_db)
            row = con.execute("SELECT uid FROM games WHERE game_list=? LIMIT 1", (label,)).fetchone()
            con.close()
            return row[0] if row else None
        except Exception:
            return None

    def _effective_system(self, full_path):
        """Resolve the IAGL-relevant system name. Arcade collections use one game-list."""
        parts = full_path.strip("/").lstrip(".").strip("/").split("/")
        collection = parts[0] if parts else ''
        if collection == 'MAME':
            return 'MAME'
        if collection == 'FinalBurn Neo':
            return 'FBNeo - Arcade' if (len(parts) > 1 and parts[1] == 'arcade') else (parts[1] if len(parts) > 1 else '')
        return parts[-2] if len(parts) >= 2 else ''

    def _template(self, system):
        label = self._map_system(system)
        if not label:
            return None, None
        uid = self._sample_uid(label)
        if not uid:
            return label, None
        try:
            tg = self.db.get_game_from_id(game_id=uid, game_title_setting=self.cm.get_setting('game_title_setting'))
            return label, tg
        except Exception as exc:
            xbmc.log(msg='IAGL: minerva template error %s' % exc, level=xbmc.LOGERROR)
            return label, None

    def _resolve_launch(self, tg):
        lp = next(iter([x for x in [tg.get('user_game_external_launch_command'),
                                    tg.get('user_global_external_launch_command')] if isinstance(x, str)]), None)
        if not lp and isinstance(tg.get('default_global_external_launch_command'), str):
            try:
                if self.cm.get_setting('user_launch_os') in self.config.defaults.get('config_available_systems'):
                    default_cmd = next(iter(self.db.query_db(self.db.get_query(
                        'get_retroarch_default_commands', user_launch_os=self.cm.get_setting('user_launch_os'),
                        applaunch='0', appause='0'), return_as='dict')), None)
                    cores = self.cm.get_installed_ra_cores(ra_default_command=default_cmd)
                    match = next(iter([x for x in cores if isinstance(x, dict)
                                       and x.get('core_stem') == tg.get('default_global_external_launch_command')]), None)
                    if match and isinstance(match.get('command'), str):
                        lp = match.get('command')
            except Exception as exc:
                xbmc.log(msg='IAGL: minerva launch resolve error %s' % exc, level=xbmc.LOGERROR)
        return lp

    # ---------- MAME short-name -> title map (display only) ----------
    def _mame_titles(self):
        if self._mame_map is None:
            self._mame_map = {}
            cache = os.path.join(self.data_dir, 'minerva_mame_titles.json')
            try:
                if os.path.exists(cache):
                    self._mame_map = json.load(open(cache, encoding='utf-8'))
            except Exception:
                self._mame_map = {}
            if not self._mame_map:
                try:
                    url = "https://raw.githubusercontent.com/libretro/libretro-database/master/metadat/mame/MAME.dat"
                    text = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60).read().decode('utf-8', 'replace')
                    for m in re.finditer(r'game \(\s*\n\s*name "([^"]+)".*?rom \( name ([^\s]+?)\.zip', text, re.S):
                        self._mame_map[m.group(2)] = m.group(1)
                    json.dump(self._mame_map, open(cache, 'w', encoding='utf-8'))
                except Exception as exc:
                    xbmc.log(msg='IAGL: minerva MAME titles error %s' % exc, level=xbmc.LOGERROR)
        return self._mame_map

    # ---------- covers: use IAGL's own libretro base per system ----------
    def _art_base(self, system):
        if system in self._base_cache:
            return self._base_cache[system]
        base = None
        label = self._map_system(system)
        if label:
            try:
                con = sqlite3.connect(self.iagl_db)
                row = con.execute("SELECT p.url FROM games g JOIN paths p ON p.path=g.art_box_path "
                                  "WHERE g.game_list=? AND g.art_box_path IS NOT NULL AND g.art_box IS NOT NULL LIMIT 1",
                                  (label,)).fetchone()
                con.close()
                if row and row[0]:
                    base = row[0]
            except Exception:
                base = None
        if not base:
            base = "https://thumbnails.libretro.com/%s/Named_Boxarts/" % urllib.parse.quote(system)
        self._base_cache[system] = base
        return base

    def _cover(self, system, name):
        return self._art_base(system) + urllib.parse.quote(name) + ".png"

    def _mame_art(self, short):
        """Complete per-game MAME art (snapshots) keyed by set short-name."""
        return MAME_SNAP_BASE + urllib.parse.quote(short) + ".png"

    # ---------- browsing ----------
    def _find_python(self):
        for p in _PY_CANDIDATES:
            if os.path.exists(p):
                return p
        for name in ('python.exe', 'python3.exe', 'py.exe'):
            w = shutil.which(name)
            if w:
                return w
        return None

    def _url(self, route, p):
        return self.plugin.url_for_path(route) + '?' + urllib.parse.urlencode({'p': p})

    def _arg_p(self):
        for src in (2, 0):
            try:
                q = urllib.parse.parse_qs(sys.argv[2].lstrip('?') if src == 2
                                         else urllib.parse.urlsplit(sys.argv[0]).query)
                if q.get('p'):
                    return q['p'][0]
            except Exception:
                pass
        return ''

    def _fetch(self, browse_path):
        url = SITE + urllib.parse.quote(browse_path)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", "replace")

    def _parse(self, browse_path):
        doc = self._fetch(browse_path)
        folders, games, seen = [], [], set()
        bp = urllib.parse.unquote(browse_path)
        for m in re.finditer(r'href="(/browse/[^"]+/)"', doc):
            href = urllib.parse.unquote(html.unescape(m.group(1)))
            if href.startswith(bp) and href != bp:
                rest = href[len(bp):].strip("/")
                if rest and "/" not in rest and rest not in seen:
                    seen.add(rest)
                    folders.append((rest, href))
        for m in re.finditer(r'href="(/rom\?name=[^"]+)"', doc):
            href = html.unescape(m.group(1))
            full_path = urllib.parse.unquote(href.split("name=", 1)[1])
            fname = full_path.split("/")[-1]
            stem = re.sub(r"\.(zip|7z|chd|iso|sfc|smc|nes|md|bin|cue)$", "", fname, flags=re.I)
            games.append((stem, full_path))
        return folders, games

    def root_listitem(self):
        li = xbmcgui.ListItem(label="Minerva Archive")
        li.setArt({'icon': 'DefaultAddonProgram.png', 'thumb': 'DefaultAddonProgram.png'})
        li.setInfo('game', {'title': 'Minerva Archive'})
        return li

    def clear_cache_listitem(self):
        li = xbmcgui.ListItem(label="Clear Downloads & History")
        li.setArt({'icon': 'DefaultAddonService.png', 'thumb': 'DefaultAddonService.png'})
        li.setInfo('game', {'title': 'Clear Downloads & History'})
        return li

    def list_collections(self):
        h = self.plugin.handle
        xbmcplugin.setContent(h, 'games')
        for label, path in COLLECTIONS:
            li = xbmcgui.ListItem(label=label)
            li.setArt({'icon': 'DefaultFolder.png'})
            xbmcplugin.addDirectoryItem(h, self._url('/minerva_browse', path), li, isFolder=True)
        xbmcplugin.endOfDirectory(h)

    def list_dir(self):
        h = self.plugin.handle
        browse_path = self._arg_p()
        try:
            folders, games = self._parse(browse_path)
        except Exception as exc:
            xbmc.log(msg='IAGL: minerva parse error: %s' % exc, level=xbmc.LOGERROR)
            xbmcgui.Dialog().notification("Minerva", "Load failed", xbmcgui.NOTIFICATION_ERROR)
            xbmcplugin.endOfDirectory(h, succeeded=False)
            return
        xbmcplugin.setContent(h, 'games')
        eff = self._effective_system(games[0][1]) if games else ''
        is_mame = eff == 'MAME'
        mame_map = self._mame_titles() if is_mame else {}
        label = self._map_system(eff) if eff else None
        template_uid = self._sample_uid(label) if label else None
        for name, path in folders:
            li = xbmcgui.ListItem(label=name)
            li.setArt({'icon': 'DefaultFolder.png'})
            xbmcplugin.addDirectoryItem(h, self._url('/minerva_browse', path), li, isFolder=True)
        for stem, full_path in games:
            display = mame_map.get(stem, stem) if is_mame else stem
            li = xbmcgui.ListItem(label=display)
            cov = (self._mame_art(stem) if is_mame else None) or self._cover(eff, stem)
            li.setArt({'thumb': cov, 'poster': cov, 'icon': cov})
            li.setInfo('game', {'title': display, 'platform': eff})
            play_url = self._url('/minerva_play', full_path)
            if template_uid is not None:
                try:
                    self.cm.add_context_menu(li=li, ip='/play_game/%s' % template_uid, type_in='game')
                except Exception:
                    pass
            li.addContextMenuItems([("Download only", "RunPlugin(%s)" % self._url('/minerva_download', full_path))])
            xbmcplugin.addDirectoryItem(h, play_url, li, isFolder=False)
        xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        xbmcplugin.endOfDirectory(h)

    # ---------- download + play ----------
    def _primary_file(self, dl_path, file_name):
        stem = os.path.splitext(file_name)[0]
        cands = []
        if os.path.isdir(dl_path):
            for f in os.listdir(dl_path):
                if os.path.splitext(f)[0] == stem:
                    cands.append(os.path.join(dl_path, f))
        non_arch = [c for c in cands if os.path.splitext(c)[1].lower() not in ARCHIVE_EXT]
        if non_arch:
            return non_arch[0]
        return cands[0] if cands else None

    def _run_worker(self, full_path, dl_path, name):
        py = self._find_python()
        if not py:
            xbmcgui.Dialog().ok("Minerva", "No system Python with libtorrent + apsw found.\n"
                                           "Edit resources/lib/minerva.py _PY_CANDIDATES.")
            return False
        cmd = [py, self.worker, "single", full_path, "-o", dl_path]
        si, flags = None, 0
        try:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            flags = 0x08000000
        except Exception:
            si = None
        dp = xbmcgui.DialogProgress()
        dp.create("Minerva - downloading", name)
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    startupinfo=si, creationflags=flags, universal_newlines=True, bufsize=1)
        except Exception as exc:
            dp.close()
            xbmcgui.Dialog().notification("Minerva", "Worker failed: %s" % exc, xbmcgui.NOTIFICATION_ERROR)
            return False
        total, ok, err = 0, False, None
        for line in proc.stdout:
            line = line.strip()
            if line.startswith("@@SIZE"):
                try:
                    total = int(line.split()[1])
                except Exception:
                    total = 0
            elif line.startswith("@@PROGRESS"):
                pr = line.split()
                try:
                    pct, rate, peers = float(pr[1]), int(pr[2]), int(pr[3])
                except Exception:
                    pct, rate, peers = 0, 0, 0
                if total:
                    msg = "%s[CR]%.1f / %.1f MB   %d KB/s   %d peers" % (
                        name, pct / 100.0 * total / 1048576.0, total / 1048576.0, rate // 1024, peers)
                else:
                    msg = "%s[CR]%.1f%%   %d KB/s   %d peers" % (name, pct, rate // 1024, peers)
                dp.update(int(pct), msg)
            elif line.startswith("@@DONE"):
                ok = True
            elif line.startswith("@@ERROR"):
                err = line[7:].strip()
            if dp.iscanceled():
                try:
                    proc.kill()
                except Exception:
                    pass
                dp.close()
                xbmcgui.Dialog().notification("Minerva", "Cancelled", xbmcgui.NOTIFICATION_INFO)
                return False
        proc.wait()
        dp.close()
        if not ok:
            xbmcgui.Dialog().notification("Minerva", "Download failed: %s" % (err or "unknown"), xbmcgui.NOTIFICATION_ERROR, 6000)
        return ok

    def _prepare(self, full_path):
        """Map, compute IAGL dl_path, download if needed. Returns (dl_path, file_name, template, collection) or None."""
        parts = full_path.strip("/").lstrip(".").strip("/").split("/")
        collection = parts[0] if parts else ''
        system = self._effective_system(full_path)
        file_name = parts[-1]
        label, tg = self._template(system)
        game_list_id = (tg.get('game_list_id') if isinstance(tg, dict) else None) or label or system
        dl_path = xbmcvfs.translatePath(self.cm.get_game_dl_path(
            path_in=self.cm.get_setting('default_dl_path'), game_list_id=game_list_id,
            organize_path=self.cm.get_setting('organize_temp_dl')))
        try:
            os.makedirs(dl_path, exist_ok=True)
        except Exception:
            pass
        existing = self._primary_file(dl_path, file_name)
        if_exists = str(self.cm.get_setting('if_game_exists'))
        redownload = True
        if existing:
            if if_exists == '0':
                redownload = False
            elif if_exists == '2':
                redownload = xbmcgui.Dialog().yesno("Minerva", "%s already downloaded. Re-download?" % file_name)
        if redownload:
            if not self._run_worker(full_path, dl_path, file_name):
                return None
        return dl_path, file_name, tg, collection

    def download(self):
        prep = self._prepare(self._arg_p())
        if prep:
            xbmcgui.Dialog().notification("Minerva", "Downloaded: %s" % prep[1], xbmcgui.NOTIFICATION_INFO, 4000)

    def play(self, full_path=None):
        full_path = full_path or self._arg_p()
        system = self._effective_system(full_path)
        prep = self._prepare(full_path)
        if not prep:
            return
        dl_path, file_name, tg, collection = prep
        primary = self._primary_file(dl_path, file_name)
        if not primary or not os.path.exists(primary):
            xbmcgui.Dialog().notification("Minerva", "File not found after download", xbmcgui.NOTIFICATION_ERROR)
            return
        is_archive = os.path.splitext(primary)[1].lower() in ARCHIVE_EXT
        arcade = collection in ARCADE_COLLECTIONS
        process = 'unzip' if (is_archive and not arcade) else 'none'
        lp = tg.get('launch_parameters') if isinstance(tg, dict) else None
        try:
            dsize = os.path.getsize(primary)
        except Exception:
            dsize = 0
        rom_result = [{'dl_filepath': Path(primary), 'download_success': True, 'download_size': dsize}]
        self.pp.set_launch_parameters(launch_parameters=lp)
        self.pp.set_game_name(game_name=file_name)
        self.pp.set_rom(rom=rom_result)
        self.pp.set_process(process=process)
        processed = self.pp.process_games()
        if not (isinstance(processed, dict) and processed.get('process_success')):
            xbmcgui.Dialog().notification("Minerva", "Extract failed", xbmcgui.NOTIFICATION_ERROR)
            return
        # Disc images: prefer the .m3u/.cue/.gdi sheet so all tracks load.
        lf = processed.get('launch_file')
        if isinstance(lf, str) and os.path.splitext(lf)[1].lower() in ('.bin', '.iso', '.img'):
            folder = os.path.dirname(lf)
            try:
                files = os.listdir(folder)
                for ext in ('.m3u', '.cue', '.gdi'):
                    cands = sorted([f for f in files if f.lower().endswith(ext)])
                    if cands:
                        base = os.path.splitext(os.path.basename(lf))[0].split(' (Track')[0]
                        match = next((c for c in cands if c.startswith(base)), cands[0])
                        processed['launch_file'] = os.path.join(folder, match)
                        break
            except Exception:
                pass
        if not isinstance(tg, dict):
            xbmcgui.Dialog().notification("Minerva", "Downloaded (no IAGL game-list to launch this system)",
                                          xbmcgui.NOTIFICATION_INFO, 5000)
            return
        launch_process = self._resolve_launch(tg)
        if not launch_process:
            xbmcgui.Dialog().ok("Minerva", "Downloaded and extracted, but no launch command is set for the "
                                           "matching IAGL game-list. Configure that system's launch in IAGL to play.")
            return
        self.ln.set_launcher(launcher='external')
        self.ln.set_game_name(game_name=file_name)
        self.ln.set_appause(appause=next(iter([x for x in [tg.get('user_global_uses_apppause')] if isinstance(x, int)]), 0))
        self.ln.set_applaunch(applaunch=next(iter([x for x in [tg.get('user_global_uses_applaunch')] if isinstance(x, int)]), 0))
        self.ln.set_rom(rom=processed)
        self.ln.set_launch_parameters(launch_parameters={'launch_process': launch_process, 'netplay': None})
        launched = None
        try:
            launched = self.ln.launcher.launch()
        except Exception as exc:
            xbmc.log(msg='IAGL: minerva launch error %s' % exc, level=xbmc.LOGERROR)
            xbmcgui.Dialog().notification("Minerva", "Launch error", xbmcgui.NOTIFICATION_ERROR)
        uid = self._register_game(full_path, file_name, system, dsize)
        if uid and isinstance(launched, dict) and launched.get('launch_success'):
            try:
                self.db.add_history(game_id=uid)
                self.db.update_pc_and_cp(game_id=uid)
            except Exception as exc:
                xbmc.log(msg='IAGL: minerva history error %s' % exc, level=xbmc.LOGERROR)

    # ---------- native DB registration (history / favorites / covers) ----------
    def _register_game(self, full_path, name, system, size):
        label = self._map_system(system)
        if not label:
            return None
        tuid = self._sample_uid(label)
        if not tuid:
            return None
        uid = hashlib.md5(full_path.encode('utf-8')).hexdigest()
        stem = os.path.splitext(name)[0]                       # libretro cover filename base
        if system == 'MAME':
            title = self._mame_titles().get(stem, stem)
        else:
            title = stem
        rom = json.dumps([{"url": "minerva://" + full_path, "size": size or 0, "filename": name}])
        try:
            con = sqlite3.connect(self.iagl_db)
            if system == 'MAME':
                # complete MAME snapshot source (keyed by set short-name)
                con.execute("INSERT OR IGNORE INTO paths (path,url) VALUES (900002,?)", (MAME_SNAP_BASE,))
                bpath, box, spath, snap = 900002, stem + '.png', 900002, stem + '.png'
            else:
                tr = con.execute("SELECT art_box_path,art_snapshot_path FROM games WHERE uid=?", (tuid,)).fetchone()
                bpath = tr[0] if tr else None
                spath = tr[1] if tr else None
                box = (stem + '.png') if bpath else None        # resolves via IAGL: base + name.png
                snap = (stem + '.png') if spath else None
            con.execute(
                "INSERT OR REPLACE INTO games "
                "(uid,originaltitle,name_clean,name_search,game_list,system,rom,size,launch_parameters,"
                "art_box_path,art_box,art_snapshot_path,art_snapshot,is_1g1r,playcount) "
                "SELECT ?,?,?,?,game_list,system,?,?,launch_parameters,?,?,?,?,0,0 "
                "FROM games WHERE uid=?",
                (uid, title, title, title.lower(), rom, size or 0, bpath, box, spath, snap, tuid))
            con.commit()
            con.close()
            return uid
        except Exception as exc:
            xbmc.log(msg='IAGL: minerva register error %s' % exc, level=xbmc.LOGERROR)
            return None

    def minerva_rom_path(self, uid):
        try:
            con = sqlite3.connect(self.iagl_db)
            row = con.execute("SELECT rom FROM games WHERE uid=?", (uid,)).fetchone()
            con.close()
            if row and row[0]:
                data = json.loads(row[0])
                u = data[0].get('url') if data else None
                if isinstance(u, str) and u.startswith('minerva://'):
                    return u[len('minerva://'):]
        except Exception:
            pass
        return None

    # ---------- clear cache ----------
    def clear_cache(self):
        if not xbmcgui.Dialog().yesno("IAGL", "Delete ALL downloaded games (archive + Minerva) and clear play history?"):
            return
        removed = 0
        bases = []
        try:
            bases.append(self.cm.get_setting('default_dl_path'))
        except Exception:
            pass
        try:
            bases.append(str(self.config.paths.get('default_temp_dl')))
        except Exception:
            pass
        for base in bases:
            if not base:
                continue
            base = xbmcvfs.translatePath(base)
            if os.path.isdir(base):
                for entry in os.listdir(base):
                    p = os.path.join(base, entry)
                    try:
                        if os.path.isdir(p):
                            shutil.rmtree(p, ignore_errors=True)
                        else:
                            os.remove(p)
                        removed += 1
                    except Exception:
                        pass
        try:
            con = sqlite3.connect(self.iagl_db)
            con.execute("DELETE FROM history")
            con.commit()
            con.close()
        except Exception as exc:
            xbmc.log(msg='IAGL: minerva clear history error %s' % exc, level=xbmc.LOGERROR)
        xbmcgui.Dialog().notification("IAGL", "Cleared %d items + history" % removed, xbmcgui.NOTIFICATION_INFO, 4000)
        xbmc.executebuiltin('Container.Refresh')

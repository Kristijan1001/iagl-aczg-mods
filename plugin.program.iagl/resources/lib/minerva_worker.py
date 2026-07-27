r"""
Minerva worker (called by the Kodi plugin via system Python).
Modes:
  lookup  "<full_path>"            -> print JSON metadata for one game
  single  "<full_path>" -o <dir>   -> download ONE game via libtorrent, verify, move
  section "<browse_url>" -o <dir>  -> download a whole console (from the original script)
Progress is emitted as machine-readable lines:
  @@PROGRESS <pct> <rate_bytes_s> <peers>
  @@DONE <abs_path>
  @@ERROR <message>
"""
import sys, os, re, json, time, shutil, hashlib, http.client, threading
from pathlib import Path
from urllib.parse import quote, unquote, urlparse
from urllib.request import Request, urlopen

BASE = "https://minerva-archive.org"
DB_URL = BASE + "/assets/hashes.db"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
CHUNK = 64 * 1024
TRACKERS = [
    "udp://tracker.opentrackr.org:1337/announce","udp://open.stealth.si:80/announce",
    "udp://exodus.desync.com:6969/announce","udp://bt1.archive.org:6969/announce",
    "udp://opentracker.io:6969/announce","udp://explodie.org:6969/announce",
    "udp://tracker.torrent.eu.org:451/announce","udp://open.demonii.com:1337/announce",
]

import apsw
import libtorrent as lt


class _RemoteFile:
    def __init__(self, url):
        p = urlparse(url); self.host, self.path = p.netloc, p.path
        self.lock = threading.Lock(); self.conn = None; self.cache = {}
        self.size = self._size()
    def _request(self, method, headers):
        for attempt in range(3):
            try:
                if self.conn is None:
                    self.conn = http.client.HTTPSConnection(self.host, timeout=60)
                self.conn.request(method, self.path, headers={**UA, **headers})
                return self.conn.getresponse()
            except Exception:
                self.conn = None
                if attempt == 2: raise
    def _size(self):
        r = self._request("HEAD", {}); r.read(); return int(r.headers["Content-Length"])
    def _chunk(self, idx):
        if idx not in self.cache:
            start = idx * CHUNK; end = min(start + CHUNK, self.size) - 1
            r = self._request("GET", {"Range": f"bytes={start}-{end}"}); self.cache[idx] = r.read()
        return self.cache[idx]
    def xRead(self, amount, offset):
        with self.lock:
            out = b""
            while amount > 0:
                idx, within = divmod(offset, CHUNK)
                piece = self._chunk(idx)[within:within + amount]
                out += piece; offset += len(piece); amount -= len(piece)
            return out
    def xFileSize(self): return self.size
    def xClose(self):
        if self.conn: self.conn.close()
    def xLock(self, l): pass
    def xUnlock(self, l): pass
    def xCheckReservedLock(self): return False
    def xSync(self, f): pass
    def xSectorSize(self): return 4096
    def xDeviceCharacteristics(self): return 0
    def xFileControl(self, op, ptr): return False
    def xWrite(self, d, o): raise apsw.ReadOnlyError()
    def xTruncate(self, n): raise apsw.ReadOnlyError()


class HttpVFS(apsw.VFS):
    def __init__(self): super().__init__("http", base="")
    def xOpen(self, name, flags):
        url = name.filename() if hasattr(name, "filename") else str(name)
        flags[1] |= apsw.SQLITE_OPEN_READONLY; return _RemoteFile(url)
    def xAccess(self, pathname, flags):
        return flags == apsw.SQLITE_ACCESS_EXISTS and pathname.endswith(".db")
    def xFullPathname(self, name): return name
    def xDelete(self, name, syncdir): pass


_VFS = HttpVFS()


def _conn():
    return apsw.Connection(DB_URL, vfs="http",
                           flags=apsw.SQLITE_OPEN_READONLY | apsw.SQLITE_OPEN_URI)

def lookup_one(full_path):
    c = _conn()
    row = c.cursor().execute(
        "SELECT file_name,size,md5,sha1,torrents,so_id FROM files WHERE full_path = ?",
        (full_path,)).fetchone()
    c.close()
    if not row: return None
    return dict(zip(["file_name","size","md5","sha1","torrents","so_id"], row))

def safe(n): return re.sub(r'[<>:"/\\|?*]', "_", n).strip()

def _md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def download_single(full_path, out_base):
    meta = lookup_one(full_path)
    if not meta or not meta.get("torrents"):
        print("@@ERROR no torrent/source for that game", flush=True); return 1
    print("@@SIZE %d" % (meta.get("size") or 0), flush=True)
    # out_base is the exact folder to place the file in (IAGL already organized it)
    out_dir = Path(out_base); out_dir.mkdir(parents=True, exist_ok=True)
    final = out_dir / meta["file_name"]
    if final.exists() and meta.get("md5") and _md5(final) == meta["md5"]:
        print("@@DONE " + str(final), flush=True); return 0

    turl = f"{BASE}/assets/{quote(meta['torrents'])}"
    tdata = urlopen(Request(turl, headers=UA), timeout=120).read()
    info = lt.torrent_info(lt.bdecode(tdata))
    ses = lt.session({"listen_interfaces": "0.0.0.0:6881", "enable_dht": True, "alert_mask": 0})
    save_root = Path(out_base) / ".minerva_tmp"; save_root.mkdir(parents=True, exist_ok=True)
    h = ses.add_torrent({"ti": info, "save_path": str(save_root)})
    for tr in TRACKERS: h.add_tracker({"url": tr})
    idx = int(meta["so_id"])
    nfiles = info.files().num_files()
    prios = [0] * nfiles
    if 0 <= idx < nfiles: prios[idx] = 7
    h.prioritize_files(prios)
    orig_rel = info.files().file_path(idx)
    flat_name = safe(meta["file_name"])
    try:
        h.rename_file(idx, flat_name)   # flatten to avoid Windows 260-char path limit
    except Exception:
        pass
    fsz = info.files().file_size(idx)
    print("@@SIZE %d" % fsz, flush=True)          # accurate size of the selected file
    stall = None
    while True:
        s = h.status()
        fp = h.file_progress()
        done = fp[idx] if idx < len(fp) else 0
        pct = (done * 100.0 / fsz) if fsz else 0.0  # progress of the wanted file, not the whole torrent
        print("@@PROGRESS %.1f %d %d" % (pct, int(s.download_rate), s.num_peers), flush=True)
        if fsz > 0 and done >= fsz:
            break
        if s.is_seeding or s.progress >= 1.0:
            break
        if s.download_rate == 0 and s.num_peers == 0:
            stall = stall or time.time()
            if time.time() - stall > 300:
                ses.remove_torrent(h); print("@@ERROR no seeders found (5 min)", flush=True); return 2
        else:
            stall = None
        time.sleep(1)
    ses.remove_torrent(h); del ses; time.sleep(1)
    src = save_root / flat_name
    if not src.exists():
        alt = save_root / orig_rel   # fallback if rename didn't apply
        src = alt if alt.exists() else src
    if not src.exists():
        print("@@ERROR downloaded file missing", flush=True); return 3
    if meta.get("md5"):
        got = _md5(src)
        if got != meta["md5"]:
            print(f"@@ERROR hash mismatch got {got} want {meta['md5']}", flush=True); return 4
    shutil.move(str(src), str(final))
    shutil.rmtree(save_root, ignore_errors=True)   # remove tmp incl. libtorrent .parts
    print("@@DONE " + str(final), flush=True); return 0


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "lookup":
        print(json.dumps(lookup_one(sys.argv[2]))); return 0
    if mode == "single":
        fp = sys.argv[2]
        out = "."
        if "-o" in sys.argv: out = sys.argv[sys.argv.index("-o") + 1]
        return download_single(fp, out)
    print("usage: lookup|single", file=sys.stderr); return 1

if __name__ == "__main__":
    sys.exit(main())

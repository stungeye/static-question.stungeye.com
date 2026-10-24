#!/usr/bin/env python3
"""Fetch the S5 decks of question.stungeye.com from the origin (bypassing Cloudflare) plus
every same-host asset they reference (src/href, CSS url(), @import), into site/.

Usage: python3 -I tools/crawl.py ids.sorted site extra_paths.txt
  extra_paths.txt: extra same-host paths to fetch (e.g. the whole /ui/ tree), one per line.
Writes crawl.log next to site/. Paths keep their on-server names; query strings are dropped
from saved filenames (static hosts ignore them, so the HTML needs no rewrite).
"""
import re, subprocess, sys, time
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote

HOST, ORIGIN = "question.stungeye.com", "159.203.24.194"
ids_file, site_dir, extra_file = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
log = open(site_dir.parent / "crawl.log", "w")

def fetch(path):
    """GET https://HOST<path> from the origin. Returns (status, bytes)."""
    out = subprocess.run(
        ["curl", "-s", "-g", "--resolve", f"{HOST}:443:{ORIGIN}", "-A", "ODM-archiver/1.0",
         "-w", "\n%{http_code}", f"https://{HOST}{path}"], capture_output=True)
    body, _, code = out.stdout.rpartition(b"\n")
    return int(code or 0), body

def save(path, body):
    rel = unquote(urlsplit(path).path).lstrip("/")
    dest = (site_dir / rel).resolve()
    assert str(dest).startswith(str(site_dir.resolve())), path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(body)
    return dest

REF = re.compile(rb'(?:src|href)\s*=\s*["\']([^"\']+)["\']', re.I)
CSSURL = re.compile(rb'url\(\s*["\']?([^"\')]+)["\']?\s*\)|@import\s+["\']([^"\']+)["\']', re.I)

def local_refs(base, body, css=False):
    found = []
    for m in (CSSURL if css else REF).finditer(body):
        raw = next(g for g in m.groups() if g).decode("utf-8", "replace").strip()
        if raw.startswith(("#", "mailto:", "javascript:", "data:")):
            continue
        u = urlsplit(urljoin(f"https://{HOST}{base}", raw))
        if u.netloc == HOST:
            found.append(u.path + (f"?{u.query}" if u.query else ""))
    if not css:  # inline style="" / <style> blocks
        for m in CSSURL.finditer(body):
            raw = next(g for g in m.groups() if g).decode("utf-8", "replace").strip()
            u = urlsplit(urljoin(f"https://{HOST}{base}", raw))
            if u.netloc == HOST and not raw.startswith("data:"):
                found.append(u.path)
    return found

queue, seen = [], set()
for i in open(ids_file).read().split():
    queue.append(f"/s5/show/{i}")
queue += [l.strip() for l in open(extra_file) if l.strip()]

while queue:
    p = queue.pop(0)
    key = urlsplit(p).path
    if key in seen:
        continue
    seen.add(key)
    code, body = fetch(p)
    log.write(f"{code} {p}\n")
    if code != 200:
        print(f"!! {code} {p}")
        continue
    is_deck = key.startswith("/s5/show/")
    dest = save(key + (".html" if is_deck else ""), body)
    if is_deck or dest.suffix in (".html", ".htm"):
        queue += local_refs(key, body)
    elif dest.suffix == ".css":
        queue += local_refs(key, body, css=True)
    time.sleep(0.05)

log.close()
print(f"fetched {len(seen)} paths")

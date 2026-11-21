"""Vorschau der Karriereseite als eigener, nie indexierter Cloudflare Worker (hwm-karriere-vorschau).

Wofür: Die Live-Seite geht per Commit auf GitHub Pages, und den Commit sperrt das Design-Tor, solange irgendeine Seite rot
ist. Arbeitet ein anderer Chat gerade an /websites/, kann Noah die Karriereseite trotzdem schon ansehen (21.11.2026).
Nimmt nur karriere/index.html und die Dateien, auf die sie (und ihre Stylesheets) verweisen, mit; noindex wie jede Vorschau.

Aufruf: /Users/noahs/CEO-GPT/.venv/bin/python firma/website/start-neu/karriere_vorschau.py
"""
import re
import shutil
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, "/Users/noahs/CEO-GPT/system/apps/kunden-vorschau")
import vorschau_deploy as vd  # noqa: E402

NAME = "hwm-karriere-vorschau"


def verweise(text, basis="/"):
    for m in re.finditer(r'''(?:src|href|data-src|poster|data-poster)=["'](/[^"'?#]+)''', text):
        yield m.group(1)
    for m in re.finditer(r'''url\(\s*["']?(/[^"')?#]+)''', text):
        yield m.group(1)
    for m in re.finditer(r'''["'\[](/static/[^"'\]\s?#]+)''', text):  # data-pool, JSON in Attributen
        yield m.group(1)


def bauen():
    ziel = Path(vd.BUILD) / NAME
    if ziel.exists():
        shutil.rmtree(ziel)
    ziel.mkdir(parents=True)
    html = (WURZEL / "karriere/index.html").read_text(encoding="utf-8")
    offen, gesehen = list(verweise(html)), set()
    while offen:
        pfad = offen.pop()
        if pfad in gesehen or pfad.endswith("/"):
            continue
        gesehen.add(pfad)
        q = WURZEL / pfad.lstrip("/")
        if not q.is_file():
            continue
        z = ziel / pfad.lstrip("/")
        z.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(q, z)
        if q.suffix in (".css", ".js"):
            offen += list(verweise(q.read_text(encoding="utf-8", errors="ignore")))
    s = re.sub(r'<meta name="robots" content="(?!noindex)[^"]*">', "", html)
    s = re.sub(r"(<head[^>]*>)", r"\1" + vd.META, s, count=1)
    (ziel / "index.html").write_text(s, encoding="utf-8")
    (ziel / "karriere").mkdir(exist_ok=True)
    (ziel / "karriere/index.html").write_text(s, encoding="utf-8")
    (ziel / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (ziel / "_headers").write_text("/*\n  X-Robots-Tag: noindex, nofollow\n", encoding="utf-8")
    toml = ziel.parent / f"{NAME}.toml"
    toml.write_text(f'name = "{NAME}"\ncompatibility_date = "2026-09-01"\n\n[assets]\ndirectory = "./{NAME}"\n'
                    f'not_found_handling = "404-page"\n', encoding="utf-8")
    n = sum(1 for _ in ziel.rglob("*") if _.is_file())
    print(f"📦 {n} Dateien → {ziel}")
    return toml, vd.titel(s)


if __name__ == "__main__":
    toml, soll = bauen()
    rc = vd.ausrollen(toml)
    if rc:
        sys.exit(rc)
    ok, ist = vd.live_gleich(NAME, soll)
    print(("✅ " if ok else "❌ ") + vd.url_von(NAME), "→", ist)
    sys.exit(0 if ok else 1)

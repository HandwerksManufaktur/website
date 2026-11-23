"""Bewegtes Bild (animiertes WebP) zu jedem Video der Live-Seiten — Rückfall, wenn das Handy Videos nicht selbst startet.

Noah, 24.11.2026: „videos laufen am handy immer noch nicht … schick es nicht noch mal rein, ohne dass du sichergestellt
hast, dass es mobil auch die Videos durchlaufen.“ Im Stromsparmodus und in manchen App-Browsern verweigert iOS jedes
Selbststarten (play() → NotAllowedError). Ein animiertes Bild läuft dort trotzdem. main.js legt es dann über das Video.

Je Video  foo.mp4  →  foo.anim.webp  daneben (360 px breit, 8 Bilder/s, höchstens 6 s, verlustbehaftet q 45).
Aufruf:  .venv/bin/python firma/website/start-neu/video_bilder.py [--neu]   (ohne --neu nur fehlende)
"""
import re, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

W = Path(__file__).resolve().parent.parent
AUSSCHLUSS = ('archiv', 'test-', 'start-neu', '/alt/', 'node_modules', 'neu-neu')
BREITE, FPS, MAX_S, Q = 360, 8, 6, 45


def quellen():
    out = set()
    for h in W.rglob('*.html'):
        if any(a in str(h) for a in AUSSCHLUSS):
            continue
        for tag in re.findall(r'<(?:video|source)[^>]*>', h.read_text(errors='ignore')):
            for p in re.findall(r'(?:data-src-mobil|data-src|src)="(/[^"?]+\.(?:mp4|webm))', tag):
                p = W / p.lstrip('/').replace('.webm', '.mp4')
                if p.exists():
                    out.add(p)
    return sorted(out)


def ziel(p):
    return p.with_name(p.stem + '.anim.webp')


def bauen(p):
    z = ziel(p)
    if z.exists() and '--neu' not in sys.argv:
        return None
    with tempfile.TemporaryDirectory() as t:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(p), '-t', str(MAX_S), '-an',
                        '-vf', f'fps={FPS},scale=min({BREITE}\\,iw):-2:flags=lanczos', f'{t}/b%04d.png'], check=True)
        bilder = sorted(Path(t).glob('b*.png'))
        if not bilder:
            return f'leer: {p}'
        subprocess.run(['img2webp', '-loop', '0', '-lossy', '-q', str(Q), '-m', '4', '-d', str(1000 // FPS),
                        *map(str, bilder), '-o', str(z)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return None


if __name__ == '__main__':
    qs = quellen()
    with ThreadPoolExecutor(6) as ex:
        fehler = [f for f in ex.map(bauen, qs) if f]
    groesse = sum(ziel(p).stat().st_size for p in qs if ziel(p).exists())
    print(f'{len(qs)} Videos, {sum(ziel(p).exists() for p in qs)} Bilder, {groesse / 1e6:.1f} MB', *fehler, sep='\n')

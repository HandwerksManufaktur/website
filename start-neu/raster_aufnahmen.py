"""Aufnahmen für das Websites-Raster („Bezugsfertig.“ auf /websites/) in Retina-Schärfe (Noah, 21.11.2026: „die seiten da schauen
richtig unscharf aus“ — die alten Aufnahmen unter static/assets/vid/hero/ sind 640 px breit, die Kacheln am Desktop 400–1250 px).

Je Betrieb in static/assets/vid/raster/:
  h<k>.webm  Hero-Schleife der LIVE-Seite, 1280×800 (breit: 1920×960, zwei: 1600×640), VP9, 8 s, ohne Ton
  h<k>.jpg   Vorschaubild (erstes Bild der Schleife)
  s<k>.webp  ganze Seite zum Durchscrollen, 1440 px breit (breit: 1920), Höhe auf 6000 px gekappt, WebP q78
  v<k>.webp  alte Website („Vorher“), 1440 px breit, Höhe auf 5000 px gekappt — aus vorher_quellen()

Das Laufband der Startseite bleibt bei den 640-px-Fassungen in static/assets/vid/hero/ (Ladezeit der Startseite).
Aufnahme: system/apps/audit/hero_aufnehmen.mjs (HERO_W/HERO_H/SEITE_W/SEITE_MAX).

Aufruf:  /Users/noahs/CEO-GPT/.venv/bin/python start-neu/raster_aufnahmen.py [k …] [--vorher]
         ohne k: alle (vorhandene werden übersprungen, außer sie werden genannt) · --vorher: nur die Vorher-Bilder
"""
import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
REPO = Path(__file__).resolve().parent.parent
CEO = REPO.parent.parent
ZIEL = REPO / "static/assets/vid/raster"
AUDIT = CEO / "system/apps/audit"
ARBEIT = Path("/tmp/hwm-raster")

# k → (Live-URL, Form). Form: "" normale Kachel, "breit" über alle Spalten, "zwei" zwei Spalten breit
SEITEN = {
    "entenmann": ("https://entenmann-preview.pages.dev/", "breit"),   # Domain zeigt noch nicht auf die neue Seite (21.11.2026)
    "irlbacher": ("https://www.hs-irlbacher.de/", "breit"), "sdhirsch": ("https://sdhirsch.de/", ""),
    "schillinger": ("https://meisterschillinger.de/", ""), "koller": ("https://zimmerei-koller.com/", "breit"),
    "dinkel": ("https://dinkel-metallbau.de/", ""), "ww": ("https://w-w-bau.com/", ""),
    "knappich": ("https://zimmerei-knappich.de/", ""), "hirschvogel": ("https://kuechenhaus-hirschvogel.de/", ""),
    "kirchner": ("https://kirchner-thaining.de/", ""), "wohner": ("https://elektrotechnik-wohner.de/", "breit"),
    "baureize": ("https://baureize.de/", ""), "resch": ("https://resch-kinsau.de/", ""),
    "hindelang": ("https://planung-hindelang.de/", ""), "kraus": ("https://dachbau-kraus.de/", ""),
    "schwaighofer": ("http://schwaighofer-betontechnik.de/", ""), "vogel": ("https://vogel-holzbau.de/", ""),
    "maser": ("https://tankschutz-landsberg.de/", ""), "kreitner": ("https://schreinerei-kreitner.de/", "breit"),
    "erisried": ("https://www.schustererisried.de/", ""), "wagenknecht": ("https://juwelier-wagenknecht.de/", ""),
    "weber": ("https://weber-metalltechnik.com/", ""), "mueller": ("https://mueller-maler-meister.de/", ""),
    "ess": ("https://erwin-schmidt-sohn.de/", "breit"),
}
FORM = {"": (1280, 800, 1440), "breit": (1920, 960, 1920), "zwei": (1640, 560, 1440), "gross": (1200, 1140, 1440)}
# Große Kacheln (2 × 2) sind am Desktop fast quadratisch (819 × 781 px gemessen): eigener Film h<k>-q.webm in 1200 × 1140,
# damit nichts abgeschnitten wird; der 16:10-Film h<k>.webm bleibt für Handy/Tablet (data-src-mobil).
GROSS = set()  # seit 21.11.2026 keine quadratischen Kacheln mehr (Noah: „eher waagrecht, irlbacher ist schon fast senkrecht und die seite ist abgeschnitten“)


def vorher_quellen():
    """Alte Website je Betrieb — nur belegte Aufnahmen, nie geraten (siehe Rückmeldung im Commit)."""
    vn = REPO / "images/Vorher-Nachher"
    return {
        "sdhirsch": vn / "SD Hirsch vorher.png", "erisried": vn / "Schuster Erisried vorher.png", "baureize": vn / "Baureize vorher.png",
        "maser": vn / "Maser Tankschutz vorher.png", "kreitner": vn / "Schreinerei Kreitner vorher.png",
        "kirchner": vn / "Kirchner Thaining vorher.png", "hirschvogel": vn / "Küchenhaus Hirschvogel vorher.png",
        "dinkel": vn / "Dinkel Metallbau vorher.png",  # Schwaighofer: Aufnahme zeigt nur „Die Website ist nicht erreichbar“ → kein Vorher
        "kraus": vn / "Dachbau Kraus vorher.png", "resch": vn / "Resch Bau vorher.png", "knappich": vn / "Zimmerei Knappich vorher.png",
        "hindelang": vn / "Planung Hindelang vorher.png", "vogel": vn / "Vogel Holzbau vorher.png",
        "koller": REPO / "assets/work/vorher-koller.jpg",
        # Screenshots der alten Seiten aus den Kundenakten (aufgenommen, als sie noch live waren)
        "irlbacher": CEO / "kunden/irlbacher/recherche/screenshots/alt-desktop-1440.png",      # Vorgänger Rauch GmbH (übernommen)
        "schillinger": CEO / "kunden/schillinger/recherche/screenshots/alt-desktop-1440.png",
        # Wayback Machine, Aufnahme 09.02.2025 (vor der neuen Seite)
        "entenmann": REPO / "start-neu/vorher-roh/entenmann.png",
    }


def vorher(k):
    q = vorher_quellen().get(k)
    if not q or not q.exists():
        return None
    im = Image.open(q).convert("RGB"); w, h = im.size
    # Fenster-Screenshots haben unten einen schwarzen Rand: dunkle Zeilen vom Fuß her abschneiden
    grau = im.convert("L").resize((64, h))
    unten = h
    while unten > h // 3 and sum(grau.crop((0, unten - 1, 64, unten)).getdata()) / 64 < 18:
        unten -= 1
    im = im.crop((0, 0, w, unten)); h = unten
    im = im.resize((1440, round(h * 1440 / w)), Image.LANCZOS)
    im = im.crop((0, 0, 1440, min(im.height, 5000)))
    ziel = ZIEL / f"v{k}.webp"
    im.save(ziel, "WEBP", quality=78, method=6)
    return ziel.stat().st_size


def leer_raus(im, lang=300, rest=120):
    """Leere Bänder (gepinnte Scroll-Strecken hinterlassen in der Ganzseiten-Aufnahme hunderte Pixel einfarbige Fläche, z. B.
    Entenmanns Wärmekreis) auf `rest` px zusammenschieben, damit die Kachel beim Durchscrollen nie lange nur Fläche zeigt."""
    from PIL import ImageStat
    klein = im.convert("L").resize((96, im.height))
    leer = [ImageStat.Stat(klein.crop((0, y, 96, y + 1))).stddev[0] < 2.5 for y in range(im.height)]
    teile, y = [], 0
    while y < im.height:
        z = y
        while z < im.height and leer[z] == leer[y]:
            z += 1
        if leer[y] and z - y > lang:
            teile.append((y, y + rest // 2)); teile.append((z - rest // 2, z))
        else:
            teile.append((y, z))
        y = z
    if len(teile) == 1:
        return im
    neu = Image.new("RGB", (im.width, sum(b - a for a, b in teile)))
    o = 0
    for a, b in teile:
        neu.paste(im.crop((0, a, im.width, b)), (0, o)); o += b - a
    return neu


def aufnehmen(k, nur_film=None):
    """nur_film="gross": nur den quadratischen Film h<k>-q für die große Kachel (Seitenbild bleibt)."""
    url, form = SEITEN[k]
    fw, fh, sw = FORM[nur_film if nur_film else form]
    zus = "-q" if nur_film == "gross" else ""
    ARBEIT.mkdir(parents=True, exist_ok=True)
    out = ARBEIT / f"h{k}{zus}"
    env = {"HERO_W": str(fw), "HERO_H": str(fh), "SEITE_W": str(sw), "SEITE_MAX": "12000", "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"}
    r = subprocess.run(["node", "hero_aufnehmen.mjs", url, str(out), "9"], cwd=AUDIT, env=env, capture_output=True, text=True,
                       stdin=subprocess.DEVNULL, timeout=240)
    info = json.loads(r.stdout.strip().splitlines()[-1])
    cut = info["cut"]
    ff = ["ffmpeg", "-nostdin", "-loglevel", "error", "-y"]
    subprocess.run(ff + ["-ss", str(cut), "-t", "8", "-i", f"{out}.raw.webm", "-vf", f"scale={fw}:-2,fps=24", "-c:v", "libvpx-vp9",
                         "-crf", "40", "-b:v", "0", "-row-mt", "1", "-deadline", "good", "-cpu-used", "2", "-an", str(ZIEL / f"h{k}{zus}.webm")], check=True)
    subprocess.run(ff + ["-ss", str(cut), "-i", f"{out}.raw.webm", "-frames:v", "1", "-vf", f"scale={fw}:-2", "-q:v", "4",
                         str(ZIEL / f"h{k}{zus}.jpg")], check=True)
    if nur_film:
        return k, zus, (ZIEL / f"h{k}{zus}.webm").stat().st_size
    im = leer_raus(Image.open(f"{out}.seite.png").convert("RGB"))
    im = im.crop((0, 0, im.width, min(im.height, 6000)))
    im.save(ZIEL / f"s{k}.webp", "WEBP", quality=78, method=6)
    return k, {x: (ZIEL / f"{x}{k}.{e}").stat().st_size for x, e in (("h", "webm"), ("h", "jpg"), ("s", "webp"))}, im.size


if __name__ == "__main__":
    ZIEL.mkdir(parents=True, exist_ok=True)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--vorher" in sys.argv:
        for k in args or SEITEN:
            print(k, vorher(k))
        sys.exit(0)
    if "--gross" in sys.argv:  # nur die quadratischen Filme der großen Kacheln
        for k in args or sorted(GROSS):
            print(*aufnehmen(k, "gross"), flush=True)
        sys.exit(0)
    liste = args or [k for k in SEITEN if not (ZIEL / f"h{k}.webm").exists()]
    with ThreadPoolExecutor(4) as pool:
        def sicher(k):
            try:
                return aufnehmen(k)
            except Exception as e:  # ein Ausfall hält die anderen nicht an
                return k, "FEHLER", repr(e)[:300]
        for erg in pool.map(sicher, liste):
            print(*erg, flush=True)

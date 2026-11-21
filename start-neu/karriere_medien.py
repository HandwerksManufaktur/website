"""Lifestyle-Bilder und Hero-Film für /karriere/ (Noah, 21.11.2026: „die seite muss ansprechender sein … so bisschen
lifestyle mäßig kann die schon sein“).

Quelle: Noahs eigene Reiseclips auf der „Extreme Pro“ (Clip-Bibliothek, systeme/clip-bibliothek.md), nur Szenen mit Noah
allein im Bild, keine Kunden, kein Bruder (Dolomiten-Clips C085x), kein Oberkörper frei. Sony S-Log3 bekommt Noahs eigenen
Look „NS 01 Natur“ aus der LUT-Fabrik. Ausgabe nach static/assets/img/karriere/ und static/assets/vid/karriere/.

Aufruf: /Users/noahs/CEO-GPT/.venv/bin/python firma/website/start-neu/karriere_medien.py [--nur-bilder|--nur-film]
"""
import subprocess
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
IMG = WURZEL / "static/assets/img/karriere"
VID = WURZEL / "static/assets/vid/karriere"
LUT = "/Users/noahs/CEO-GPT/system/apps/lut-fabrik/ausgabe/NS 01 Natur A7IV SLog3.cube"
EP = "/Volumes/Extreme Pro"

# (Datei-Kurz, Ort, Pfad, Sekunde für das Standbild, Bildausschnitt horizontal in % für Hochkant)
ORTE = [
    ("kapstadt", "Kapstadt", f"{EP}/2025/Kapstadt, Südafrika/Kamera Videos/C1921.MP4", 4.0, 55),
    ("singapur", "Singapur", f"{EP}/2025/Singapur/Videos Sony A7IV/C0585.MP4", 6.6, 62),
    ("kuala-lumpur", "Kuala Lumpur", f"{EP}/2026/Kuala Lumpur, Malaysia/Kamera Videos/C2223.MP4", 6.0, 40),
    ("mexiko", "Mexiko", f"{EP}/2025/Tulum, Mexico/Kamera Videos/C1356.MP4", 4.0, 50),
    ("vietnam", "Da Nang", f"{EP}/2026/Da Nang, Vietnam/Kamera Videos/C2068.MP4", 30.5, 58),
    ("athen", "Athen", f"{EP}/2026/Athens, Greece/Kamera Videos/C2835.MP4", 4.5, 50),
    ("lions-head", "Kapstadt", f"{EP}/2025/Kapstadt, Südafrika/Linos Head/Videos/C1595.MP4", 108.0, 45),
    ("sonnenuntergang", "Kapstadt", f"{EP}/2025/Kapstadt, Südafrika/Linos Head/Videos/C1604.MP4", 3.5, 45),
]

# Hero-Film: (Pfad, Start, Dauer); der Laptop-Film vom Kontakt-Hero als Anker „hier wird gearbeitet“
FILM = [  # Noah, 21.11.2026: Hout-Bay-Clip (C1921, Blick in die Kamera) raus, Globus-Dreher und Tippen auf der Tastatur rein
    (str(WURZEL / "static/assets/vid/hero-unter/kontakt-d.mp4"), 1.0, 3.0, False),                         # Laptop in KL
    (f"{EP}/2025/Kapstadt, Südafrika/Kamera Videos/C1693.MP4", 35.1, 2.4, True),                         # Tippen auf der Tastatur
    (f"{EP}/2025/Kapstadt, Südafrika/Kamera Videos/C1536.MP4", 1.0, 1.4, True),                          # Globus, erst wenn er sich schon dreht (Noah 21.11.: „kürzer oder wo es schon in motion ist“)
    (f"{EP}/2025/Kapstadt, Südafrika/Linos Head/Videos/C1604.MP4", 2.6, 2.4, True),
    (f"{EP}/2025/Singapur/Videos Sony A7IV/C0585.MP4", 5.4, 2.4, True),
    (f"{EP}/2026/Da Nang, Vietnam/Kamera Videos/C2068.MP4", 28.8, 2.4, True),
    (f"{EP}/2026/Kuala Lumpur, Malaysia/Kamera Videos/C2223.MP4", 5.0, 2.6, True),
]


def ff(*args):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *args], check=True)


def bilder():
    IMG.mkdir(parents=True, exist_ok=True)
    from PIL import Image  # ffmpeg hier ohne libwebp → PNG ziehen, mit Pillow als WebP schreiben
    for kurz, _ort, pfad, sek, _x in ORTE:
        roh = IMG / f"_{kurz}.png"
        ff("-ss", str(sek), "-i", pfad, "-frames:v", "1", "-vf", f"lut3d='{LUT}'", str(roh))
        bild = Image.open(roh).convert("RGB")
        for breite in (1600, 900):
            b = bild.copy()
            b.thumbnail((breite, breite * 2), Image.LANCZOS)
            b.save(IMG / f"{kurz}-{breite}.webp", "WEBP", quality=80, method=6)
        roh.unlink()
        print("✓ Bild", kurz)


def globus_ruhig(datei, zoom=1.07):
    """Globus-Clip ruhigstellen (Noah, 21.11.2026: „ein bisschen stabilisieren … soll sich drehen, aber geil positioniert“).
    Erkennt den Globus je Bild als Kreis, glättet die Mittelpunkte und hält ihn per Ausschnitt an einer festen Stelle."""
    import cv2, numpy as np
    cap = cv2.VideoCapture(str(datei)); bilder = []
    while True:
        ok, f = cap.read()
        if not ok: break
        bilder.append(f)
    H, W = bilder[0].shape[:2]
    mitte = []
    for f in bilder:
        g = cv2.medianBlur(cv2.cvtColor(cv2.resize(f, (W // 4, H // 4)), cv2.COLOR_BGR2GRAY), 5)
        c = cv2.HoughCircles(g, cv2.HOUGH_GRADIENT, dp=1.2, minDist=200, param1=80, param2=30, minRadius=H // 16, maxRadius=H // 8)
        mitte.append(c[0][0][:2] * 4 if c is not None else None)
    bekannt = np.array([m for m in mitte if m is not None])
    c0 = np.median(bekannt, 0)
    # Die Kreiserkennung trifft eher den Ständer-Ring; die Bildmitte des Globus selbst ist der Schwerpunkt der hellen Fläche
    hell = []
    for f in bilder[::4]:
        g = cv2.cvtColor(cv2.resize(f, (W // 4, H // 4)), cv2.COLOR_BGR2GRAY)
        _, m = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        mo = cv2.moments(m); hell.append([mo["m10"] / mo["m00"] * 4, mo["m01"] / mo["m00"] * 4])
    globus = np.median(np.array(hell), 0)
    # Kreiserkennung schwankt selbst um ±20 px; das echte Wackeln misst der feste Ring um den Globus (Kanten, Phasenkorrelation)
    yy, xx = np.mgrid[:H, :W]; d = np.hypot(xx - c0[0], yy - c0[1]); r = H / 2
    maske = ((d > r * 0.92) & (d < r * 1.25)).astype(np.float32)
    kante = lambda f: cv2.GaussianBlur(cv2.Canny(f, 60, 150).astype(np.float32) * maske, (0, 0), 3)
    ref = kante(bilder[0]); vers = [np.zeros(2)]
    for f in bilder[1:]:
        (dx, dy), _ = cv2.phaseCorrelate(ref, kante(f)); vers.append(np.array([dx, dy]))
    vers = np.array(vers); mitte = c0 + vers
    k = 3; glatt = np.array([mitte[max(0, i - k // 2):i + k // 2 + 1].mean(0) for i in range(len(mitte))])
    schnitt = glatt.mean(0)
    hw, hh = W / zoom / 2, H / zoom / 2
    ziel = schnitt  # Bildaufbau der Aufnahme bleibt (Globus sitzt dort schon mittig), nur das Wackeln geht raus
    zx = min(max(ziel[0], hw + 30), W - hw - 30); zy = min(max(ziel[1], hh + 20), H - hh - 20)
    roh = Path(str(datei) + ".roh.mp4")
    pr = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "25", "-i", "-",
                           "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", str(roh)], stdin=subprocess.PIPE)
    for f, m in zip(bilder, glatt):
        cx = min(max(zx + (m[0] - schnitt[0]), hw), W - hw); cy = min(max(zy + (m[1] - schnitt[1]), hh), H - hh)
        x0, y0 = int(round(cx - hw)), int(round(cy - hh))
        aus = f[y0:y0 + int(2 * hh), x0:x0 + int(2 * hw)]
        pr.stdin.write(cv2.resize(aus, (W, H), interpolation=cv2.INTER_LANCZOS4).tobytes())
    pr.stdin.close(); pr.wait()
    roh.replace(datei)
    print("  Globus ruhiggestellt, Wackeln vorher ±%.0f px" % np.abs(vers - vers.mean(0)).max())


def film():
    VID.mkdir(parents=True, exist_ok=True)
    teile = []
    for i, (pfad, start, dauer, log) in enumerate(FILM):
        # erst auf 1280 Höhe verkleinern, dann einfärben (LUT auf 4K kostete 8 Min je Szene), eine Decodierung für beide Fassungen
        import hashlib, shutil
        CACHE = Path.home() / "Library/Caches/hwm-karriere"
        CACHE.mkdir(parents=True, exist_ok=True)
        schl = hashlib.md5(f"{pfad}|{start}|{dauer}|{log}|v2".encode()).hexdigest()[:12]
        if (CACHE / f"{schl}d.mp4").exists() and (CACHE / f"{schl}m.mp4").exists():
            shutil.copy(CACHE / f"{schl}d.mp4", VID / f"_teil{i}d.mp4"); shutil.copy(CACHE / f"{schl}m.mp4", VID / f"_teil{i}m.mp4")
            print("  Szene", i, "(Zwischenspeicher)", flush=True); teile.append(i); continue
        farbe = f",lut3d='{LUT}'" if log else ""
        graph = (f"[0:v]scale=-2:1280:flags=bicubic{farbe},fps=25,format=yuv420p,split=2[a][b];"
                 "[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080[d];"
                 "[b]crop=720:1280[m]")
        ff("-ss", str(start), "-t", str(dauer), "-i", pfad, "-an", "-filter_complex", graph,
           "-map", "[d]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", str(VID / f"_teil{i}d.mp4"),
           "-map", "[m]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", str(VID / f"_teil{i}m.mp4"))
        shutil.copy(VID / f"_teil{i}d.mp4", CACHE / f"{schl}d.mp4"); shutil.copy(VID / f"_teil{i}m.mp4", CACHE / f"{schl}m.mp4")
        print("  Szene", i, flush=True)
        teile.append(i)
    for i, (pfad, *_r) in enumerate(FILM):
        if "C1536" in pfad:
            globus_ruhig(VID / f"_teil{i}d.mp4")
    for art, crf in (("d", "27"), ("m", "28")):
        liste = VID / f"_liste{art}.txt"
        liste.write_text("".join(f"file '_teil{i}{art}.mp4'\n" for i in teile))
        ff("-f", "concat", "-safe", "0", "-i", str(liste), "-c:v", "libx264", "-preset", "slow", "-crf", crf,
           "-movflags", "+faststart", "-pix_fmt", "yuv420p", str(VID / f"hero-{art}.mp4"))
        ff("-ss", "1.5", "-i", str(VID / f"hero-{art}.mp4"), "-frames:v", "1", "-q:v", "4", str(VID / f"hero-{art}.jpg"))
    for f in VID.glob("_*"):
        f.unlink()
    print("✓ Film", [(f.name, f.stat().st_size // 1024) for f in sorted(VID.iterdir())])


# Handy-Fassung aus dem Desktop-Film: je Szene ein eigener Ausschnitt, damit Noah im Bild bleibt (Mitte schnitt ihn in
# Singapur und Da Nang ab). (Dauer, Bildmitte horizontal 0–1) in der Reihenfolge von FILM.
HANDY_MITTE = [0.56, 0.5, 0.5, 0.5, 0.75, 0.76, 0.42]


def handy():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        start, liste = 0.0, []
        for i, ((_p, _s, dauer, _l), cx) in enumerate(zip(FILM, HANDY_MITTE)):
            teil = Path(tmp) / f"t{i}.mp4"
            ff("-ss", f"{start:.2f}", "-t", str(dauer), "-i", str(VID / "hero-d.mp4"),
               "-vf", f"crop=608:1080:x='max(0,min(in_w-608,in_w*{cx}-304))':y=0,scale=720:1280:flags=lanczos,fps=25,format=yuv420p",
               "-c:v", "libx264", "-crf", "18", "-preset", "medium", str(teil))
            liste.append(f"file '{teil}'\n")
            start += dauer
        (Path(tmp) / "l.txt").write_text("".join(liste))
        ff("-f", "concat", "-safe", "0", "-i", str(Path(tmp) / "l.txt"), "-c:v", "libx264", "-preset", "slow", "-crf", "27",
           "-movflags", "+faststart", "-pix_fmt", "yuv420p", str(VID / "hero-m.mp4"))
    ff("-ss", "1.5", "-i", str(VID / "hero-m.mp4"), "-frames:v", "1", "-q:v", "4", str(VID / "hero-m.jpg"))
    print("✓ Handy-Film", (VID / "hero-m.mp4").stat().st_size // 1024, "KB")


# Noahs eigene Arbeitsfotos aus dem Bewerber-Funnel (firma/sales-funnel/assets/Arbeit) für „Lerne uns kennen“ und „Was wir bieten“
ARBEIT = WURZEL.parent / "sales-funnel/assets/Arbeit"
FOTOS = {"mission": "Bild mit Kunde.JPG", "geschichte": "Einzelbild.jpg", "setup": "arbeiten am strand 3.JPG",
         "kultur": "gemeinsam arbeiten 1.jpg", "team": "gemeinsam arbeiten 2.JPG", "calls": "calls am strand.JPG",
         "pool": "arbeiten aus thailand.JPG"}


def fotos():
    from PIL import Image, ImageOps
    IMG.mkdir(parents=True, exist_ok=True)
    for kurz, datei in FOTOS.items():
        bild = ImageOps.exif_transpose(Image.open(ARBEIT / datei)).convert("RGB")
        for breite in (1400, 800):
            b = bild.copy(); b.thumbnail((breite, breite * 2), Image.LANCZOS)
            b.save(IMG / f"a-{kurz}-{breite}.webp", "WEBP", quality=80, method=6)
        print("✓ Foto", kurz, bild.size)


if __name__ == "__main__":
    if "--fotos" in sys.argv:
        fotos(); sys.exit()
    if "--handy" in sys.argv:
        handy(); sys.exit()
    if "--nur-film" not in sys.argv:
        bilder()
    if "--nur-bilder" not in sys.argv:
        film()

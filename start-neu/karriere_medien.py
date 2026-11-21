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
FILM = [
    (str(WURZEL / "static/assets/vid/hero-unter/kontakt-d.mp4"), 1.0, 3.2, False),
    (f"{EP}/2025/Kapstadt, Südafrika/Linos Head/Videos/C1604.MP4", 2.6, 2.6, True),
    (f"{EP}/2025/Singapur/Videos Sony A7IV/C0585.MP4", 5.4, 2.6, True),
    (f"{EP}/2026/Da Nang, Vietnam/Kamera Videos/C2068.MP4", 28.8, 2.6, True),
    (f"{EP}/2026/Kuala Lumpur, Malaysia/Kamera Videos/C2223.MP4", 5.0, 2.6, True),
    (f"{EP}/2025/Kapstadt, Südafrika/Kamera Videos/C1921.MP4", 3.0, 2.6, True),
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


def film():
    VID.mkdir(parents=True, exist_ok=True)
    teile = []
    for i, (pfad, start, dauer, log) in enumerate(FILM):
        # erst auf 1280 Höhe verkleinern, dann einfärben (LUT auf 4K kostete 8 Min je Szene), eine Decodierung für beide Fassungen
        farbe = f",lut3d='{LUT}'" if log else ""
        graph = (f"[0:v]scale=-2:1280:flags=bicubic{farbe},fps=25,format=yuv420p,split=2[a][b];"
                 "[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080[d];"
                 "[b]crop=720:1280[m]")
        ff("-hwaccel", "videotoolbox", "-ss", str(start), "-t", str(dauer), "-i", pfad, "-an", "-filter_complex", graph,
           "-map", "[d]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", str(VID / f"_teil{i}d.mp4"),
           "-map", "[m]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", str(VID / f"_teil{i}m.mp4"))
        print("  Szene", i, flush=True)
        teile.append(i)
    for art, crf in (("d", "27"), ("m", "28")):
        liste = VID / f"_liste{art}.txt"
        liste.write_text("".join(f"file '_teil{i}{art}.mp4'\n" for i in teile))
        ff("-f", "concat", "-safe", "0", "-i", str(liste), "-c:v", "libx264", "-preset", "slow", "-crf", crf,
           "-movflags", "+faststart", "-pix_fmt", "yuv420p", str(VID / f"hero-{art}.mp4"))
        ff("-ss", "4.2", "-i", str(VID / f"hero-{art}.mp4"), "-frames:v", "1", "-q:v", "4", str(VID / f"hero-{art}.jpg"))
    for f in VID.glob("_*"):
        f.unlink()
    print("✓ Film", [(f.name, f.stat().st_size // 1024) for f in sorted(VID.iterdir())])


# Handy-Fassung aus dem Desktop-Film: je Szene ein eigener Ausschnitt, damit Noah im Bild bleibt (Mitte schnitt ihn in
# Singapur und Da Nang ab). (Dauer, Bildmitte horizontal 0–1) in der Reihenfolge von FILM.
HANDY_MITTE = [0.56, 0.5, 0.75, 0.76, 0.42, 0.66]


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
    ff("-ss", "4.2", "-i", str(VID / "hero-m.mp4"), "-frames:v", "1", "-q:v", "4", str(VID / "hero-m.jpg"))
    print("✓ Handy-Film", (VID / "hero-m.mp4").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    if "--handy" in sys.argv:
        handy(); sys.exit()
    if "--nur-film" not in sys.argv:
        bilder()
    if "--nur-bilder" not in sys.argv:
        film()

"""Linke Hero-Säule der HWM-Startseite (static/assets/vid/saeule/drohnen-d.mp4, -m.mp4, drohnen.jpg) neu schneiden.

Noah, 21.11.2026: „bei der linken säule … brauchen wir iwie szenen auch, die nice sind … neuen Entenmann Shooting …
Zimmerei Koller … mäßig action drin, wo mans sieht“. Harte Schnitte, stumm, 25 fps, Desktop 600×800, Handy 360×480,
nie zwei Szenen vom selben Betrieb direkt hintereinander (auch nicht über die Schleife).

Quellen:
  alt       = die bisherige drohnen-d.mp4 (Git-Stand; Drohnenflüge Wohner/Kreitner/CS Metalldesign, schon 3:4)  → ALT=<Pfad>
  entenmann = kunden/entenmann/material/shooting-final/Entenmann Headervideo Website 4K.mp4 (3840×2160)
  koller_a/koller_c = static/assets/vid/sr-koller-a.mp4 / sr-koller-c.mp4 (Showreel-Lagen aus „Final Zimmerei Koller“, 1280×720)
Aufruf:  ALT=/pfad/drohnen-alt-d.mp4 /Users/noahs/CEO-GPT/.venv/bin/python firma/website/start-neu/saeule_links_schneiden.py
"""
import os, subprocess, sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent
VID = WEB / "static/assets/vid"
ZIEL = VID / "saeule"
ENT = WEB.parent.parent / "kunden/entenmann/material/shooting-final/Entenmann Headervideo Website 4K.mp4"
ALT = Path(os.environ.get("ALT", ZIEL / "drohnen-d.mp4"))
KOLLER_A, KOLLER_C = VID / "sr-koller-a.mp4", VID / "sr-koller-c.mp4"
CS_B = VID / "sr-cs-b.mp4"   # Showreel-Lage CS: ab 2,0 s der lachende Schleifer (Noah 18./19.11.: „richtig geil“)

# (Betrieb, Quelle, Start s, Länge s, Mitte x 0–1 des 3:4-Ausschnitts, alt=schon 3:4, was man sieht)
SZENEN = [
    # Kreitner-Drohne raus (Noah, 21.11.2026: „das drohnenvideo bei kreitner raus … da sieht man nur die decke“)
    # CS-Schleifer vorn (Noah, 21.11.2026: „da in die geile säule links kommt auch der cs metalldesign clip was ich so nice fand …
    # die clips vom koller shooting sind gut, müssen nicht viele sein“) → zwei Koller-Szenen bleiben
    # Wohner-Drohne raus, dafür Entenmann-Nahaufnahme (Noah, 21.11.2026: „mach das wohner drohnenvideo in der mitte raus … close ups,
    # z.b. von entenmann shooting“); Reihenfolge so, dass nie zwei Szenen vom selben Betrieb aufeinander folgen (auch nicht über die Schleife)
    # CS-Drohne raus (Noah, 21.11.2026: „auch der drohnenclip von cs metalldesign in der mitte raus“) → keine Drohne mehr in der Mitte.
    # Mit nur noch einer CS-Szene trägt die Folge höchstens drei Entenmann-Szenen ohne zwei gleiche hintereinander → Rohrschneider raus.
    # Noah 24.11.2026: Nahaufnahme raus, unscharf (Entenmann Zange an der Armatur ENT 8.46). Alle Szenen am Quellschnitt gemessen
    # (ffmpeg scene>0.25): keine Szene enthält einen Quellschnitt, Ende/Anfang mind. 0,08 s Abstand. Trennschleifer endete vorher
    # im Schnitt bei 10,51 s (Transporter), Wärmepumpe im Schnitt bei 5,31 s, CS ab 2,12 s, Koller-A bei 2,8 s ... jeweils gekürzt.
    ("CS Metall",  CS_B,     2.20, 1.50, 0.45, "Schleifer mit Brille lacht an der Werkbank"),
    ("Entenmann",  ENT,      9.55, 0.85, 0.40, "Trennschleifer mit Funken am Rohr"),
    ("Koller",     KOLLER_A, 0.10, 1.22, 0.28, "Zimmerer mit Akkuschrauber am Balken"),
    ("Entenmann",  ENT,      4.30, 0.92, 0.60, "Wärmepumpe wird durch den Garten gebracht"),
    ("Koller",     KOLLER_C, 1.30, 1.20, 0.52, "Kappsäge, Zimmerer mit Gehörschutz schneidet den Balken"),
]
assert all(SZENEN[i][0] != SZENEN[i - 1][0] for i in range(len(SZENEN))), "zwei Szenen vom selben Betrieb hintereinander"


def filt(quelle, cx, i):
    if cx is None:
        return f"[{i}:v]fps=25,setpts=PTS-STARTPTS,scale=600:800:flags=lanczos,setsar=1[v{i}]"
    ew = f"trunc(ih*3/4/2)*2"
    return (f"[{i}:v]fps=25,setpts=PTS-STARTPTS,crop={ew}:ih:max(0\\,min(iw-{ew}\\,iw*{cx}-{ew}/2)):0,"
            f"scale=600:800:flags=lanczos,setsar=1[v{i}]")


def bauen():
    ein, f = [], []
    for i, (_, q, ab, dauer, cx, _) in enumerate(SZENEN):
        assert Path(q).exists(), q
        ein += ["-ss", str(ab), "-t", str(dauer), "-i", str(q)]
        f.append(filt(q, cx, i))
    n = len(SZENEN)
    f.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1,format=yuv420p[v]")
    tmp = ZIEL / "_drohnen-neu-d.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ein, "-filter_complex", ";".join(f), "-map", "[v]", "-an", "-r", "25",
                    "-c:v", "libx264", "-crf", os.environ.get("CRF", "25"), "-preset", "slow", "-movflags", "+faststart", str(tmp)], check=True)
    m = ZIEL / "_drohnen-neu-m.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-vf", "scale=360:480:flags=lanczos", "-an", "-r", "25",
                    "-c:v", "libx264", "-crf", os.environ.get("CRF_M", "27"), "-preset", "slow", "-movflags", "+faststart", str(m)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-frames:v", "1", "-q:v", "4", str(ZIEL / "drohnen.jpg")], check=True)
    os.replace(tmp, ZIEL / "drohnen-d.mp4")
    os.replace(m, ZIEL / "drohnen-m.mp4")
    print(f"{n} Szenen, {sum(s[3] for s in SZENEN):.2f} s")


if __name__ == "__main__":
    bauen()

#!/usr/bin/env python3
"""Film-Heros der Unterseiten (Noah, 21.11.2026): je Seite ein eigener Film über die volle Breite statt der drei Säulen.

Ausgabe je Seite in static/assets/vid/hero-unter/:  <seite>-d.mp4 (1920 x 1080) · <seite>-m.mp4 (540 x 1080, Ausschnitt je Szene)
                                                    <seite>.jpg · <seite>-m.jpg (erstes Bild = Poster)
Stumm, H.264 faststart, harte Schnitte, 8 bis 15 s Schleife. Foto & Video behält seinen Showreel (bauen.py).

Quellen:
  Entenmann-Headerfilm  kunden/entenmann/material/shooting-final/Entenmann Headervideo Website 4K.mp4 (Schnittgrenzen B wie in
                        kunden/entenmann/website/videos_schneiden.py)
  Websitefilme          static/assets/vid/*.mp4 und static/assets/fv/v/*.mp4 (schon im Repo)
  Noah am Laptop        Extreme Pro  /2025/Kapstadt, Südafrika/Kamera Videos/C1697.MP4 (Hände auf der Laptop-Tastatur, S-Log3)
                        Extreme Pro  /2026/Kuala Lumpur, Malaysia/Kamera Videos/C2246.MP4 (Noah im Café am Laptop, S-Log3, gespiegelt,
                        damit er rechts sitzt und die Überschrift links frei bleibt)
                        S-Log3-Quellen: NS 06 Filmprint (system/apps/lut-fabrik/ausgabe). Die 4K-Dateien vorher auf die Platte kopieren
                        (QUELLEN=<ordner> mit C1697.MP4 und C2246.MP4), von der exFAT-Platte aus ist das Springen zu langsam.

Aufruf:  QUELLEN=<ordner> /Users/noahs/CEO-GPT/.venv/bin/python firma/website/start-neu/hero_unterseiten_schneiden.py [seite ...]
"""
import os, subprocess, sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
ZIEL = WURZEL / "static/assets/vid/hero-unter"
VID = WURZEL / "static/assets/vid"
FV = WURZEL / "static/assets/fv/v"
QUELLEN = Path(os.environ.get("QUELLEN", "."))
ENT = Path("/Users/noahs/CEO-GPT/kunden/entenmann/material/shooting-final/Entenmann Headervideo Website 4K.mp4")
LUT = "/Users/noahs/CEO-GPT/system/apps/lut-fabrik/ausgabe/NS 06 Filmprint A7IV SLog3.cube"

B = [0, 1.0677, 2.1355, 3.2032, 4.2376, 5.3053, 6.3397, 7.3740, 8.4084, 9.4428, 10.5105, 11.5449, 12.5792, 13.6136,
     14.6480, 15.6823, 16.7167, 17.7844, 18.8522, 19.8532, 20.9209, 21.9886, 23.0230, 24.0574, 25.0584, 26.0927,
     27.1271, 28.2282, 29.2959, 30.2636, 31.3313]
ENT_MX = {1: .50, 3: .46, 4: .60, 5: .60, 7: .55, 10: .35, 15: .60, 19: .75, 22: .55}


def ent(n):
    return (ENT, B[n - 1] + .05, B[n] - B[n - 1] - .10, ENT_MX[n], "")


# (Datei, Start s, Länge s, Mitte x des Handy-Ausschnitts 0–1 (nach dem Spiegeln), Zusatz: "lut" | "lut,flip" | "")
SEITEN = {
    # Websites: Entenmann, das Vorzeigeprojekt (neun Einstellungen aus dem Headerfilm)
    "websites": [ent(n) for n in (4, 5, 7, 10, 19, 22, 15, 3, 1)],
    # Neukundengewinnung: Fischer Bad Heizung Solar (Team am Transporter, Solardach von oben)
    "neukundengewinnung": [(FV / "fi-team.mp4", .6, 6.2, .50, ""), (FV / "fi-drohne.mp4", .2, 3.6, .45, "")],
    # Mitarbeitergewinnung: Resch Bau, Zimmerei Koller, Schreinerei Kreitner bei der Arbeit
    "mitarbeitergewinnung": [(VID / "resch.mp4", 0.0, 2.9, .55, ""), (VID / "resch.mp4", 4.4, 3.7, .50, ""),
                             (VID / "koller.mp4", 0.0, 2.0, .40, ""), (VID / "koller.mp4", 5.0, 1.8, .50, ""),
                             (VID / "kreitner.mp4", 6.0, 2.5, .50, "")],
    # Suchmaschinenoptimierung: Drohnenflüge über Betriebe (Baureize, Wohner, Koller, Fischer)
    "suchmaschinenoptimierung": [(VID / "baureize.mp4", .9, 3.5, .50, ""), (FV / "g-wohner.mp4", .3, 3.5, .50, ""),
                                 (VID / "koller.mp4", 3.0, 2.0, .45, ""), (FV / "fi-drohne.mp4", 4.1, 1.5, .50, "")],
    # Über uns: Noah am Laptop (Hände auf der Tastatur, Noah im Café)
    "ueber-uns": [(QUELLEN / "C1697.MP4", 2.0, 5.5, .50, "lut"), (QUELLEN / "C2246.MP4", 12.0, 5.0, .58, "lut,flip"),
                  (QUELLEN / "C1697.MP4", 10.5, 3.5, .50, "lut")],
    # Kontakt: ruhige Szene, Noah im Café am Laptop (anderer Abschnitt)
    "kontakt": [(QUELLEN / "C2246.MP4", 25.0, 12.0, .56, "lut,flip")],
}


def ff(*a):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)


def kette(teile, mobil):
    f = []
    for i, (_, _, _, cx, extra) in enumerate(teile):
        v = f"[{i}:v]setpts=PTS-STARTPTS,scale=1920:1080:flags=lanczos"
        if "lut" in extra:
            v += f",lut3d='{LUT}'"
        if "flip" in extra:
            v += ",hflip"
        if mobil:
            x = min(max(round(1920 * cx - 270), 0), 1920 - 540)
            v += f",crop=540:1080:{x}:0"
        f.append(v + f",fps=25,format=yuv420p[q{i}]")
    return ";".join(f) + ";" + "".join(f"[q{i}]" for i in range(len(teile))) + f"concat=n={len(teile)}:v=1:a=0[v]"


def schneiden(seite):
    teile = SEITEN[seite]
    ein = []
    for datei, ab, dauer, _, _ in teile:
        ein += ["-ss", f"{ab:.3f}", "-t", f"{dauer:.3f}", "-i", str(datei)]
    gem = ["-an", "-c:v", "libx264", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-g", "50"]
    ZIEL.mkdir(parents=True, exist_ok=True)
    ff(*ein, "-filter_complex", kette(teile, False), "-map", "[v]", *gem, "-crf", "28", "-maxrate", "2200k", "-bufsize", "4400k", str(ZIEL / f"{seite}-d.mp4"))
    ff(*ein, "-filter_complex", kette(teile, True), "-map", "[v]", *gem, "-crf", "29", "-maxrate", "1100k", "-bufsize", "2200k", str(ZIEL / f"{seite}-m.mp4"))
    ff("-i", str(ZIEL / f"{seite}-d.mp4"), "-frames:v", "1", "-q:v", "5", str(ZIEL / f"{seite}.jpg"))
    ff("-i", str(ZIEL / f"{seite}-m.mp4"), "-frames:v", "1", "-q:v", "5", str(ZIEL / f"{seite}-m.jpg"))
    gesamt = sum(t[2] for t in teile)
    print(f"  {seite}: {len(teile)} Szenen, {gesamt:.1f} s · {(ZIEL / f'{seite}-d.mp4').stat().st_size / 1e6:.2f} MB / Handy {(ZIEL / f'{seite}-m.mp4').stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    for s in (sys.argv[1:] or SEITEN):
        schneiden(s)

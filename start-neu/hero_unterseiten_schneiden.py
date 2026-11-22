#!/usr/bin/env python3
"""Film-Heros der Unterseiten (Noah, 21.11.2026): je Seite ein eigener Film über die volle Breite statt der drei Säulen.

Ausgabe je Seite in static/assets/vid/hero-unter/:  <seite>-d.mp4 (1920 x 1080) · <seite>-m.mp4 (540 x 1080, Ausschnitt je Szene)
                                                    <seite>.jpg · <seite>-m.jpg (erstes Bild = Poster)
Stumm, H.264 faststart, harte Schnitte, 8 bis 15 s Schleife. Foto & Video behält seinen Showreel (bauen.py).

Quellen:
  Entenmann-Headerfilm  kunden/entenmann/material/shooting-final/Entenmann Headervideo Website 4K.mp4 (Schnittgrenzen B wie in
                        kunden/entenmann/website/videos_schneiden.py)
  Koller-Shooting       Extreme Pro  /2026/Deutschland/Shooting Koller/Kamera Videos/C23xx.MP4 (Sony, S-Log3-Cine → NS 06) und
                        Drohe Shots/DJI_*.MP4 (Rec709 → GRADE)
  Kreitner-Film         Extreme Pro  /2025/Kunden/Shooting Schreinerei Kreitner/Schreinerei Kreitner Video.mp4 (4K, schon gegradet)
  Websitefilme          static/assets/vid/*.mp4 und static/assets/fv/v/*.mp4 (schon im Repo)
  Noah am Laptop        Extreme Pro  /2025/Kapstadt, Südafrika/Kamera Videos/C1697.MP4 (Hände auf der Laptop-Tastatur, S-Log3)
                        Extreme Pro  /2026/Kuala Lumpur, Malaysia/Kamera Videos/C2246.MP4 (Noah im Café am Laptop, S-Log3, gespiegelt,
                        damit er rechts sitzt und die Überschrift links frei bleibt)
                        S-Log3-Quellen: NS 06 Filmprint (system/apps/lut-fabrik/ausgabe). Die 4K-Dateien vorher auf die Platte kopieren
                        (QUELLEN=<ordner> mit Kopien gleichen Namens, z. B. C1697.MP4, C2362.MP4), von der exFAT-Platte aus ist das
                        Springen zu langsam; was in QUELLEN fehlt, wird vom Originalpfad gelesen.

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
CSFILM = Path("/Volumes/Extreme Pro/2025/Kunden/Shooting CS Metalldesign/CS Metalldesign.mp4")
BAUREIZEFILM = Path("/Volumes/Extreme Pro/2025/Kunden/Shooting Baureize/Baureize original.mp4")
KOLLERFILM = Path("/Volumes/Extreme Pro/2026/Deutschland/Shooting Koller/Final Zimmerei Koller.mp4")
RESCHFILM = Path("/Volumes/Extreme Pro/2025/Kunden/Shooting A. Resch Bau/Resch Bau.mp4")
KAPSTADT = Path("/Volumes/Extreme Pro/2025/Kapstadt, Südafrika/Kamera Videos")
KOLLER = Path("/Volumes/Extreme Pro/2026/Deutschland/Shooting Koller")
KREITNER = Path("/Volumes/Extreme Pro/2025/Kunden/Shooting Schreinerei Kreitner/Schreinerei Kreitner Video.mp4")
BAUREIZE = Path("/Volumes/Extreme Pro/2025/Kunden/Shooting Baureize/Drone-Shots")
LUT = "/Users/noahs/CEO-GPT/system/apps/lut-fabrik/ausgabe/NS 06 Filmprint A7IV SLog3.cube"
# Rec709-Material ohne Look (flach, kalt, überbelichtet) an den warmen Filmlook der anderen Heros angleichen
# (Noah, 21.11.2026: „colorgrading bei der unterseite neukundengewinnung ist noch trash“)
GRADE = ("curves=all='0/0.025 0.25/0.19 0.5/0.48 0.75/0.79 1/0.93',"
         "colorbalance=rs=-0.07:bs=0.06:rm=0.03:bm=-0.03:rh=0.07:gh=0.02:bh=-0.07,eq=saturation=1.06,vignette=PI/5")

B = [0, 1.0677, 2.1355, 3.2032, 4.2376, 5.3053, 6.3397, 7.3740, 8.4084, 9.4428, 10.5105, 11.5449, 12.5792, 13.6136,
     14.6480, 15.6823, 16.7167, 17.7844, 18.8522, 19.8532, 20.9209, 21.9886, 23.0230, 24.0574, 25.0584, 26.0927,
     27.1271, 28.2282, 29.2959, 30.2636, 31.3313]
ENT_MX = {1: .50, 3: .46, 4: .60, 5: .60, 7: .55, 10: .35, 15: .60, 19: .75, 22: .55}


def quelle(p):
    """Kopie gleichen Namens in QUELLEN bevorzugen (exFAT-Platte ist zum Springen zu langsam)."""
    k = QUELLEN / Path(p).name
    return k if k.exists() else Path(p)


def kol(name):
    return KOLLER / ("Drohe Shots" if name.startswith("DJI") else "Kamera Videos") / name


def ent(n):
    return (ENT, B[n - 1] + .05, B[n] - B[n - 1] - .10, ENT_MX[n], "")


# (Datei, Start s, Länge s, Mitte x des Handy-Ausschnitts 0–1 (nach dem Spiegeln), Zusatz: "lut" | "lut,flip" | "grade" | "")
SEITEN = {
    # Websites: Entenmann, das Vorzeigeprojekt (neun Einstellungen aus dem Headerfilm)
    "websites": [ent(n) for n in (4, 5, 7, 10, 19, 22, 15, 3, 1)],
    # Neukundengewinnung (Noah, 21.11.2026: Fischer-Film „trash“, nur 960×540 hochskaliert, Drohne „nicht clean in einer Linie“
    # → komplett ersetzt): Koller-Shooting 4K (S-Log3 → LUT, Drohne Rec709 → GRADE) + zwei Entenmann-Einstellungen, die auf
    # /websites/ nicht laufen (Transporter vor dem Kundenhaus, Monteure an der Haustür)
    # Noah, 21.11.2026: „nicht diesen Switch von Koller auf einmal zu Entenmann … einfach Close-ups verwenden: Schweißen,
    # Säge von Koller, Drahtdrehen von Resch, Akkuschrauber, der sich dreht“
    # Noah, 21.11.2026: „beim schweißen … den clip … wo man den laser so in der mitte des bildes sieht“
    "neukundengewinnung": [(CSFILM, 5.97, 1.5, .50, ""),                 # CS: Schweißlicht mitten im Bild (Close-up)
                           (KOLLERFILM, 3.68, 1.4, .50, ""),             # Koller: Säge, Späne fliegen (Close-up)
                           (RESCHFILM, 8.45, 0.85, .55, ""),               # Resch: Draht an der Bewehrung drehen (Close-up)
                           (ENT, 25.12, 0.95, .50, "")],                 # Entenmann: Rohrschneider dreht sich am Rohr (Close-up, vor dem nächsten Schnitt)
 # Monteure an der Haustür
    # Mitarbeitergewinnung (Noah, 21.11.2026: „nicht einfach das von Resch, sondern da kannst du das von Koller nehmen“):
    # Koller-Team im 4K-Original, S-Log3 über NS 06
    # Noah, 21.11.2026: „kürzere zusammengeschnittene clips nimm einfach die was wir bei koller so auch drin hatten nur bisschen anders
    # gecutted“ → 11 Szenen à ~1 s aus demselben Koller-Shooting, wechselnd nah/weit
    # Noah, 21.11.2026 spät: „einen koller clip doppelt drin“ (Akkuschrauber 2×) → einmal; „den koller clip noch oben mit rein vom desktop“
    # (Bohrer in den Spänen, linke Säule Startseite) und „foto & video … drittens von links … koller … der dritte clip“ (Hof von oben)
    "mitarbeitergewinnung": [(kol("C2362.MP4"), 2.4, 1.0, .50, "lut"),   # Team läuft auf die Kamera zu
                             (KOLLERFILM, 5.48, 1.3, .50, ""),           # Hof von oben (Koller-Galeriefilm, 3. Clip)
                             (kol("C2391.MP4"), 1.2, 1.0, .42, "lut"),   # Akkuschrauber am Balken
                             (KOLLERFILM, 9.1, 1.2, .50, ""),            # Close-up: Bohrer in den Spänen (Startseite)
                             (kol("C2412.MP4"), 2.6, 0.9, .58, "lut"),   # Säge mit Gehörschutz
                             (KOLLERFILM, 14.48, 1.3, .50, ""),          # Close-up: Sägeblatt im Balken
                             (KOLLERFILM, 7.28, 1.3, .50, "")],          # Martin fährt Stapler
       # Close-up: Sägeblatt im Balken (vorletzte Foto-&-Video-Lage)
    # (Noah, 21.11.2026: „das Video, wo Martin winkt, kommt raus … wie er im Stapler fährt … lieber noch die Close-ups … vom vorletzten Video von Foto und Video“)
    # (Noah, 21.11.2026: „da wo der eine mitarbeiter komplett still in die kamera starrt weg und manche andere, was da sonst nicht
    # drin waren, auch raus“ → nur die bisherigen Koller-Clips, junger Zimmerer C2371 und die Neuzugänge raus)
    # Noah, 21.11.2026: „da kannst meinetwegen das gruppen-ding von kreitner nehmen … aber rest was anderes, nicht kreitner drohne“
    # → Drohnenflüge über Betriebe (Koller über dem Ort, Baureize-Halle) in 4K, dazwischen die Kreitner-Gruppe
    # Noah, 21.11.2026 abends: „bei seo nimm die schlechten videos raus“ → graue Drohnenflüge (Koller-Ort, Baureize-Halle) raus,
    # nur die freigegebene Kreitner-Gruppe bleibt
    # Noah, 21.11.2026: „nicht nur kreitner … wo sind die guten clips cs metalldesign … bei baureize mit dem laser … und paar andere gut“
    # → die im Showreel freigegebenen Stellen aus den 4K-Originalfilmen (CS Metalldesign.mp4, Baureize original.mp4), schon gegradet
    "suchmaschinenoptimierung": [(BAUREIZEFILM, 20.67, 1.6, .55, ""),  # Baureize: grüner Linienlaser
                                 (BAUREIZEFILM, 12.67, 1.9, .50, ""),  # Baureize: Wolfgang an der Formatkreissäge
                                 # (Noah, 21.11.2026: „den kreitner clip bei seo raus, ist shit“)
                                 (CSFILM, 9.96, 1.9, .50, ""),         # CS: Schleifer lacht
                                 # Noah, 22.11.2026: „den clip vom hilti bohrer … von entenmann … als letzter – und nochmal
                                 #  irgendeinen von cs metalldesign danach“ + „close up von den teilen bei entenmann“
                                 (ENT, 26.1, 1.0, .50, ""),            # Entenmann: Hilti-Bohrer auf dem Tisch, Gegenlicht
                                 (ENT, 12.7, 0.75, .50, ""),           # Entenmann: Nahaufnahme Fittings im Regal
                                 (CSFILM, 4.6, 1.3, .55, "")],         # CS: Schweißerin mit Maske
    # (Noah, 21.11.2026: „den komischen Übergang weg … vom Lasermesser zu Kreitner“ → Kreitner nicht mehr nach dem Laser;
    #  CS-Schweißen mit roten Handschuhen „kommt beim anderen raus“ → Neukundengewinnung)
       # CS: Schweißen mit Maske
    # Über uns: Noah am Laptop, nur die Hände auf der Tastatur (Kapstadt C1697).
    # Noah, 21.11.2026: „mach bei über uns das video von mir in singapur raus“ → Café-Szene C2246 raus, auch bei Kontakt
    "ueber-uns": [(KAPSTADT / "C1697.MP4", 2.0, 5.5, .50, "lut"), (KAPSTADT / "C1697.MP4", 10.5, 3.5, .50, "lut")],
    "kontakt": [(KAPSTADT / "C1697.MP4", 14.0, 6.5, .50, "lut")],
}


def ff(*a):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)


def kette(teile, mobil):
    f = []
    for i, (_, _, _, cx, extra) in enumerate(teile):
        v = f"[{i}:v]setpts=PTS-STARTPTS,scale=1920:1080:flags=lanczos"
        if "lut" in extra:
            v += f",lut3d='{LUT}'"
        if "grade" in extra:
            v += "," + GRADE
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
        ein += ["-ss", f"{ab:.3f}", "-t", f"{dauer:.3f}", "-i", str(quelle(datei))]
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

"""Showreel-Lagen für den Hero von Foto & Video (static/assets/vid/sr-*.mp4): je Betrieb DREI Einstellungen
(Noah, 19.11.2026: „Wir wollen nicht nur zwei Szenen haben, wir wollen drei Szenen haben“), 1280 × 720, 25 fps, stumm,
letztes Bild 1,2 s stehend für die Überblendung.

Quellen (Originale aus dem Kunden-Drive, lokal in QUELLEN abgelegt):
  koller_final.mp4       Drive „Kunden/Webdesign/abgeschlossene Projekte/Zimmerei Koller/Shooting/Videos/Final Zimmerei Koller.mp4“
  cs_metalldesign.mp4    Drive „…/CS Metalldesign/Videos/CS Metalldesign.mp4“
  baureize_original.mp4  Drive „Baureize original.mp4“
  kirchner_0503.mp4      Drive „dji_fly_20240625_143026_0503_…_video.mp4“ (1v9bcwkcUGE28LUk763WJzfVmcznTDTJq)
Fischer (sr-fischer) und Resch (sr-resch) sind schon dreiteilig bzw. vierteilig und werden hier nicht neu gebaut.

Aufruf:  QUELLEN=<ordner> /Users/noahs/CEO-GPT/.venv/bin/python firma/website/start-neu/showreel_szenen.py [lage …]
"""
import os, subprocess, sys
from pathlib import Path

ZIEL = Path(__file__).resolve().parent.parent / "static/assets/vid"
QUELLEN = Path(os.environ.get("QUELLEN", "."))
HALT = 1.2

# (Datei, Start s, Länge s, zeitlupe) — zeitlupe = alle Originalbilder mit 25 fps abspielen (30-fps-Quelle wirkt ruhiger)
LAGEN = {
    # Noah 19.11.: „das kommt als Allererstes, weil dieses Video richtig geil ist“ → Halle, Zylinder, lachender Schleifer (letzte)
    "sr-cs-b": [("cs_metalldesign.mp4", 0.3, 1.2, False), ("cs_metalldesign.mp4", 7.97, 0.92, False), ("cs_metalldesign.mp4", 9.96, 1.94, True)],
    "sr-cs-a": [("cs_metalldesign.mp4", 2.04, 1.5, False), ("cs_metalldesign.mp4", 4.1, 1.4, False), ("cs_metalldesign.mp4", 5.97, 1.6, False)],
    "sr-koller-a": [("koller_final.mp4", 1.86, 1.4, False), ("koller_final.mp4", 3.68, 1.4, False), ("koller_final.mp4", 27.1, 1.4, False)],
    "sr-koller-b": [("koller_final.mp4", 5.48, 1.3, False), ("koller_final.mp4", 7.28, 1.3, False), ("koller_final.mp4", 25.1, 1.4, False)],
    "sr-koller-c": [("koller_final.mp4", 23.6, 1.2, False), ("koller_final.mp4", 12.68, 1.4, False), ("koller_final.mp4", 14.48, 1.3, False)],
    # Säge bleibt die letzte Einstellung (Noah 19.11.: „wo er an der säge steht mach da bei ihm als letztes hin“)
    "sr-baureize": [("baureize_original.mp4", 20.67, 1.6, False), ("baureize_original.mp4", 16.6, 1.3, False), ("baureize_original.mp4", 12.67, 1.9, False)],
    # Kirchner „darf drin bleiben, aber nur kurz“ (18.11.) → drei sehr kurze Einstellungen aus dem einen Drohnenflug
    "sr-kirchner": [("kirchner_0503.mp4", 0.2, 0.7, False), ("kirchner_0503.mp4", 1.9, 1.1, False), ("kirchner_0503.mp4", 5.5, 0.8, False)],
}


def bauen(name):
    teile = LAGEN[name]
    ein, filt = [], []
    for i, (datei, ab, dauer, zeitlupe) in enumerate(teile):
        quelle = QUELLEN / datei
        assert quelle.exists(), quelle
        ein += ["-ss", str(ab), "-t", str(dauer), "-i", str(quelle)]
        tempo = "setpts=N/25/TB" if zeitlupe else "fps=25,setpts=PTS-STARTPTS"
        filt.append(f"[{i}:v]{tempo},scale=1280:720:flags=lanczos,setsar=1[v{i}]")
    kette = "".join(f"[v{i}]" for i in range(len(teile)))
    filt.append(f"{kette}concat=n={len(teile)}:v=1,tpad=stop_mode=clone:stop_duration={HALT},format=yuv420p[v]")
    aus = ZIEL / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ein, "-filter_complex", ";".join(filt), "-map", "[v]", "-an", "-r", "25",
                    "-c:v", "libx264", "-crf", "20", "-preset", "slow", "-movflags", "+faststart", str(aus)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "0.4", "-i", str(aus), "-frames:v", "1", "-vf", "scale=960:540", "-q:v", "4",
                    str(ZIEL / "poster" / f"{name}.jpg")], check=True)
    inhalt = sum(t[2] * (30 / 25 if t[3] else 1) for t in teile)
    print(f"{name}: {len(teile)} Einstellungen, {inhalt:.2f} s")
    return inhalt


if __name__ == "__main__":
    for n in (sys.argv[1:] or LAGEN):
        bauen(n)

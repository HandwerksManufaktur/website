"""Medien für die neuen Unterseiten-Heros und die Seite Foto & Video (Noah, 18.11.2026).

„Bei Foto und Video brauchen wir einfach eine geile … Da müssen wir die besten Fotos und Videos haben … weil da stehe ich
jetzt dreimal irgendwie mit Kunden und ich sollte da jetzt nicht unbedingt damit drauf sein.“

🔴 Nur eigenes Drehtag-Material (Robert), kein Foto, auf dem Noah mit einem Kunden steht (die liegen in
marketing/instagram/noah-mit-kunden/ und gehören auf /ueber-uns/). Jede Auswahl unten ist von Hand angesehen.
Quellen: marketing/instagram/karussells/<kunde>/ (2000 px), Shooting-Ordner der Kunden, firma/website-shk/assets/fotos,
die Reels der Kunden (kunden/<kunde>/videos/reel/out, liegen auf der Extreme Pro).

Schreibt nach static/assets/fv/ (g = Galerie, h = Hero, k = Kontaktabzug, v = Reels) und start-neu/bilder/fv-*.webp.
Idempotent: vorhandene Dateien bleiben stehen (--neu erzwingt).
Aufruf: /Users/noahs/CEO-GPT/.venv/bin/python firma/website/start-neu/medien_bauen.py [--neu]
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageOps

HIER = Path(__file__).resolve().parent
WEB = HIER.parent
CEO = WEB.parent.parent
ZIEL = WEB / "static/assets/fv"
NEU = "--neu" in sys.argv

K = CEO / "marketing/instagram/karussells"
SE = str(CEO) + "/kunden/senftleben/funnel/assets/Senftleben Shooting Bilder/Senftleben 2026 ({}).jpg"
ES = str(CEO) + "/kunden/erwin-schmidt-sohn/funnel/assets/Erwin Schmidt & Sohn GmbH Shooting Bilder/Erwin Schmidt Fotos ({}).jpg"
ST = str(CEO) + "/kunden/stimpfle/assets/shooting/Stimpfle_-_Bilder_{}.jpg"
SHK = CEO / "firma/website-shk/assets/fotos"
PRAXIS = WEB / "static/assets/img/praxis"
P = lambda muster, n: Path(muster.format(n))

# (Datei-Kürzel, Quelle, Gewerk-Schlüssel, Gewerk, Betrieb)  — Betrieb nur, wo er auf dem Bild oder in unseren Akten belegt ist
GALERIE = [
    ("se-hocke", P(SE, 25), "shk", "Sanitär & Heizung", "Senftleben Haustechnik"),
    ("st-bohrhammer", P(ST, 43), "shk", "Sanitär & Heizung", "Stimpfle Sanitär & Heizung"),
    ("ko-kluft", K / "koller/16.jpg", "holz", "Zimmerei", "Zimmerei Koller"),
    ("cs-schweissen", K / "cs-metalldesign/07.jpg", "metall", "Metallbau", "CS Metalldesign"),
    ("se-luft", P(SE, 67), "shk", "Sanitär & Heizung", "Senftleben Haustechnik"),
    ("ki-team", K / "kirchner/13.jpg", "bau", "Bau & Transporte", "Kirchner Thaining"),
    ("kr-hobel", K / "kreitner/14.jpg", "holz", "Schreinerei", "Schreinerei Kreitner"),
    ("es-tragen", P(ES, 36), "shk", "Sanitär & Heizung", "Erwin Schmidt & Sohn"),
    ("sd-roboter", K / "sd-hirsch/09.jpg", "metall", "Metallverarbeitung", "SD Hirsch"),
    ("se-armatur", P(SE, 52), "shk", "Sanitär & Heizung", "Senftleben Haustechnik"),
    ("sn-balken", K / "schneider/18.jpg", "holz", "Zimmerei", "Zimmerei Schneider"),
    ("dach", PRAXIS / "foto-dach-kraus.jpg", "bau", "Dach", "Dachbau Kraus"),
    ("st-wasserwaage", P(ST, 47), "shk", "Sanitär & Heizung", "Stimpfle Sanitär & Heizung"),
    ("cs-hund", K / "cs-metalldesign/15.jpg", "metall", "Metallbau", "CS Metalldesign"),
    ("kl-lachen", K / "klass/12.jpg", "shk", "Sanitär & Heizung", "Heizung-Sanitär Klaß"),
    ("ki-bagger", K / "kirchner/18.jpg", "bau", "Tiefbau", "Kirchner Thaining"),
    ("ko-balken", K / "koller/18.jpg", "holz", "Zimmerei", "Zimmerei Koller"),
    ("es-kisten", P(ES, 42), "shk", "Sanitär & Heizung", "Erwin Schmidt & Sohn"),
    ("cs-helm", K / "cs-metalldesign/11.jpg", "metall", "Metallbau", "CS Metalldesign"),
    ("se-wagen", P(SE, 63), "shk", "Sanitär & Heizung", "Senftleben Haustechnik"),
    ("pv", PRAXIS / "foto-elektro-wohner-pv.jpg", "bau", "Elektro", "Wohner Elektrotechnik"),
    ("kr-regal", K / "kreitner/09.jpg", "holz", "Schreinerei", "Schreinerei Kreitner"),
    ("su-lager", SHK / "sussmann-lager-scharf.jpg", "shk", "Sanitär & Heizung", "Erich Sussmann"),
    ("ki-lkw", K / "kirchner/07.jpg", "bau", "Bau & Transporte", "Kirchner Thaining"),
    ("sd-rohre", K / "sd-hirsch/12.jpg", "metall", "Metallverarbeitung", "SD Hirsch"),
    ("es-faust", P(ES, 20), "shk", "Sanitär & Heizung", "Erwin Schmidt & Sohn"),
    ("sn-stapler", K / "schneider/17.jpg", "holz", "Zimmerei", "Zimmerei Schneider"),
    ("kl-wand", K / "klass/09.jpg", "shk", "Sanitär & Heizung", "Heizung-Sanitär Klaß"),
    ("galabau", PRAXIS / "foto-galabau-peine-baum.jpg", "bau", "Garten- & Landschaftsbau", ""),
    ("se-hammer", P(SE, 41), "shk", "Sanitär & Heizung", "Senftleben Haustechnik"),
    ("cs-schleifen", K / "cs-metalldesign/09.jpg", "metall", "Metallbau", "CS Metalldesign"),
    ("kr-team", K / "kreitner/19.jpg", "holz", "Schreinerei", "Schreinerei Kreitner"),
    ("ir-lager", SHK / "irlbacher-josef-lager.jpg", "shk", "Sanitär & Heizung", "Irlbacher Gebäudetechnik"),
    ("maler", PRAXIS / "foto-maler-woerner-team.jpg", "bau", "Maler", "Malerbetrieb Wörner"),
    ("hv-schubladen", K / "hirschvogel/13.jpg", "holz", "Küchenbau", "Küchenhaus Hirschvogel"),
    ("ki-kabine", K / "kirchner/05.jpg", "bau", "Tiefbau", "Kirchner Thaining"),
    ("st-tragen", P(ST, 36), "shk", "Sanitär & Heizung", "Stimpfle Sanitär & Heizung"),
    ("ko-team", K / "koller/06.jpg", "holz", "Zimmerei", "Zimmerei Koller"),
]
# Kontaktabzug: je Motiv eine Aufnahme (Folgen fast gleicher Bilder sähen wie Dubletten aus), in Aufnahme-Reihenfolge
KONTAKT_AUSWAHL = (1, 5, 6, 11, 13, 15, 22, 25, 28, 30, 32, 37, 39, 40, 44, 46, 49, 55, 57, 59)
# Karten „Was wir übernehmen“ auf /foto-video/ (vorher drei Fotos mit Noah und Kunde)
KARTEN = [
    ("fv-motivliste", K / "hirschvogel/14.jpg"),
    ("fv-drehtag", WEB / "static/assets/img/team/team-robert-gross.webp"),
    ("fv-uebergabe", K / "hirschvogel/17.jpg"),
]
# Hintergründe der Heros Neukunden (Sussmann) und Mitarbeiter (Irlbacher), passend zu den Reels in den Telefonen
HERO = [("h-sussmann", SHK / "sussmann-team-2026.jpg"), ("h-irlbacher", SHK / "irlbacher-wagen.jpg")]
# Reels (echte Anzeigen, die wir gedreht haben): Leadgen Sussmann, Recruiting Irlbacher — je 8 s, 540 × 960
REELS = [
    ("su-dusche", CEO / "kunden/sussmann/videos/reel/out/v07-wanne-zu-dusche.mp4", 0.0),
    ("su-mirjana", CEO / "kunden/sussmann/videos/reel/out/v12-muenchner-osten.mp4", 0.0),
    ("su-patrick", CEO / "kunden/sussmann/videos/reel/out/v01-termin-geplatzt.mp4", 0.0),
    ("ir-montage", CEO / "kunden/irlbacher/videos/reel/out/v04-montage.mp4", 0.0),
    ("ir-geselle", CEO / "kunden/irlbacher/videos/reel/out/v12-frischer-geselle.mp4", 0.0),
    ("ir-nummer", CEO / "kunden/irlbacher/videos/reel/out/v01-nur-eine-nummer.mp4", 0.0),
]


def oeffnen(q):
    im = Image.open(q)
    im.draft("RGB", (2400, 2400))
    return ImageOps.exif_transpose(im).convert("RGB")


def webp(im, ziel, breite, qual=78):
    if ziel.exists() and not NEU:
        return
    ziel.parent.mkdir(parents=True, exist_ok=True)
    k = im.copy()
    if k.width > breite:
        k = k.resize((breite, round(k.height * breite / k.width)), Image.LANCZOS)
    k.save(ziel, "WEBP", quality=qual, method=6)


def main():
    daten = []
    for kurz, q, g, gewerk, betrieb in GALERIE:
        assert q.exists(), q
        im = oeffnen(q)
        webp(im, ZIEL / f"g/{kurz}-480.webp", 480, 74)
        webp(im, ZIEL / f"g/{kurz}-900.webp", 900)
        webp(im, ZIEL / f"g/{kurz}-1800.webp", 1800, 80)
        daten.append({"k": kurz, "g": g, "gewerk": gewerk, "betrieb": betrieb, "w": im.width, "h": im.height})
    for kurz, q in KARTEN:
        webp(oeffnen(q), HIER / f"bilder/{kurz}.webp", 1200)
    for kurz, q in HERO:
        webp(oeffnen(q), ZIEL / f"h/{kurz}.webp", 1920, 74)
    # Kontaktabzug: ein Drehtag bei Stimpfle, nur Querformate, in Aufnahme-Reihenfolge
    kontakt = []
    for n in KONTAKT_AUSWAHL:
        q = P(ST, n)
        if not q.exists():
            continue
        im = oeffnen(q)
        if im.width <= im.height:
            continue
        webp(im, ZIEL / f"k/st{n:02d}.webp", 420, 72)
        kontakt.append(f"st{n:02d}")
    for kurz, q, ab in REELS:
        mp4, jpg = ZIEL / f"v/{kurz}.mp4", ZIEL / f"v/{kurz}.jpg"
        if mp4.exists() and not NEU:
            continue
        assert q.exists(), q
        mp4.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ab), "-i", str(q), "-t", "8", "-an",
                        "-vf", "scale=540:960:force_original_aspect_ratio=increase,crop=540:960,fps=30",
                        "-c:v", "libx264", "-profile:v", "main", "-crf", "27", "-preset", "slow", "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart", str(mp4)], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "0.6", "-i", str(mp4), "-frames:v", "1", "-q:v", "4", str(jpg)], check=True)
    (ZIEL / "galerie.json").write_text(json.dumps({"fotos": daten, "kontakt": kontakt}, ensure_ascii=False, indent=1))
    print(f"✓ {len(daten)} Galeriefotos, {len(kontakt)} Kontaktabzug-Bilder, {len(REELS)} Reels → {ZIEL.relative_to(WEB)}")


if __name__ == "__main__":
    main()

"""Kunden-Zusammenschnitt für die rechte Hero-Säule der HWM-Startseite (Noah, 18.11.2026).

„wenn die Kunden da drin sind … können sie ruhig ein bisschen kleiner sein, also so weit weg wie möglich. Der Kopf von
denen sollte eigentlich eher mittig beim rechten Balken sein“. Die Originale (alle Hochformat) haben den Kopf bei 20–33 %
der Höhe — darum: jede Szene verkleinert, Kopf bei KOPF_Y der Säule und überall gleich groß (Match Cut), der Rand ist
dieselbe Szene weichgezeichnet und abgedunkelt, die Kante des scharfen Bildes läuft weich aus.
Szenen, Reihenfolge, Startbilder: firma/website-shk/neu/video/kunden_szenen.py (SZENEN), Köpfe gemessen mit dessen
gesichter()/ruhigste_sekunde(). Aufruf (System-python3 wegen OpenCV):
  SZENEN_CACHE=<ordner mit Fenstern> /usr/bin/python3 firma/website/start-neu/kunden_szenen_saeule.py
"""
import json, os, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, '/Users/noahs/CEO-GPT/firma/website-shk/neu/video')
import kunden_szenen as k
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance

W, H = 540, 1056                 # Seitenverhältnis der Säule am Desktop (433 × 846 px, Video 459 × 897)
KOPF_Y, KOPF_H = 0.50, 0.095     # Kopfmitte in der Säulenmitte, Kopf gut halb so groß wie auf der SHK-Seite (0,17)
ZIEL = Path(__file__).resolve().parent.parent / 'static/assets/vid/saeule'
C = Path(os.environ['SZENEN_CACHE'])


def maske(w, h, rand):
    # Weicher Übergang statt sichtbarem Kasten: seitlich und oben und unten je ein Fünftel bzw. Sechstel als Verlauf (endet das Bild über der Säulenunterkante, sonst Kante sichtbar), unten läuft
    # das Bild ohnehin aus der Säule (Noah sieht sonst einen Rahmen um die Person).
    rx, ry = max(rand, w // 5), max(rand, h // 6)
    m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
    d.rectangle([rx, ry, w - rx, h - ry], fill=255)
    return m.filter(ImageFilter.GaussianBlur(min(rx, ry) * 0.7))


def szene(sz, kopf, aus):
    fen = Path(kopf['datei']); s = kopf['start']
    fh = round(KOPF_H * H / kopf['h']); fw = round(fh * kopf['W'] / kopf['H'])
    x0 = round(W / 2 - kopf['cx'] * fw); y0 = round(KOPF_Y * H - kopf['cy'] * fh)
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['ffmpeg', '-v', 'error', '-i', str(fen), '-vf', f"select='between(n\\,{s}\\,{s + k.BILDER - 1})',setpts=N/30/TB,scale={fw}:{fh}:flags=lanczos",
                        '-frames:v', str(k.BILDER), f'{d}/f_%03d.png'], check=True)
        rand = max(24, fw // 12); mk = maske(fw, fh, rand)
        for p in sorted(Path(d).glob('f_*.png')):
            fg = Image.open(p).convert('RGB')
            s_bg = max(W / fw, H / fh) * 1.08
            bg = fg.resize((round(fw * s_bg), round(fh * s_bg)), Image.BILINEAR)
            bx, by = round(W / 2 - kopf['cx'] * bg.width), round(H / 2 - kopf['cy'] * bg.height)
            bx = min(0, max(W - bg.width, bx)); by = min(0, max(H - bg.height, by))
            leinwand = Image.new('RGB', (W, H), (22, 19, 14))
            leinwand.paste(ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(28))).enhance(0.34), (bx, by))
            leinwand.paste(fg, (x0, y0), mk)
            leinwand.save(Path(d) / ('o_' + p.name))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '30', '-i', f'{d}/o_f_%03d.png', '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', str(aus)], check=True)
    return fw, fh, x0, y0


def main():
    koepfe = json.loads((C / 'koepfe.json').read_text())
    teile = []
    with tempfile.TemporaryDirectory() as d:
        for i, sz in enumerate(k.SZENEN):
            aus = Path(d) / f'{i:02d}.mp4'
            print(k.sid(sz), szene(sz, koepfe[k.sid(sz)], aus), flush=True)
            teile.append(aus)
        liste = Path(d) / 'liste.txt'; liste.write_text(''.join(f"file '{t}'\n" for t in teile))
        roh = Path(d) / 'roh.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(liste), '-c', 'copy', str(roh)], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(roh), '-an', '-c:v', 'libx264', '-crf', '28', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(ZIEL / 'kunden-szenen-d.mp4')], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(roh), '-an', '-vf', 'scale=360:704', '-c:v', 'libx264', '-crf', '30', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(ZIEL / 'kunden-szenen-m.mp4')], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '0.5', '-i', str(roh), '-frames:v', '1', '-q:v', '4', str(ZIEL / 'kunden-szenen.jpg')], check=True)
        # Prüfung am fertigen Video: Kopf je Szene mittig und gleich groß
        kd = k.gesichter(ZIEL / 'kunden-szenen-d.mp4', verkl=1.0)
        for i, sz in enumerate(k.SZENEN):
            f = [x for x in kd[i * k.BILDER:(i + 1) * k.BILDER] if x]
            if not f: print('  ⚠️', k.sid(sz), 'kein Kopf erkannt'); continue
            m = lambda key: sorted(x[key] for x in f)[len(f) // 2]
            print(f"  {k.sid(sz):24s} Kopf x={m('cx'):.2f} y={m('cy'):.2f} h={m('h'):.3f} ({len(f)}/{k.BILDER} Bilder frontal)")


if __name__ == '__main__':
    main()

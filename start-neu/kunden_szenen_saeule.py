"""Kunden-Zusammenschnitt für die rechte Hero-Säule der HWM-Startseite (Noah, 18.11.2026).

1) „können sie ruhig ein bisschen kleiner sein, also so weit weg wie möglich“ · 2) nach dem Versuch mit weichgezeichnetem
Rand: „Nein, das Video soll schon das ganz ausfüllen, aber es sollte halt nicht so sein, dass der Kopf … abgeschnitten ist“.
Also: jede Szene im VOLLEN Originalbild ohne Zoom (weiter weg geht nicht, ohne Rand anzustückeln), randvoll im Format der
Säule (540 × 1056), seitlich auf den Kopf gemittelt. Kein Weichzeichner-Rand, kein Kasten.
Prüfung: Kopf je Szene ganz im Bild und unterhalb der schrägen Oberkante + Etikett der Säule (KOPF_OBEN_MIN).
Szenen, Reihenfolge, Startbilder: firma/website-shk/neu/video/kunden_szenen.py (SZENEN). Aufruf (System-python3 wegen OpenCV):
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


KOPF_OBEN_MIN = 0.12   # schräge Oberkante (9 %) der Säule; darüber wäre der Kopf angeschnitten


def szene(sz, kopf, aus):
    fen = Path(kopf['datei']); s = kopf['start']
    sw, sh = kopf['W'], kopf['H']
    ch = sh; cw = round(sh * W / H)
    if cw > sw: cw, ch = sw, round(sw * H / W)
    x0 = min(max(0, round(kopf['cx'] * sw - cw / 2)), sw - cw); y0 = 0
    vf = (f"select='between(n\\,{s}\\,{s + k.BILDER - 1})',setpts=N/30/TB,crop={cw}:{ch}:{x0}:{y0},"
          f"scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(fen), '-vf', vf, '-frames:v', str(k.BILDER), '-r', '30', '-an',
                    '-c:v', 'libx264', '-crf', '16', '-preset', 'slow', str(aus)], check=True)
    return cw, ch, x0, y0


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
            oben = m('cy') - m('h') / 2
            print(f"  {k.sid(sz):24s} Kopf x={m('cx'):.2f} y={m('cy'):.2f} h={m('h'):.3f} Oberkante={oben:.3f} {'✓' if oben >= KOPF_OBEN_MIN else '✗ ZU HOCH'} ({len(f)}/{k.BILDER} frontal)")


if __name__ == '__main__':
    main()

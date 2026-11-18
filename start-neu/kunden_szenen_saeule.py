"""Kunden-Zusammenschnitt für die rechte Hero-Säule der HWM-Startseite (Noah, 18.11.2026).

Noah: 1) „können sie ruhig ein bisschen kleiner sein, also so weit weg wie möglich. Der Kopf … eher mittig beim rechten
Balken“ · 2) „das Video soll schon das ganz ausfüllen“ (kein verkleinertes Bild mit weichem Rand) · 3) „die Köpfe sind immer
noch abgeschnitten. Vielleicht muss man sonst auch einen anderen Clip … nehmen … das soll auf jeden Fall mehr zentriert sein“.

Ursache bis v3: die Takes der SHK-Seite (kunden_szenen.py) sind eng gefilmt, der Kopf sitzt im Original bei 20–27 % der Höhe;
oben liegen die schräge Kante der Säule (9 %) und die Beschriftung „Anfragen und Bewerbungen.“ → Haaransatz verdeckt.
Lösung (v4): eigene Szenenliste mit WEITER gefilmten Takes (Rohmaterial im Drive durchsucht, ~1.500 Stichproben gemessen,
Kontaktbogen angesehen). Kein Take im Material hat Kopfmitte 35–45 % UND Kopf ≤ 12 % ohne Zoom; daher je Szene genau so viel
Zoom, dass der Kopf seitlich mittig und bei ZIEL_Y steht (oben gerade so viel Luft, dass Schräge + Beschriftung frei bleiben).
Randvoll 540 × 1056 (Säulenformat), kein Weichzeichner. Die SHK-Datei kunden_szenen.py bleibt unangetastet (baut die SHK-Seite).

Regeln (Noah, 18./19.10. + 15.11.): jeder Betrieb zuerst einmal, nie derselbe Betrieb zweimal hintereinander (auch nicht über die
Schleife), Blick in die Kamera, Augen offen, keine eingebrannten Untertitel, Logo auf der Kleidung frei, Florian Schmidt raus.

Aufruf (System-python3 wegen OpenCV-Cascade):
  SZENEN_CACHE=<ordner für Fenster> /usr/bin/python3 firma/website/start-neu/kunden_szenen_saeule.py
  … --pruefen   → misst nur die fertige Datei
"""
import json, os, statistics as st, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, '/Users/noahs/CEO-GPT/firma/website-shk/neu/video')
import kunden_szenen as k                      # nur drive_token(); die SHK-Szenenliste wird hier NICHT benutzt

W, H = 540, 1056                 # Seitenverhältnis der Säule am Desktop (433 × 846 px bei 1440 × 900)
BILDER = 30                      # 1,0 s je Szene
ZIEL_Y = 0.36                    # Kopfmitte im Bild: so tief wie nötig (Schräge + Beschriftung), so wenig Zoom wie möglich
OBEN_MIN = 0.235                 # Kopfoberkante (Haar/Kappe) mindestens hier: bei 1000 × 555 endet die Beschriftung bei ≈ 0,21 des Videos
HAAR = 0.75                      # Gesichtsbox ≈ Brauen bis Kinn; Haaransatz ≈ ¾ Boxhöhe über der Kopfmitte (Kappe: eigener Wert je Szene)
GRENZEN = dict(y=(0.35, 0.45), x=(0.42, 0.58), haar_min=0.23, h_max=0.19, erkannt_min=0.8)
ZIEL = Path(__file__).resolve().parent.parent / 'static/assets/vid/saeule'
ID = lambda s: s['id']

# fen = Drive-Datei-ID, ab/dauer = Fenster im Original (s), bild = Startbild im Fenster (Sichtprüfung: Blick in die Kamera,
# Augen offen, Lächeln, keine Hand vorm Gesicht), x = Lage der gemeinten Person im Original (bei zwei Personen im Bild).
SZENEN = [
    dict(id='sussmann', betrieb='Sussmann', wer='Patrick Wähnl redet in die Kamera, Lager (lehnt am Regal)',
         datei='Bodies/Sussmann Bodys (4).MP4', fen='1kuXUTHwEBLFEeG9FNgH5PO9TZNJdfIxP', ab=160, dauer=20, bild=420, x=0.5, h_max=0.22),   # Noah 18.11. abends: Patrick „anderes“, aktiv redend statt stumm vor dem Wagen (CTAs (2), 20,2 s)
    dict(id='stimpfle', betrieb='Stimpfle', wer='Mitarbeiterin von Stimpfle lächelt in der Werkstatt',
         datei='Arbeitsclips/h3.mp4 (= Hooks (3).MP4, Proxy)', fen='1pnyURN083iPTMSUh0KLD4RY2uX78fS1O', ab=0, dauer=9, bild=45, x=0.41),
    dict(id='erwin-schmidt', betrieb='Erwin Schmidt', wer='Mitarbeiter (Kappe) von Erwin Schmidt am Tisch',
         datei='Videos/Erwin Schmidt Videos(13) - Mitarbeiter 2.MP4', fen='1BAZUGJdcPTz9_41zRHw5su2GJTsZsHoO', ab=20, dauer=12, bild=243, x=0.56, haar=0.9),
    dict(id='fischer', betrieb='Fischer', wer='Bettina Tittmann sitzt an der Werkbank und lächelt',
         datei='Arbeitsclips/h13.mp4 (= Hooks - Fischer (13).MP4, Proxy)', fen='1bd7zBbgj9X9CVo0nDWBNIzhn4nEsW2ZD', ab=18, dauer=14, bild=354, x=0.52),
    dict(id='senftleben', betrieb='Senftleben', wer='Mitarbeiterin von Senftleben am Tisch (Interview)',
         datei='Recruiting/MA-Interviews/Senftleben Mitarbeiter (3).MP4', fen='1bjOejFdcWlCcupT5o19dykP50gAIFH2J', ab=60, dauer=10, bild=81, x=0.29),
    dict(id='irlbacher', betrieb='Irlbacher', wer='Mitarbeiter von Irlbacher vor dem Firmenwagen',
         datei='Mitarbeiter/Interview.MP4', fen='1MqMldEOR677S8IqSsSYPYptdG7Lexh6n', ab=92, dauer=8, bild=15, x=0.53),
    # Noah 18.11. abends: „Mirjana sollte noch mit rein. Yannick Stimpfle sollte auch mit rein.“ — von beiden gibt es keinen weiten Take,
    # daher mehr Zoom (Kopf etwas größer als bei den übrigen), Kopf ganz, mittig, unter der Beschriftung.
    dict(id='sussmann-mirjana', betrieb='Sussmann', wer='Mirjana Wähnl vor der Sussmann-Logowand, Blick in die Kamera',
         datei='Hooks/Sussmann Hooks (18).MP4', fen='1XJvZpI9nt_sM9_Ua5voUnOdCOntqxUqx', ab=0, dauer=8, bild=9, x=0.5, h_max=0.22),
    dict(id='stimpfle-yannick', betrieb='Stimpfle', wer='Yannick Stimpfle redet in die Kamera, Werkstatt',
         datei='Arbeitsclips/h1.mp4 (= Hooks (1).MP4, Proxy)', fen='1SfErnbAQXKn4CkM8MVqErsm1hiXq73AT', ab=86, dauer=28, bild=414, x=0.5, h_max=0.24),
]
# Nicht genommen (18.11.2026, Messung + Kontaktbogen): Senftleben-Mitarbeiter rechts im selben Interview (Brille, Gesicht nur
# zeitweise frontal erkannt) — sechs Szenen, jeder Betrieb genau einmal, statt Wiederholungen; alle Sussmann-Hooks/Bodys, Meike-Takes, Senftleben LeadGen (Benjamin),
# Stimpfle-Hooks/CTA, Irlbacher-Hooks/CTAs (Josef) — Kopfmitte dort 0,15–0,27, mit Zoom auf Mitte würde der Kopf riesig;
# Erwin-Schmidt-Takes mit Meike im Ganzkörper (4) stehen mit Florian im Bild (raus); Erwin Mitarbeiter 1 schaut zur Seite;
# Irlbacher h2/h3 (Josef weit) schaut nach unten; Fischer-Promo (Gruppe am Wagen) ohne Blick in die Kamera.


# ── Gesicht ──────────────────────────────────────────────────────────────
def _cascaden():
    import cv2
    if not hasattr(cv2, 'CascadeClassifier'):
        sys.exit('OpenCV ohne CascadeClassifier — mit /usr/bin/python3 aufrufen')
    return cv2, [cv2.CascadeClassifier(cv2.data.haarcascades + n) for n in ('haarcascade_frontalface_default.xml', 'haarcascade_frontalface_alt2.xml')]


def koepfe(pfad, x_hint=None, verkl=0.5, start=0, anzahl=None):
    """Je Bild der Kopf (cx, cy, h als Anteil) der gemeinten Person: das frontale Gesicht, das x_hint am nächsten liegt
    (sonst das größte); Fehltreffer (winzig, weit weg vom Hinweis) fallen raus."""
    cv2, ges = _cascaden()
    cap, out, n = cv2.VideoCapture(str(pfad)), [], 0
    while True:
        ok, f = cap.read()
        if not ok or (anzahl is not None and n >= start + anzahl): break
        n += 1
        if n - 1 < start: continue
        Hh, Ww = f.shape[:2]
        g = cv2.cvtColor(cv2.resize(f, None, fx=verkl, fy=verkl), cv2.COLOR_BGR2GRAY)
        kand = []
        for m in ges:
            kand = [(x, y, w, h) for x, y, w, h in m.detectMultiScale(g, 1.1, 6, minSize=(24, 24))]
            kand = [r for r in kand if r[3] / verkl / Hh > 0.05]
            if kand: break
        if not kand: out.append(None); continue
        if x_hint is not None:
            r = min(kand, key=lambda r: abs((r[0] + r[2] / 2) / verkl / Ww - x_hint))
            if abs((r[0] + r[2] / 2) / verkl / Ww - x_hint) > 0.15: out.append(None); continue
        else:
            r = max(kand, key=lambda r: r[2] * r[3])
        x, y, w, h = r
        out.append(dict(cx=(x + w / 2) / verkl / Ww, cy=(y + h / 2) / verkl / Hh, h=h / verkl / Hh, W=Ww, H=Hh))
    return out


def median(f, key): return st.median(x[key] for x in f)


# ── Schneiden ────────────────────────────────────────────────────────────
def fenster(sz, cache, token):
    p = cache / f"{sz['id']}-{sz['fen'][-10:]}-{sz['ab']}-{sz['dauer']}.mp4"
    if not p.exists() or p.stat().st_size < 100000:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(sz['ab']), '-headers', f'Authorization: Bearer {token}\r\n',
                        '-i', f"https://www.googleapis.com/drive/v3/files/{sz['fen']}?alt=media&supportsAllDrives=true",
                        '-t', str(sz['dauer']), '-an', '-vf', 'fps=30', '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', str(p)],
                       check=True, timeout=1800)
    return p


def ausschnitt(kopf, sw, sh, haar=HAAR):
    """Randvoller Säulenausschnitt: so wenig Zoom wie möglich, aber Kopf seitlich mittig und Kopfmitte bei ZIEL_Y."""
    cw0, ch0 = sh * W / H, sh
    if cw0 > sw: cw0, ch0 = sw, sw * H / W
    fx, fy = kopf['cx'] * sw, kopf['cy'] * sh
    z_x = cw0 / (2 * min(fx, sw - fx))                          # damit links und rechts vom Kopf je eine halbe Breite Platz ist
    z_y = ZIEL_Y * ch0 / fy                                     # Kopf rückt nur durch Zoom tiefer (Ausschnitt oben bündig)
    z_oben = OBEN_MIN / (kopf['cy'] - haar * kopf['h'])         # Kopfoberkante unter Schräge + Beschriftung (auch 1000 × 555)
    z = max(1.0, z_x, z_y, z_oben)
    cw, ch = cw0 / z, ch0 / z
    x0 = min(max(0, fx - cw / 2), sw - cw)
    ziel_y = max(ZIEL_Y, OBEN_MIN + haar * kopf['h'] * z)          # Kopfmitte so, dass die Kopfoberkante bei ≥ OBEN_MIN liegt
    y0 = min(max(0, fy - ziel_y * ch), sh - ch)
    return z, round(cw), round(ch), round(x0), round(y0)


def szene_schneiden(sz, fen, aus):
    s = sz['bild']
    d = koepfe(fen, sz.get('x'), verkl=0.5, start=s, anzahl=BILDER)
    f = [x for x in d if x]
    if len(f) < BILDER * 0.8: sys.exit(f"{sz['id']}: Kopf nur in {len(f)}/{BILDER} Bildern erkannt")
    kopf = dict(cx=median(f, 'cx'), cy=median(f, 'cy'), h=median(f, 'h'))
    z, cw, ch, x0, y0 = ausschnitt(kopf, f[0]['W'], f[0]['H'], sz.get('haar', HAAR))
    vf = (f"select='between(n\\,{s}\\,{s + BILDER - 1})',setpts=N/30/TB,crop={cw}:{ch}:{x0}:{y0},"
          f"scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(fen), '-vf', vf, '-frames:v', str(BILDER), '-r', '30', '-an',
                    '-c:v', 'libx264', '-crf', '16', '-preset', 'slow', str(aus)], check=True)
    return dict(sekunde=round(sz['ab'] + s / 30, 2), zoom=round(z, 2), quelle_kopf=dict(cx=round(kopf['cx'], 3), cy=round(kopf['cy'], 3), h=round(kopf['h'], 3)))


def bauen():
    cache = Path(os.environ.get('SZENEN_CACHE') or tempfile.mkdtemp(prefix='saeule-'))
    cache.mkdir(parents=True, exist_ok=True)
    token = k.drive_token()
    protokoll, teile = {}, []
    with tempfile.TemporaryDirectory() as d:
        for i, sz in enumerate(SZENEN):
            aus = Path(d) / f'{i:02d}.mp4'
            protokoll[sz['id']] = szene_schneiden(sz, fenster(sz, cache, token), aus)
            print(f"{sz['id']:18s}", protokoll[sz['id']], flush=True)
            teile.append(aus)
        liste = Path(d) / 'liste.txt'; liste.write_text(''.join(f"file '{t}'\n" for t in teile))
        roh = Path(d) / 'roh.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(liste), '-c', 'copy', str(roh)], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(roh), '-an', '-c:v', 'libx264', '-crf', '28', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(ZIEL / 'kunden-szenen-d.mp4')], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(roh), '-an', '-vf', 'scale=360:704', '-c:v', 'libx264', '-crf', '30', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(ZIEL / 'kunden-szenen-m.mp4')], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '0.5', '-i', str(roh), '-frames:v', '1', '-q:v', '4', str(ZIEL / 'kunden-szenen.jpg')], check=True)
    (Path(__file__).with_name('kunden_szenen_saeule.json')).write_text(json.dumps(protokoll, ensure_ascii=False, indent=1), encoding='utf-8')


# ── Prüfen (am fertigen Video) ───────────────────────────────────────────
def pruefen():
    fehler, zeilen = [], []
    betr = [s['betrieb'] for s in SZENEN]
    alle = sorted(set(betr))
    if sorted(betr[:len(alle)]) != alle: fehler.append(f'die ersten {len(alle)} Szenen zeigen nicht jeden Betrieb einmal: {betr[:len(alle)]}')
    for i in range(len(betr)):
        if betr[i] == betr[(i + 1) % len(betr)]: fehler.append(f'{betr[i]} zweimal hintereinander (Szene {i + 1} → {(i + 1) % len(betr) + 1})')
    for i, sz in enumerate(SZENEN):
        d = koepfe(ZIEL / 'kunden-szenen-d.mp4', 0.5, verkl=1.0, start=i * BILDER, anzahl=BILDER)
        f = [x for x in d if x]
        quote = len(f) / BILDER
        if quote < GRENZEN['erkannt_min']:
            fehler.append(f"{sz['id']}: Kopf nur in {quote:.0%} der Bilder frontal"); continue
        cx, cy, h = median(f, 'cx'), median(f, 'cy'), median(f, 'h')
        haar = cy - sz.get('haar', HAAR) * h                   # Kopfoberkante (Haaransatz bzw. Kappe)
        ok = (GRENZEN['y'][0] <= cy <= GRENZEN['y'][1] and GRENZEN['x'][0] <= cx <= GRENZEN['x'][1]
              and haar >= GRENZEN['haar_min'] and h <= sz.get('h_max', GRENZEN['h_max']))
        zeilen.append(f"  {sz['id']:18s} Kopf x={cx:.3f} y={cy:.3f} h={h:.3f} Haaransatz≈{haar:.3f} ({len(f)}/{BILDER} frontal) {'✓' if ok else '✗'}")
        if not ok: fehler.append(f"{sz['id']}: x={cx:.2f} y={cy:.2f} h={h:.2f} Haar={haar:.2f} außerhalb {GRENZEN}")
    return zeilen, fehler


if __name__ == '__main__':
    if '--pruefen' not in sys.argv:
        bauen()
    zeilen, fehler = pruefen()
    print('Folge:', ' → '.join(s['id'] for s in SZENEN)); print(*zeilen, sep='\n')
    if fehler: print('❌', *fehler, sep='\n  '); sys.exit(1)
    print(f"✅ {len(SZENEN)} Szenen, jeder Betrieb zuerst einmal, nie zweimal hintereinander (inkl. Schleife), Kopf mittig "
          f"(y {GRENZEN['y'][0]}–{GRENZEN['y'][1]}), Haaransatz unter {GRENZEN['haar_min']}, Kopf ≤ {GRENZEN['h_max']} (Patrick/Mirjana ≤ 0,22, Yannick ≤ 0,24)")

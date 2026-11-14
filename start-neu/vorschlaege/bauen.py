# Vorschlagsseite (noindex): immer NUR die aktuelle Runde, nie alte Listen mitliefern (Noah, 15.11.2026).
# Runde 3: Startseiten als Paar gedacht wie die abgenommenen Unterseiten: Hero sagt, was wir tun, die Ergebnis-Überschrift ist dasselbe Bild im fertigen Zustand.
from pathlib import Path
import html
PAARE = [
 ('HWM Startseite', 'handwerksmanufaktur.digital', [
  ('Dein Handwerk. Unsere Baustelle.', 'Fertig gemeldet.'), ('Du machst dein Handwerk. Wir den Rest.', 'Erledigt.'),
  ('Volle Bücher. Volle Mannschaft.', 'Voll geworden.'), ('Wir halten dir den Rücken frei.', 'Rücken frei. Bücher voll.'),
  ('Dein Betrieb kann mehr. Wir holen es raus.', 'Rausgeholt.'), ('Gute Arbeit soll man sehen.', 'Gesehen. Angefragt. Beauftragt.'),
  ('Wir bringen Arbeit. Und die Leute dafür.', 'Geliefert.'), ('Dein Betrieb, gut aufgestellt.', 'Aufgestellt.'),
  ('Wir packen mit an.', 'Angepackt.'), ('Dein Betrieb läuft. Wir legen nach.', 'Nachgelegt.')]),
 ('SHK Startseite', 'shk.handwerksmanufaktur.digital', [
  ('Wir schließen dich an.', 'Angeschlossen.'), ('Wir drehen auf.', 'Aufgedreht.'),
  ('Wir bringen deinen Betrieb auf Temperatur.', 'Auf Temperatur.'), ('Wir heizen deinem Betrieb ein.', 'Eingeheizt.'),
  ('Wir sorgen für Durchfluss.', 'Läuft.'), ('Du installierst. Wir liefern nach.', 'Geliefert.'),
  ('Volle Bücher. Volle Mannschaft.', 'Voll.'), ('Monteure und Aufträge. Frei Haus.', 'Zugestellt.'),
  ('Dein Betrieb läuft. Wir halten den Druck.', 'Druck gehalten.'), ('Wir halten deinen Betrieb am Laufen.', 'Läuft weiter.')]),
]
e = html.escape
out = ['<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Überschriften Startseiten</title><style>',
 ':root{--ink:#0B1424;--sub:#4A5666;--line:#DCE3EC;--paper:#F3F6FA;--warm:#C9581A}*{box-sizing:border-box;margin:0;padding:0}body{background:var(--paper);color:var(--ink);font:17px/1.5 Inter,system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased}',
 '.wrap{max-width:860px;margin:0 auto;padding:32px 20px 96px}h1{font-size:clamp(30px,5vw,44px);letter-spacing:-.03em;line-height:1.1;margin-bottom:8px}.lead{color:var(--sub)}h2{font-size:28px;letter-spacing:-.02em;margin:48px 0 12px}h2 small{display:block;font-size:15px;font-weight:400;color:var(--sub);letter-spacing:0}',
 'ol{list-style:none;counter-reset:n;background:#fff;border:1px solid var(--line);border-radius:24px;padding:4px 24px}li{counter-increment:n;display:grid;grid-template-columns:28px 1fr;gap:0 12px;padding:14px 0;border-top:1px solid var(--line)}li:first-child{border-top:0}li::before{content:counter(n);color:var(--sub);font-variant-numeric:tabular-nums;grid-row:1/3}li b{font-size:clamp(20px,3.4vw,26px);letter-spacing:-.02em;line-height:1.2}li span{color:var(--sub);font-size:15px}li span i{font-style:normal;font-weight:600;color:var(--warm)}',
 '</style></head><body><div class="wrap"><h1>Startseiten</h1><p class="lead">Je Nummer ein Paar: oben der Hero, darunter die Überschrift über den Ergebnissen.</p>']
for titel, dom, paare in PAARE:
    out.append(f'<h2>{e(titel)}<small>{dom}</small></h2><ol>' + ''.join(f'<li><b>{e(a)}</b><span>Ergebnisse: <i>{e(b)}</i></span></li>' for a, b in paare) + '</ol>')
out.append('</div></body></html>')
Path(__file__).with_name('index.html').write_text(''.join(out))
print(sum(len(p) for _, _, p in PAARE), 'Paare')

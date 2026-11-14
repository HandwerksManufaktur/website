# Vorschlagsseite (noindex): immer NUR die aktuelle Runde, nie alte Listen mitliefern (Noah, 15.11.2026).
# Runde 3: Startseiten als Paar gedacht wie die abgenommenen Unterseiten: Hero sagt, was wir tun, die Ergebnis-Überschrift ist dasselbe Bild im fertigen Zustand.
from pathlib import Path
import html
PAARE = [
 ('SHK Startseite · Hero', 'schlicht, im SHK-Stil: fette Zeile plus Akzentzeile als eigene Sinneinheit', [(x, '') for x in [
  'Der Partner für SHK-Betriebe|im DACH-Raum.', 'Planbar Monteure.|Planbar Aufträge.', 'Monteure und Aufträge.|Planbar.',
  'Die Agentur für|Sanitär, Heizung und Klima.', 'Der Partner|für SHK-Betriebe.', 'Monteure und Aufträge|für SHK-Betriebe.',
  'Mehr Monteure. Mehr Aufträge.|Planbar aus deinem Umkreis.', 'SHK-Betriebe,|planbar voll.', 'Dein SHK-Betrieb.|Planbar ausgelastet.',
  'Planbar wachsen|im SHK-Handwerk.', 'Marketing|nur für SHK-Betriebe.', 'Für SHK-Betriebe,|die planen wollen.',
  'Monteure finden.|Aufträge gewinnen.', 'Volle Mannschaft.|Volle Auftragsbücher.', 'Die Agentur,|die nur SHK macht.',
  'Über 150 Betriebe.|8 Jahre Handwerk.', 'Sanitär, Heizung, Klima.|Monteure und Aufträge dafür.', 'Dein Umkreis.|Deine Monteure. Deine Aufträge.',
  'Mitarbeiter und Aufträge|für Sanitär, Heizung und Klima.', 'Der Marketing-Partner|für das SHK-Handwerk.']]),
 ('SHK · Überschrift über den Ergebnissen', 'jetzt: Ergebnisse unserer Kunden.', [(x, '') for x in [
  'Ergebnisse|unserer Kunden.', 'Das kam|bei unseren Kunden an.', 'Zahlen|aus SHK-Betrieben.', 'So lief es|bei SHK-Betrieben.',
  'Fünf Betriebe.|Fünf Ergebnisse.', 'Das haben|unsere Kunden erreicht.', 'Monteure eingestellt.|Aufträge gewonnen.',
  'Aus der Praxis.|Mit Zahlen.', 'Kundenergebnisse|aus dem SHK-Handwerk.', 'Was SHK-Betriebe|mit uns erreicht haben.']]),
 ('HWM · Überschrift über den Ergebnissen', 'passend zu „Dein Handwerk. Unsere Baustelle.“', [(x, '') for x in [
  'Ergebnisse unserer Kunden.', 'Unsere Baustellen. Ihre Ergebnisse.', 'Fertige Baustellen.', 'Das haben unsere Kunden erreicht.',
  'Das kam bei unseren Kunden an.', 'Zahlen aus den Betrieben.', 'So lief es bei unseren Kunden.', 'Von diesen Baustellen kommen wir.',
  'Kundenergebnisse aus dem Handwerk.', 'Was unsere Kunden davon haben.']]),
]
e = html.escape
def t(x):
    a, _, b = x.partition('|')
    return e(a) + (f' <em>{e(b)}</em>' if b else '')
out = ['<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Überschriften Startseiten</title><style>',
 ':root{--ink:#0B1424;--sub:#4A5666;--line:#DCE3EC;--paper:#F3F6FA;--warm:#C9581A}*{box-sizing:border-box;margin:0;padding:0}body{background:var(--paper);color:var(--ink);font:17px/1.5 Inter,system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased}',
 '.wrap{max-width:860px;margin:0 auto;padding:32px 20px 96px}h1{font-size:clamp(30px,5vw,44px);letter-spacing:-.03em;line-height:1.1;margin-bottom:8px}.lead{color:var(--sub)}h2{font-size:28px;letter-spacing:-.02em;margin:48px 0 12px}h2 small{display:block;font-size:15px;font-weight:400;color:var(--sub);letter-spacing:0}',
 'ol{list-style:none;counter-reset:n;background:#fff;border:1px solid var(--line);border-radius:24px;padding:4px 24px}li{counter-increment:n;display:grid;grid-template-columns:28px 1fr;gap:0 12px;padding:14px 0;border-top:1px solid var(--line)}li:first-child{border-top:0}li::before{content:counter(n);color:var(--sub);font-variant-numeric:tabular-nums;grid-row:1/3}li b{font-size:clamp(20px,3.4vw,26px);letter-spacing:-.02em;line-height:1.2}li span{color:var(--sub);font-size:15px}li span i{font-style:normal;font-weight:600;color:var(--warm)}li em{font-family:Georgia,serif;font-weight:400;font-style:italic;color:var(--warm);letter-spacing:-.01em}li span i em{font-weight:400;font-size:17px}',
 '</style></head><body><div class="wrap"><h1>Startseiten</h1><p class="lead">Nenn mir Block und Nummer.</p>']
for titel, dom, paare in PAARE:
    out.append(f'<h2>{e(titel)}<small>{dom}</small></h2><ol>' + ''.join(f'<li><b>{t(a)}</b></li>' for a, b in paare) + '</ol>')
out.append('</div></body></html>')
Path(__file__).with_name('index.html').write_text(''.join(out))
print(sum(len(p) for _, _, p in PAARE), 'Paare')

# Vorschlagsseite (noindex): immer NUR die aktuelle Runde, nie alte Listen mitliefern (Noah, 15.11.2026).
# Runde 3: Startseiten als Paar gedacht wie die abgenommenen Unterseiten: Hero sagt, was wir tun, die Ergebnis-Überschrift ist dasselbe Bild im fertigen Zustand.
from pathlib import Path
import html
PAARE = [
 ('HWM Startseite · mutig', 'Bau-Welt, zieht sich durch zu Rohbau, Schlüsselübergabe und Richtfest auf den Unterseiten', [
  ('Dein Handwerk. Unsere Baustelle.', 'Abgenommen.'), ('Wir sind dein Bautrupp.', 'Fertiggestellt.'),
  ('Du baust für andere. Wir bauen für dich.', 'Gebaut.'), ('Wir bauen an deinem Betrieb.', 'Steht.'),
  ('Wir legen das Fundament. Du baust drauf.', 'Fundament steht.'), ('Wir ziehen deinen Betrieb hoch.', 'Hochgezogen.'),
  ('Baustelle Betrieb? Übernehmen wir.', 'Übergeben.'), ('Wir machen Nägel mit Köpfen.', 'Sitzt.'),
  ('Wir setzen noch einen drauf.', 'Draufgesetzt.'), ('Dein Betrieb, schlüsselfertig.', 'Schlüssel übergeben.'),
  ('Wir bauen aus. Du baust weiter.', 'Ausgebaut.'), ('Handwerk für dein Handwerk.', 'Handarbeit.'),
  ('Wir richten das.', 'Gerichtet.'), ('Erst der Plan. Dann der Bau.', 'Nach Plan gebaut.'),
  ('Dein Betrieb ist unsere Baustelle.', 'Baustelle geräumt.')]),
 ('HWM Startseite · normal', 'klar und ohne Bild', [
  ('Mehr Aufträge und Mitarbeiter für deinen Betrieb.', 'Das kam bei unseren Kunden an.'), ('Der Partner für Handwerksbetriebe.', 'So lief es bei unseren Kunden.'),
  ('Website, Kunden und Mitarbeiter aus einer Hand.', 'Ergebnisse unserer Kunden.'), ('Wir machen Handwerksbetriebe sichtbar.', 'So sichtbar wurden unsere Kunden.'),
  ('Mehr Anfragen. Mehr Bewerbungen. Aus deinem Umkreis.', 'Zahlen aus den Betrieben.'), ('Dein Betrieb, voll ausgelastet.', 'So voll wurde es.'),
  ('Über 130 Betriebe arbeiten mit uns.', 'Das haben sie davon.'), ('Seit 8 Jahren nur Handwerk.', 'Was dabei rauskommt.'),
  ('Damit dein Betrieb gefunden wird.', 'So wurden sie gefunden.'), ('Aufträge und Leute für dein Handwerk.', 'So viele kamen.'),
  ('Marketing, das auf der Baustelle ankommt.', 'Angekommen.'), ('Wir kümmern uns um Kunden und Mitarbeiter.', 'Das Ergebnis.'),
  ('Dein Handwerk verdient mehr Anfragen.', 'Mehr Anfragen, belegt.'), ('Die Agentur, die nur Handwerk macht.', 'Ergebnisse aus dem Handwerk.'),
  ('Gute Betriebe sollen voll sein.', 'Voll geworden.')]),
 ('SHK Startseite · mutig', 'SHK-Welt, zieht sich durch zu Hahn aufdrehen, nachfüllen und verlegen auf den Unterseiten', [
  ('Wir schließen dich an.', 'Angeschlossen.'), ('Wir drehen auf.', 'Aufgedreht.'),
  ('Wir bringen deinen Betrieb auf Temperatur.', 'Auf Temperatur.'), ('Wir heizen deinem Betrieb ein.', 'Eingeheizt.'),
  ('Wir sorgen für Durchfluss.', 'Läuft.'), ('Du installierst. Wir liefern nach.', 'Geliefert.'),
  ('Wir halten den Druck.', 'Druck gehalten.'), ('Wir bringen Wärme in dein Auftragsbuch.', 'Warm gelaufen.'),
  ('Wir legen dir die Leitung.', 'Leitung steht.'), ('Wasser marsch.', 'Volles Rohr.'),
  ('Wir entlüften deinen Betrieb.', 'Läuft wieder rund.'), ('Wir machen dicht, wo es tropft.', 'Dicht.'),
  ('Neuer Anschluss für deinen Betrieb.', 'Angeschlossen und abgenommen.'), ('Dein Betrieb unter Volllast.', 'Volllast.'),
  ('Vorlauf für deinen Betrieb.', 'Rücklauf: gut.')]),
 ('SHK Startseite · normal', 'klar und ohne Bild', [
  ('Der Partner für SHK-Betriebe.', 'So lief es bei unseren Kunden.'), ('Monteure und Aufträge für SHK-Betriebe.', 'Das kam bei unseren Kunden an.'),
  ('Mehr Monteure. Mehr Bäder. Aus deinem Umkreis.', 'Zahlen aus den Betrieben.'), ('Wir bringen SHK-Betrieben Monteure und Aufträge.', 'So viele kamen.'),
  ('Dein SHK-Betrieb, voll besetzt und ausgelastet.', 'So voll wurde es.'), ('Über 150 Betriebe. 8 Jahre Handwerk.', 'Das haben sie davon.'),
  ('Marketing nur für SHK.', 'Ergebnisse aus SHK-Betrieben.'), ('Monteure finden. Aufträge gewinnen.', 'Gefunden und gewonnen.'),
  ('Damit dir weder Leute noch Aufträge fehlen.', 'Fehlt nichts mehr.'), ('Die Agentur für Heizung, Sanitär und Klima.', 'Was dabei rauskommt.'),
  ('Bad und Wärmepumpe: Aufträge aus deinem Umkreis.', 'Aufträge, belegt.'), ('Wir kennen dein Gewerk.', 'Fünf Betriebe, fünf Ergebnisse.'),
  ('Planbar Monteure. Planbar Aufträge.', 'Planbar, belegt.'), ('Dein Umkreis hat mehr zu bieten.', 'Das war drin.'),
  ('Für SHK-Betriebe, die wachsen wollen.', 'So sind sie gewachsen.')]),
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

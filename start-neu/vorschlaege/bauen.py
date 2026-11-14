# Vorschlagsseite: Überschriften für HWM und SHK (Noah, 15.11.2026). Bau: python bauen.py → index.html (noindex)
from pathlib import Path
import html
T = lambda *z: list(z)
UEB = T('Du führst nur noch das Gespräch.', 'Suchen ist unser Teil.', 'Wir drehen, schalten, filtern.', 'Von der Anzeige bis zur Bewerbung.', 'Drei Schritte bis zum Vorstellungsgespräch.')
AUF = T('Du fährst hin. Den Rest machen wir.', 'Kein Portal, kein Mitbieter.', 'Wir filtern, bevor du losfährst.', 'Von der Anzeige bis zum Vor-Ort-Termin.', 'Drei Schritte bis zum Aufmaß.')
WEB = T('Du gibst frei. Wir bauen.', 'Du schreibst keinen einzigen Satz.', 'Vom ersten Foto bis zum Livegang.', 'Wir bauen. Du schaust drüber.', 'In drei Schritten online.')
SEITEN = [
 ('SHK', 'shk.handwerksmanufaktur.digital', [
  ('Startseite', [
   ('Hero', 'Der Partner für SHK-Betriebe. Seit 8 Jahren im Handwerk.', T('Volle Auftragsbücher. Volle Mannschaft.', 'Wir besorgen, was im SHK-Betrieb fehlt.', 'Du montierst. Wir besorgen den Rest.', 'Dein Betrieb läuft. Wir sorgen für Nachschub.', 'Mehr Monteure. Bessere Aufträge.', 'Der SHK-Betrieb, den im Umkreis jeder kennt.', 'Seit 8 Jahren nur Handwerk.', 'Rohre verlegst du. Den Draht zum Kunden legen wir.', 'Monteure, Aufträge, Website. Wir packen an.', 'Wir machen SHK-Betriebe bekannt im Ort.')),
   ('Leistungen', 'Drei Baustellen übernehmen wir für SHK-Betriebe.', T('Drei Baustellen. Ein Trupp.', 'Was fehlt dir gerade?', 'Sag, wo es klemmt.', 'Leute, Aufträge, Auftritt.', 'Drei Gewerke. Ein Ansprechpartner.')),
   ('Ergebnisse', 'So viel kam bei unseren Kunden an.', T('Abgerechnet wird am Schluss.', 'Zahlen von der Baustelle.', 'Das kam dabei raus.', 'Gezählt und aufgeschrieben.', 'Fünf Betriebe, fünf Abrechnungen.')),
  ]),
  ('Monteure', [
   ('Hero', 'Die Monteursuche übernehmen wir. Aus deinem Umkreis.', T('Dein nächster Monteur wohnt um die Ecke.', 'Wir suchen. Du stellst ein.', 'Die Stelle bleibt nicht leer.', 'Dein Monteur arbeitet noch woanders.', 'Gute Monteure suchen nicht. Wir finden sie.')),
   ('Das übernehmen wir', '', UEB),
   ('Ergebnisse', '25 Bewerbungen in 4 Wochen.', T('Stelle besetzt nach 4 Wochen.', 'Einer von 25 fängt an.', 'So lief es bei Erwin Schmidt & Sohn.', 'Erst gezählt, dann eingestellt.', '25 Bewerbungen. Ein neuer Kollege.')),
  ]),
  ('Aufträge', [
   ('Hero', 'Deine Bad-Anfragen übernehmen wir. Aus deinem Umkreis.', T('Bäder, die du bauen willst.', 'Die Anfrage gehört dir allein.', 'Dein Kalender, voll mit Bädern.', 'Du fährst nur noch zum Termin.', 'Aufträge nach Maß.')),
   ('Das übernehmen wir', '', AUF),
   ('Ergebnisse', '21 Bad-Anfragen in 2 Monaten.', T('7 Anfragen in den ersten 3 Tagen.', 'Ausgelastet und trotzdem gefragt.', 'So lief es bei Senftleben.', 'Zehn Termine, kein Portal.', '21 Anfragen. Alle für einen Betrieb.')),
  ]),
  ('Website', [
   ('Hero', 'Deine Website übernehmen wir. In zwei bis drei Wochen.', T('In drei Wochen steht deine Website.', 'Eine Seite je Leistung.', 'Wer dich googelt, ruft an.', 'Schluss mit der Seite von früher.', 'Deine Website, gebaut mit deinen Leuten.')),
   ('Das übernehmen wir', '', WEB),
   ('Ergebnisse', '', T('Frisch vom Bau.', 'Schau rein, bevor du fragst.', 'Seiten, die Anfragen bringen.', 'Gebaut für Betriebe wie deinen.', 'So sehen unsere SHK-Seiten aus.')),
  ]),
 ]),
 ('HWM', 'handwerksmanufaktur.digital', [
  ('Startseite', [
   ('Hero', 'Der Partner für Handwerksbetriebe.', T('Dein Handwerk verdient volle Bücher.', 'Wir machen deinen Betrieb im Ort bekannt.', 'Du baust. Wir sorgen für Nachschub.', 'Der Betrieb, den im Umkreis jeder kennt.', 'Über 130 Betriebe. Ein Handwerk: deins.', 'Wir bringen dein Handwerk an den Mann.', 'Gute Arbeit spricht sich rum. Wir helfen nach.', 'Aufträge und Leute für dein Handwerk.', 'Seit 8 Jahren nur Handwerk.', 'Website, Kunden, Mitarbeiter. Aus einer Hand.')),
   ('Leistungen', 'Drei Baustellen übernehmen wir für dich.', T('Drei Baustellen. Eine Mannschaft.', 'Was fehlt dir gerade?', 'Sag, wo es klemmt.', 'Auftritt, Aufträge, Leute.', 'Drei Gewerke. Ein Trupp.')),
   ('Ergebnisse', 'So viel kam bei unseren Kunden an.', T('Abgerechnet wird am Schluss.', 'Zahlen von der Baustelle.', 'Das kam dabei raus.', 'Gezählt und aufgeschrieben.', 'So lief es bei unseren Kunden.')),
  ]),
  ('Websites', [
   ('Hero', 'Die Website, die abends um zehn den Auftrag holt.', T('Deine Website arbeitet, wenn du Feierabend hast.', 'Die Seite, die den Auftrag holt.', 'Wer dich googelt, ruft an.', 'Schluss mit der Seite von früher.', 'Dein bester Verkäufer hat nie Urlaub.')),
   ('Das übernehmen wir', '', WEB),
   ('Ergebnisse', 'So sehen unsere Seiten aus.', T('Frisch vom Bau.', 'Schau rein, bevor du fragst.', 'Seiten, die Anfragen bringen.', 'Gebaut für Betriebe wie deinen.', 'Jedes Gewerk, eine eigene Handschrift.')),
  ]),
  ('Google (SEO)', [
   ('Hero', 'Dein nächster Kunde googelt gerade.', T('Wer oben steht, bekommt den Anruf.', 'Seite 2 liest keiner.', 'Dein Ort, dein Gewerk, dein Platz bei Google.', 'Gefunden werden ist kein Zufall.', 'Oben steht, wer dranbleibt.')),
   ('Das übernehmen wir', '', T('Wir bringen dich nach oben.', 'Eine Seite je Leistung und Ort.', 'Du arbeitest. Wir klettern.', 'Monat für Monat ein Stück höher.', 'Um Google kümmern wir uns.')),
   ('Ergebnisse', '77 Kundenseiten stehen auf Seite 1.', T('77-mal Seite 1.', 'Oben angekommen.', 'Nachgezählt bei Google.', 'Schwarz auf weiß bei Google.', '77 Seiten, alle ganz vorn.')),
  ]),
  ('Foto & Video', [
   ('Hero', 'Fotos, auf denen man deinen Betrieb wiedererkennt.', T('Dein Betrieb, wie er wirklich aussieht.', 'Ein Drehtag. Material für alles.', 'Deine Leute vor der Kamera.', 'Schluss mit Stockfotos.', 'Man sieht, wer hier arbeitet.')),
   ('Das übernehmen wir', '', T('Wir kommen mit der Kamera.', 'Ein Tag bei dir im Betrieb.', 'Du arbeitest. Wir drehen.', 'Vom Drehtag bis zum fertigen Film.', 'Wir drehen, wo du arbeitest.')),
   ('Ergebnisse', 'Diese Filme sind am Drehtag entstanden.', T('Frisch vom Drehtag.', 'Das kam beim Drehen raus.', 'Ein Tag, diese Bilder.', 'So sieht das bei unseren Kunden aus.', 'Ungestellt und aus dem Betrieb.')),
  ]),
  ('Neue Kunden', [
   ('Hero', 'Die Aufträge, die du willst. Nur für deinen Betrieb.', T('Aufträge, die du dir aussuchst.', 'Die Anfrage gehört dir allein.', 'Dein Kalender, voll mit Wunschaufträgen.', 'Du fährst nur noch zum Termin.', 'Aufträge nach Maß.')),
   ('Das übernehmen wir', '', AUF),
   ('Ergebnisse', '', T('21 Bad-Anfragen in 2 Monaten.', '7 Anfragen in den ersten 3 Tagen.', 'Ausgelastet und trotzdem gefragt.', 'Abgerechnet wird am Schluss.', 'So lief es bei unseren Kunden.')),
  ]),
  ('Neue Mitarbeiter', [
   ('Hero', 'Leute, die bei dir anfangen wollen. Aus deinem Umkreis.', T('Dein nächster Geselle wohnt um die Ecke.', 'Wir suchen. Du stellst ein.', 'Die Stelle bleibt nicht leer.', 'Gute Leute suchen nicht. Wir finden sie.', 'Dein nächster Mitarbeiter arbeitet noch woanders.')),
   ('Das übernehmen wir', '', UEB),
   ('Ergebnisse', '', T('25 Bewerbungen in 4 Wochen.', 'Stelle besetzt nach 4 Wochen.', 'Einer von 25 fängt an.', 'So lief es bei Erwin Schmidt & Sohn.', 'Erst gezählt, dann eingestellt.')),
  ]),
 ]),
]

# Die eine Fassung im Ton von oevermann & oevermann (Noah, 15.11.2026). Ihr Muster auf oeoe.de gelesen:
# Redewendung des Kunden-Gewerks wörtlich nehmen, kurze Sätze mit Punkt, Paare „von … bis …“, Dreiklang.
FASSUNG = [
 ('SHK', [
  ('Startseite', 'Wir schließen SHK-Betriebe an.', 'An Monteure, an Aufträge, ans Netz.', 'Drei Anschlüsse. Ein Partner.', 'Läuft. Nachgemessen bei fünf Betrieben.'),
  ('Monteure', 'Fehlt Druck im Team? Wir füllen nach.', 'Monteure aus deinem Umkreis.', 'Von der Anzeige bis zum Handschlag.', '25 Bewerbungen. 4 Wochen. 1 Neuer.'),
  ('Aufträge', 'Wir drehen dir den Hahn auf.', 'Bad und Wärmepumpe, aus deinem Umkreis.', 'Von der Anzeige bis zum Aufmaß.', '21 Anfragen. 2 Monate. 0 Mitbieter.'),
  ('Website', 'Wir verlegen deinen Betrieb ins Netz.', 'In zwei bis drei Wochen.', 'Vom ersten Foto bis zur Abnahme.', 'Frisch verlegt.'),
 ]),
 ('HWM', [
  ('Startseite', 'Wir bringen dein Handwerk unter die Leute.', '', 'Drei Gewerke. Eine Hand.', 'Hand drauf. Hier sind die Zahlen.'),
  ('Websites', 'Wir bauen. Du ziehst ein.', 'Deine Website, schlüsselfertig.', 'Vom Rohbau bis zur Schlüsselübergabe.', 'Bezugsfertig.'),
  ('Google (SEO)', 'Ganz oben ist dein Platz.', 'Wir stellen das Gerüst.', 'Vom ersten Suchwort bis Seite 1.', '77-mal Richtfest.'),
  ('Foto & Video', 'Wir setzen dein Handwerk ins Licht.', 'Gedreht bei dir im Betrieb.', 'Vom ersten Bild bis zum fertigen Film.', 'Abgedreht.'),
  ('Neue Kunden', 'Wir füllen dein Auftragsbuch.', 'Seite für Seite, aus deinem Umkreis.', 'Von der Anzeige bis zum Aufmaß.', 'Schwarz auf weiß.'),
  ('Neue Mitarbeiter', 'Verstärkung ist unterwegs.', 'Aus deinem Umkreis.', 'Von der Anzeige bis zum Handschlag.', '25 Bewerbungen. 4 Wochen. 1 Neuer.'),
 ]),
]

# Runde 2 (Noah, 15.11.2026): Startseiten-Hero, Ergebnisse, Alternativen SHK Aufträge/Monteure mit Bau-Vergleich
RUNDE2 = [
 ('HWM Startseite, Hero', T('Wir bringen dein Handwerk unter die Leute.', 'Wir legen das Fundament. Du baust drauf.', 'Das Gewerk, das dir noch fehlt.', 'Du baust Häuser. Wir bauen deinen Ruf.', 'Dein Betrieb, schlüsselfertig sichtbar.', 'Wir machen Nägel mit Köpfen.', 'Handwerk für dein Handwerk.', 'Dein Handwerk hat goldenen Boden. Wir legen ihn frei.', 'Wir bauen an deinem Betrieb mit.', 'Alles aus einer Hand. Wie auf einer guten Baustelle.')),
 ('SHK Startseite, Hero', T('Wir schließen SHK-Betriebe an.', 'Wir bringen deinen Betrieb auf Temperatur.', 'Wir sorgen für Druck auf der Leitung.', 'Der Anschluss, der deinem Betrieb fehlt.', 'Aufträge im Vorlauf. Monteure im Rücklauf.', 'Dein Betrieb, hydraulisch abgeglichen.', 'Du planst Anlagen. Wir planen deine Auslastung.', 'Wir verlegen die Leitung zu Kunden und Monteuren.', 'Wir halten deinen Betrieb am Laufen.', 'Alles dicht. Alles voll. Alles läuft.')),
 ('SHK Aufträge, Hero (statt „Wir drehen dir den Hahn auf.“)', T('Du baust das Bad. Wir bauen die Nachfrage.', 'Wir bauen vor. Du baust ein.', 'Anfragen, anschlussfertig geliefert.', 'Wir stellen den Zulauf sicher.', 'Wir legen dir die Aufträge vor die Tür.')),
 ('SHK Monteure, Hero (statt „Fehlt Druck im Team? Wir füllen nach.“)', T('Du baust Bäder. Wir bauen dein Team.', 'Wir stocken dein Team auf.', 'Wir bauen dein Team aus.', 'Bewerbungen, anschlussfertig geliefert.', 'Verstärkung für deine Kolonne.')),
 ('SHK, Überschrift über den Ergebnissen', T('Druckprobe bestanden.', 'Dicht. Geprüft. Abgenommen.', 'Abgenommen.', 'Das Abnahmeprotokoll.', 'Läuft.', 'Unterm Strich.', 'Nachgemessen.', 'Übergeben und abgenommen.', 'Hält, was wir versprechen.', 'Hand drauf.')),
 ('HWM, Überschrift über den Ergebnissen', T('Abgenommen.', 'Das Abnahmeprotokoll.', 'Schlüsselübergabe.', 'Richtfest.', 'Bauabnahme bestanden.', 'Sitzt, passt und hält.', 'Steht.', 'Unterm Strich.', 'Nachgemessen.', 'Hand drauf.')),
]
e = html.escape
out = ['<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Überschriften-Vorschläge</title><style>',
 ':root{--ink:#0B1424;--sub:#4A5666;--line:#DCE3EC;--paper:#F3F6FA;--kalt:#1E90E8}*{box-sizing:border-box;margin:0;padding:0}body{background:var(--paper);color:var(--ink);font:17px/1.5 Inter,system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased}',
 '.wrap{max-width:860px;margin:0 auto;padding:32px 20px 96px}h1{font-size:clamp(30px,5vw,44px);letter-spacing:-.03em;line-height:1.1;margin-bottom:8px}.lead{color:var(--sub);margin-bottom:24px}',
 'nav{position:sticky;top:0;background:rgba(243,246,250,.85);backdrop-filter:blur(16px);padding:12px 0;display:flex;gap:8px;flex-wrap:wrap;z-index:2}nav a{min-height:44px;display:inline-flex;align-items:center;padding:0 16px;border-radius:999px;background:#fff;border:1px solid var(--line);color:var(--ink);text-decoration:none;font-weight:600;font-size:15px}',
 'h2{font-size:28px;letter-spacing:-.02em;margin:48px 0 4px}h2 small{display:block;font-size:15px;font-weight:400;color:var(--sub);letter-spacing:0}h3{font-size:20px;letter-spacing:-.01em;margin:32px 0 12px}',
 '.block{background:#fff;border:1px solid var(--line);border-radius:24px;padding:20px 24px;margin-bottom:12px}.block h4{font-size:15px;color:var(--kalt);margin-bottom:2px}.jetzt{font-size:15px;color:var(--sub);margin-bottom:10px}ol{list-style:none;counter-reset:n}li{counter-increment:n;display:flex;gap:12px;padding:8px 0;border-top:1px solid var(--line);font-weight:600;letter-spacing:-.01em}li::before{content:counter(n);flex:none;width:24px;color:var(--sub);font-weight:400;font-variant-numeric:tabular-nums}',
 '.fass .h{font-size:clamp(24px,4vw,34px);font-weight:800;letter-spacing:-.03em;line-height:1.12;margin:6px 0 14px}.fass .h span{color:#F5762B}.fass dl{display:grid;grid-template-columns:auto 1fr;gap:6px 16px;border-top:1px solid var(--line);padding-top:12px}.fass dt{font-size:15px;color:var(--sub)}.fass dd{font-weight:600}@media(max-width:560px){.fass dl{grid-template-columns:1fr;gap:2px}.fass dd{margin-bottom:8px}}</style></head><body><div class="wrap"><h1>Überschriften</h1><p class="lead">Oben die neuen Vorschläge, darunter die Fassung je Seite. Die HWM-Unterseiten sind schon eingebaut.</p><nav><a href="#r2">Neue Vorschläge</a><a href="#f-shk">Fassung SHK</a><a href="#f-hwm">Fassung HWM</a><a href="#shk">Alte Liste</a></nav>']
out.append('<h2 id="r2">Neue Vorschläge<small>Nenn mir Block und Nummer.</small></h2>')
for titel, vs in RUNDE2:
    out.append(f'<div class="block"><h4>{e(titel)}</h4><ol>' + ''.join(f'<li>{e(v)}</li>' for v in vs) + '</ol></div>')
for kurz, seiten in FASSUNG:
    out.append(f'<h2 id="f-{kurz.lower()}">{kurz}</h2>')
    for name, h1, h1b, ueb, erg in seiten:
        out.append(f'<div class="block fass"><h4>{e(name)}</h4><p class="h">{e(h1)}<br><span>{e(h1b)}</span></p><dl><dt>Das übernehmen wir</dt><dd>{e(ueb)}</dd><dt>Ergebnisse</dt><dd>{e(erg)}</dd></dl></div>')
out.append('<h2 style="margin-top:72px">Alte Liste<small>die 160 Vorschläge von vorher</small></h2>')
for kurz, dom, seiten in SEITEN:
    out.append(f'<h2 id="{kurz.lower()}">{kurz}<small>{dom}</small></h2>')
    for name, bloecke in seiten:
        out.append(f'<h3>{e(name)}</h3>')
        for titel, jetzt, vs in bloecke:
            j = f'<p class="jetzt">Jetzt: {e(jetzt)}</p>' if jetzt else ''
            out.append(f'<div class="block"><h4>{e(titel)}</h4>{j}<ol>' + ''.join(f'<li>{e(v)}</li>' for v in vs) + '</ol></div>')
out.append('</div></body></html>')
Path(__file__).with_name('index.html').write_text(''.join(out))
print(sum(len(vs) for _,_,s in SEITEN for _,b in s for _,_,vs in b), 'Vorschläge')

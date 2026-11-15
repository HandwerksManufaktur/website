# Vorschlagsseite (noindex): immer NUR die aktuelle Runde, nie alte Listen mitliefern (Noah, 15.11.2026).
# Stand 15.11.2026 18:00: keine offene Runde. Die letzte Runde (10 Schlusssätze für Über uns) hat Noah komplett
# abgelehnt („Lass den letzten Satz einfach bei beiden Seiten weg … schon wieder so viele Beispiele dabei, die so gar
# nicht gepasst haben“). Sie steht unten als Negativprobe im Selbsttest.
#
# Vorschlags-Prüfliste (agenten/helena/pruefliste.md, Abschnitt „Eigene Seiten HWM + SHK · Text-Vorschläge“):
# pruefen() bricht den Bau ab, wenn ein Vorschlag eine messbare Ursache der abgelehnten Runden trägt.
#   python3 bauen.py              baut index.html (nur wenn pruefen() grün)
#   python3 bauen.py --selbsttest Mutationsprobe: jede Negativprobe muss rot, jede Positivprobe grün sein
import html
import re
import sys
from pathlib import Path

N = 'Noah Seelau, Gründer'
# (Titel, Hinweis, [(kleine Zeile, Überschrift, Text, Unterschrift)])
BLOECKE = []

# ---------------------------------------------------------------- Vorschlags-Prüfung
# V3 Füllsatz am Schluss: anbiedernd, flapsig oder Handlungsaufforderung (abgelehnt 15.11.: „Und genau das setzen
# wir jetzt für deinen Betrieb um.“, „Wenn du Lust hast, lass uns einfach mal quatschen.“ und alle 10 danach)
SCHLUSS_VERBOTEN = [
    r'\bLust\b', r'quatsch', r'\bfreu', r'ruf (mich |uns )?einfach an', r'meld(e|et) (dich|euch)',
    r'genau das setzen wir', r'(erzähl|zeig)e? ich dir gern', r'erreichst du mich', r'kennenzulernen',
    r'lass uns (doch )?(einfach )?(mal )?schauen', r'um den Rest kümmern wir uns', r'wovon sie reden',
    r'im Erstgespräch', r'am Telefon',
]
# V2 Insider- und Amtswörter als Pointe, SHK-Wortspiele (abgelehnt 15.11.: „Ergebnisse richtig, richtig schlecht“,
# „Bei SHK sind die ganzen Mutigen komplett scheiße“)
INSIDER = [
    r'hydraulisch', r'Druckprobe', r'Abnahmeprotokoll', r'entlüft', r'Wasser marsch', r'Rücklauf', r'Vorlauf',
    r'auf Temperatur', r'heiz\w* \w* ?ein\b', r'schließen \w+ an\b', r'drehen (dir )?(den Hahn )?auf\b',
    r'Durchfluss', r'Nägel mit Köpfen', r'goldenen Boden',
]
# V1 Werbetexter-Pointen und KI-Wendungen, die Noah wörtlich abgelehnt hat
PHRASEN = [
    r'komme aus einer Handwerkerfamilie', r'keine Lust', r'Einer musste', r'Meisterbrief hängt',
    r'kenne die Betriebe von innen', r'Werbung (kommt|immer) als Letztes', r'Marketing-Deutsch',
    r'bester Verkäufer', r'nie Urlaub', r'abends um zehn', r'gebunden', r'Mindestlaufzeit',
    r'Recruiting', r'Heizung, Sanitär',
]
# V4 Zahl als Komma-Anhängsel („, über 150 bisher“, „, für über 150 Betriebe“)
KOMMA_ZAHL = re.compile(r',\s+(für\s+)?(über|mehr als|rund|knapp)\s+\d+[^.!?]*[.!?]?$')
# V5 Werkzeuge statt Ergebnis in Unterzeilen (Noah 15.11.: „Ich will nicht Anzeigen, Bewerbungen, Website in den
# Vordergrund stellen … das Ergebnis“)
WERKZEUG_TRIO = re.compile(r'(Website|Anzeigen|Bewerbungen|Google)\W+(und\s+)?(Website|Anzeigen|Bewerbungen|Google)'
                           r'\W+(und\s+)?(Website|Anzeigen|Bewerbungen|Google)', re.I)
GENERISCH = {'schlusssatz', 'unterzeile', 'überschrift', 'text', 'titel', 'über', 'uns'}


def saetze(t):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', t or '') if len(s.split()) >= 4]


def norm(s):
    return re.sub(r'[^\wäöüß ]', '', s.lower()).strip()


def pruefen(bloecke):
    """Gibt eine Liste von Befunden zurück, leer = grün."""
    f = []
    for titel, _, liste in bloecke:
        schluss_block = 'schluss' in titel.lower() or any('schluss' in (kl or '').lower() for kl, *_ in liste)
        unterzeile_block = 'unterzeile' in titel.lower() or any('unterzeile' in (kl or '').lower() for kl, *_ in liste)
        gesehen = {}
        for i, (kl, hh, tx, sig) in enumerate(liste, 1):
            alles = ' '.join(x for x in (kl, hh.replace('|', ' '), tx) if x)
            wo = f'{titel} #{i}'
            # V1 Gedankenstrich, X-statt-Y, abgelehnte Wendungen
            if '–' in alles or '—' in alles:
                f.append(f'{wo}: Gedankenstrich')
            if re.search(r'\bsondern\b', alles):
                f.append(f'{wo}: „sondern“ (X-statt-Y)')
            for p in PHRASEN:
                if re.search(p, alles, re.I):
                    f.append(f'{wo}: abgelehnte Wendung /{p}/')
            # V2 Insider/Wortspiel
            for p in INSIDER:
                if re.search(p, alles, re.I):
                    f.append(f'{wo}: Insider-/Wortspiel /{p}/')
            # V3 Schlusssätze ohne Anbiederung
            letzter = (saetze(tx) or [tx or hh])[-1] if (tx or hh) else ''
            if schluss_block or (tx and len(saetze(tx)) >= 3):
                for p in SCHLUSS_VERBOTEN:
                    if re.search(p, letzter, re.I):
                        f.append(f'{wo}: Schlusssatz anbiedernd/flapsig /{p}/')
            # V4 Komma-Anhängsel
            for s in saetze(tx) + [tx or '']:
                if KOMMA_ZAHL.search(s):
                    f.append(f'{wo}: Zahl als Komma-Anhängsel „{s[-40:]}“')
                    break
            # V5 Werkzeuge statt Ergebnis
            if unterzeile_block and WERKZEUG_TRIO.search(alles):
                f.append(f'{wo}: Unterzeile zählt Werkzeuge auf statt Ergebnis')
            # V6 kleine Zeile und Überschrift sagen nicht dasselbe
            if kl and hh:
                a = {w for w in norm(kl).split() if len(w) >= 5} - GENERISCH
                b = {w for w in norm(hh).split() if len(w) >= 5}
                if a & b:
                    f.append(f'{wo}: kleine Zeile und Überschrift doppeln {sorted(a & b)}')
            # V7 wirklich verschiedene Fassungen: kein Satz in zwei Vorschlägen desselben Blocks
            for s in saetze(tx) + ([hh] if hh and len(hh.split()) >= 4 else []):
                k = norm(s)
                if k in gesehen and gesehen[k] != i:
                    f.append(f'{wo}: Satz steht schon in #{gesehen[k]}: „{s[:50]}“')
                gesehen.setdefault(k, i)
        # V8 Vorschläge eines Blocks nicht nur getauschter Schlusssatz: gleicher Anfang (erste 6 Wörter) höchstens 2x
        anfaenge = {}
        for i, (kl, hh, tx, sig) in enumerate(liste, 1):
            k = ' '.join(norm(tx or hh).split()[:6])
            if len(k.split()) == 6:
                anfaenge.setdefault(k, []).append(i)
        for k, nr in anfaenge.items():
            if len(nr) > 2:
                f.append(f'{titel}: {len(nr)} Vorschläge mit gleichem Anfang „{k}“ ({nr})')
    return f


# ---------------------------------------------------------------- Selbsttest (Mutationsprobe)
ABGELEHNT_SCHLUSS = [  # Noah, 15.11.2026 17:56: alle zehn abgelehnt
    'Du musst uns also nicht erst erklären, wie dein Betrieb läuft.',
    'Wenn du wissen willst, was davon bei dir drin ist, ruf einfach an.',
    'Melde dich einfach, dann schauen wir uns deinen Betrieb gemeinsam an.',
    'Den Rest erzähle ich dir gern am Telefon.',
    'Du machst dein Handwerk, um den Rest kümmern wir uns.',
    'Ich freu mich, deinen Betrieb kennenzulernen.',
    'Lass uns schauen, was in deinem Umkreis drin ist.',
    'Bei uns hast du Leute, die wissen, wovon sie reden.',
    'Wenn du Fragen hast, erreichst du mich direkt.',
    'Wie das bei dir aussehen kann, zeige ich dir gern im Erstgespräch.',
]
NEGATIV = [
    [('Schluss', '', [('Schlusssatz', '', 'Wenn du Lust hast, lass uns einfach mal quatschen.', '')])],
    [('Schluss', '', [('Schlusssatz', '', 'Und genau das setzen wir jetzt für deinen Betrieb um.', '')])],
    [('Über uns', '', [('Über uns', 'Seit 2019 nur fürs Handwerk.', 'Servus, ich bin Noah. Zwei meiner Brüder sind im Handwerk. Seit 2019 machen wir Websites und Anzeigen nur fürs Handwerk, für über 150 Betriebe bisher.', N)])],
    [('Über uns', '', [('Über uns', 'Wer dahinter steht.', 'Ich bin Noah und komme aus einer Handwerkerfamilie.', N)])],
    [('Über uns', '', [('Über uns', 'Einer musste|ins Büro.', 'Meine Brüder haben den Meister gemacht.', N)])],
    [('Ergebnisse', '', [('Ergebnisse', 'Druckprobe bestanden.', '', ''), ('Ergebnisse', 'Dein Betrieb, hydraulisch abgeglichen.', '', '')])],
    [('SHK Hero', '', [('Hero', 'Wir schließen dich an.', '', ''), ('Hero', 'Wir heizen deinem Betrieb ein.', '', '')])],
    [('Unterzeile', '', [('Unterzeile', '', 'Wir kümmern uns um Website, Anzeigen und Bewerbungen, damit du dich um deine Baustellen kümmern kannst.', '')])],
    [('Fallstudien', '', [('Die Ergebnisse', 'Ergebnisse unserer Kunden.', '', '')])],
    [('Texte', '', [('Text', '', 'Servus, ich bin Noah. Zum Handwerk hab ich einen kurzen Weg. Daher weiß ich, wie es zugeht.', ''),
                    ('Text', '', 'Hallo, hier Noah. Zum Handwerk hab ich einen kurzen Weg. Wir machen Websites.', '')])],
    [('FAQ', '', [('FAQ', 'Wie lange bin ich gebunden?', '', '')])],
    [('SHK', '', [('Hero', 'Die Agentur für Heizung, Sanitär und Klima.', '', '')])],
] + [[('Über uns · letzter Satz', '', [('Schlusssatz', '', s, '')])] for s in ABGELEHNT_SCHLUSS[1:]]
POSITIV = [  # von Noah am 15.11.2026 genommen
    [('HWM Start', '', [('Hero', 'Dein Handwerk.|Unsere Baustelle.', '', '')])],
    [('HWM Unterseiten', '', [('Websites', 'Wir bauen.|Du ziehst ein.', '', ''), ('Mitarbeiter', 'Verstärkung ist unterwegs.', '', ''),
                              ('Neue Kunden', 'Wir füllen dein Auftragsbuch.', '', ''), ('Ergebnisse', 'Bezugsfertig.', '', '')])],
    [('Ergebnisse', '', [('Fallstudien', 'Ergebnisse unserer Kunden.', '', '')])],
    [('Über uns', '', [('Du bist auf der Baustelle daheim. Wir im Internet.', 'Wer hinter der Handwerksmanufaktur steht.',
                        'Servus, ich bin Noah, Gründer der Handwerksmanufaktur. Dass wir nur fürs Handwerk arbeiten, kommt nicht von ungefähr. '
                        'Meine drei Brüder haben alle im Handwerk gelernt. Zwei davon sind Meister. Zusätzlich haben wir in der Familie mehrere Handwerksbetriebe. '
                        'Dadurch habe ich schon von klein auf täglich mitgekriegt, wie es im Handwerk wirklich zugeht. '
                        'In den letzten 8 Jahren haben wir über 150 Firmen betreut und wissen mittlerweile ganz genau, was ein Handwerksbetrieb online braucht, damit Kunden und Bewerber bei ihm landen.', N)])],
    [('Unterzeile', '', [('Unterzeile', '', 'Wir bauen deine Website und bringen dir qualifizierte Kunden und Mitarbeiter aus deinem Umkreis.', ''),
                         ('Unterzeile', '', 'Wer wir sind, wie wir arbeiten und warum wir das Handwerk so gut kennen.', '')])],
    [('SHK Leistungskarten', '', [('Titel', '', 'Gute Monteure. Lukrative Aufträge. Starke Website.', '')])],
    [('SHK Über uns', '', [('Wer dahinter steht', 'Du beherrschst dein Handwerk.|Wir unseres.', '', ''), ('Team', 'Kleines Team.|Kurze Wege.', '', '')])],
]


def selbsttest():
    fehler = 0
    for i, b in enumerate(NEGATIV, 1):
        if not pruefen(b):
            print(f'ROT FEHLT: Negativprobe {i} geht durch: {b[0][2]}')
            fehler += 1
    for i, b in enumerate(POSITIV, 1):
        r = pruefen(b)
        if r:
            print(f'FALSCH ROT: Positivprobe {i}: {r}')
            fehler += 1
    print(f'Selbsttest: {len(NEGATIV)} Negativ-, {len(POSITIV)} Positivproben, {fehler} Fehler')
    return fehler == 0


# ---------------------------------------------------------------- Seite bauen
e = html.escape


def h(x):
    a, _, b = x.partition('|')
    return e(a) + (f'<br><em>{e(b)}</em>' if b else '')


def bauen():
    befunde = pruefen(BLOECKE)
    if befunde:
        print('Vorschlags-Prüfung rot, nichts geschrieben:')
        print('\n'.join(' - ' + b for b in befunde))
        sys.exit(1)
    out = ['<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Über-uns-Texte</title><style>'
           ':root{--ink:#0B1424;--sub:#4A5666;--line:#DCE3EC;--paper:#F3F6FA;--warm:#C9581A}*{box-sizing:border-box;margin:0;padding:0}body{background:var(--paper);color:var(--ink);font:17px/1.55 Inter,system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased}'
           '.wrap{max-width:760px;margin:0 auto;padding:32px 20px 96px}h1{font-size:clamp(30px,5vw,44px);letter-spacing:-.03em;line-height:1.1;margin-bottom:8px}.lead{color:var(--sub)}h2{font-size:24px;letter-spacing:-.02em;margin:56px 0 16px}h2 small{display:block;font-size:15px;font-weight:400;letter-spacing:0;color:var(--sub);margin-top:4px}'
           '.k{background:#fff;border:1px solid var(--line);border-radius:24px;padding:32px;margin-bottom:16px;position:relative}.nr{position:absolute;top:28px;right:32px;font-size:15px;font-weight:600;color:var(--sub)}.kl{font-size:14px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--warm);margin-bottom:16px}'
           '.k h3{font-size:clamp(28px,5vw,38px);line-height:1.1;letter-spacing:-.03em;margin-bottom:20px;text-wrap:balance}.k h3 em{font-style:italic;font-weight:500;color:var(--warm)}.k p{color:var(--sub);max-width:58ch}.k .sig{margin-top:20px;color:var(--ink);font-weight:600;font-size:15px}'
           '@media(max-width:560px){.k{padding:24px 20px}.nr{top:20px;right:20px}}'
           '</style></head><body><div class="wrap"><h1>Über-uns-Texte</h1>']
    if not BLOECKE:
        out.append('<p class="lead">Gerade ist keine Runde offen.</p>')
    else:
        out.append('<p class="lead">Nenn mir Seite und Nummer.</p>')
    for titel, dom, liste in BLOECKE:
        out.append(f'<h2>{e(titel)}<small>{e(dom)}</small></h2>')
        for i, (kl, hh, tx, sig) in enumerate(liste, 1):
            out.append(f'<div class="k"><span class="nr">{i}</span><div class="kl">{e(kl)}</div>' + (f'<h3 style="margin-bottom:0">{h(hh)}</h3>' if hh else '') + (f'<p>{e(tx)}</p>' if tx else '') + (f'<p class="sig">{e(sig)}</p>' if sig else '') + '</div>')
    out.append('</div></body></html>')
    s = ''.join(out)
    assert '–' not in s and '—' not in s
    Path(__file__).with_name('index.html').write_text(s)
    print(sum(len(l) for _, _, l in BLOECKE), 'Texte')


if __name__ == '__main__':
    if '--selbsttest' in sys.argv:
        sys.exit(0 if selbsttest() else 1)
    if not selbsttest():
        sys.exit('Selbsttest rot, Seite nicht gebaut')
    bauen()

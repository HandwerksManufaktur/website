"""Entwurf der Seite: Firma → Leistungen → Ergebnisse (Noah, 14.11.2026, wie shk…/start-neu/).

Die Startseite positioniert uns als Partner für Handwerksbetriebe, zeigt die drei Leistungen
gleichrangig und danach die Ergebnisse; Problem-Szenen und Mechanik gehören auf die Unterseiten.
Baut start-neu/index.html aus der Live-Startseite (index.html) und die fünf Leistungs-Entwürfe
start-neu/<leistung>/index.html aus den Live-Unterseiten, damit Entwurf und Live nie auseinanderlaufen.
Jede Unterseite zündet nur auf ihre Leistung: Hero → Problem → wie es läuft → Ergebnisse → Stimmen
→ Fragen → Kontakt. Alle Entwurfsseiten noindex, Links auf Start + die fünf Leistungen bleiben im Entwurf.
Live bleibt unberührt (kein Link von Live in den Entwurf, nicht in sitemap.xml / llms.txt).
Aufruf: /Users/noahs/CEO-GPT/.venv/bin/python start-neu/bauen.py
"""
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
WURZEL = HIER.parent
LEISTUNGEN = ("websites", "suchmaschinenoptimierung", "foto-video", "neukundengewinnung", "mitarbeitergewinnung")
import sys
# Quelle = eingefrorener Stand der Seiten vor dem Umbau (start-neu/quelle/). Seit dem Livegang (14.11.2026) schreibt
# `bauen.py --live` die neuen Fassungen an die echten Adressen; ohne Flag entsteht wie bisher der Entwurf unter /start-neu/.
LIVE = "--live" in sys.argv
QUELLE = HIER / "quelle"
ZIEL = WURZEL if LIVE else HIER
LIVE_START = (QUELLE / "start.html").read_text()

# Nur Website-Kunden in der SEO-Rangliste (Noah, 16.11.2026: „alle Kunden, die nicht Website-Kunden sind, dürfen wir dort
# nicht erwähnen. Generell darf [Betrieb] auch nicht erwähnt werden.“). Liste + Grund je Betrieb: system/config/rankings.yaml.
import yaml
NICHT_NENNEN = yaml.safe_load((WURZEL.parent.parent / "system/config/rankings.yaml").read_text(encoding="utf-8"))["nicht_auf_hwm_website"]


def nur_website_kunden(seite):
    """Streicht Nicht-Website-Kunden aus Rangliste und „Alle Messungen“, füllt die zwölf Kacheln mit der nächsten
    Platz-1-Seite auf und rechnet „auf Seite 1“ / „davon auf Platz 1“ / „Alle N Messungen“ aus den übrigen Zeilen."""
    muster = [m for e in NICHT_NENNEN for m in e["muster"]]
    weg = lambda li: any(m in li for m in muster)
    h = seite.h
    ul = re.search(r'<ul class="seo-liste">(.*?)</ul>', h, re.S)
    alle = re.findall(r'<li class="[^"]*" style="--i:\d+">.*?</li>', ul.group(1), re.S)
    zeilen = [z for z in alle if not weg(z)]
    plaetze = [int(p) for z in zeilen for p in re.findall(r'<span class="platz">Platz (\d+)</span>', z)]
    seite1, platz1 = sum(p <= 10 for p in plaetze), plaetze.count(1)
    zeilen = [re.sub(r'--i:\d+', f'--i:{i}', z, 1) for i, z in enumerate(zeilen)]
    ol = re.search(r'<ol class="rangliste">(.*?)</ol>', h, re.S)
    kacheln = re.findall(r'<li class="reveal">.*?</li>', ol.group(1), re.S)
    behalten = [k for k in kacheln if not weg(k)]
    worte = {re.search(r'<small>(.*?)</small>', k).group(1) for k in behalten}
    for z in zeilen:
        if len(behalten) >= len(kacheln): break
        if '<span class="platz">Platz 1</span>' not in z: continue
        name, wort = re.search(r'<b>(.*?)</b><small>Suchbegriff: „(.*?)“</small>', z).groups()
        if wort in worte: continue
        behalten.append(f'<li class="reveal"><span class="rl-platz">1</span><div><b>{name}</b><small>{wort}</small></div></li>')
        worte.add(wort)
    assert len(behalten) == len(kacheln), (len(behalten), len(kacheln))
    behalten.sort(key=lambda k: re.search(r'<b>(.*?)</b>', k).group(1).casefold())
    h = h[:ol.start(1)] + ''.join(behalten) + h[ol.end(1):]
    ul = re.search(r'<ul class="seo-liste">(.*?)</ul>', h, re.S)
    h = h[:ul.start(1)] + ''.join(zeilen) + h[ul.end(1):]
    zahlen = iter((seite1, platz1))
    h, n = re.subn(r'(<div class="rl-zahl"><span class="nr" data-zahl=")\d+(" data-nach="[^"]*">)\d+(</span>)',
                   lambda m: f'{m.group(1)}{(v := next(zahlen))}{m.group(2)}{v}{m.group(3)}', h)
    assert n == 2, n
    h, n = re.subn(r'<b>Alle \d+ Messungen aufklappen</b>', f'<b>Alle {len(zeilen)} Messungen aufklappen</b>', h)
    assert n == 1, n
    assert not any(m in h for m in muster), [m for m in muster if m in h]
    seite.h = h
    return seite1

# Kontakt-Sektion am Seitenende (Noah, 15.11.2026: „wieso ist da links schon wieder die Sektion kürzer“): am Desktop
# füllt die Collage genau die Höhe der Textspalte (oben und unten bündig, Raster 4 × 4, Köpfe setzt main.js per data-k),
# am Handy zwei volle Reihen statt einer angeschnittenen dritten. Dieselbe Regel steht wortgleich in ueber-uns/index.html.
KONTAKT_STIL = ('@media (min-width:901px){.umkreis-kontakt .uk-karte{align-items:stretch!important}'
                '.umkreis-kontakt .uk-bild{position:relative;max-height:none;overflow:visible}'
                '.umkreis-kontakt .uk-bild .collage.mit-film{position:absolute;inset:0;grid-template-columns:repeat(4,minmax(0,1fr))!important;'
                'grid-template-rows:repeat(4,minmax(0,1fr));grid-auto-rows:0;align-content:stretch!important;gap:8px}'
                '.umkreis-kontakt .uk-bild .collage.mit-film img{height:100%;aspect-ratio:auto;object-fit:cover}'
                '.umkreis-kontakt .uk-bild .collage.mit-film img:nth-child(-n+13){display:block}'
                '.umkreis-kontakt .uk-bild .collage.mit-film img:nth-child(n+14){display:none}}'
                '@media (max-width:760px){.umkreis-kontakt .uk-bild{max-height:none}'
                '.umkreis-kontakt .uk-bild .collage.mit-film img:nth-child(n+4){display:none}}'
                '.umkreis-kontakt .uk-bild .collage img,.umkreis-kontakt .uk-bild .collage .c-film{border-radius:var(--radius)}')

# Leistungskarten (Startseite „Drei Baustellen …“ und „Was wir übernehmen“ der Unterseiten), Noah 15.11.2026: Apple-Regeln.
# Ein Raster: Rand 32/22 rundum, Titel → Zeile 4, Zeile → Text 12, Text → Link 20; Text in jeder Karte einer Reihe gleich
# viele Zeilen (am Desktop 2, am Handy bei „Was wir übernehmen“ 3), am Handy alle Karten einer Reihe gleich hoch.
KARTEN_STIL = ('.leistungen-sek .erg-in p,.uebernehmen-sek .erg-in p{min-height:3em;min-height:2lh}'
               '.leistungen-sek .erg .textlink{margin-top:8px}'
               '@media (max-width:760px){.leistungen-sek .ergebnisse,.uebernehmen-sek .ergebnisse{align-items:stretch!important}'
               '.uebernehmen-sek .erg-in p{min-height:4.5em;min-height:3lh}}')


# Fuß (Noah, 18.11.2026): „Websites für dein Gewerk“ und „Mitarbeiter finden je Gewerk“ unten noch nicht anzeigen,
# Einsatzgebiet raus, Mail und Telefon sitzen nicht mittig zum Icon (Emoji auf der Grundlinie, Link 44 px hoch).
# Dieselbe Fassung erzeugt build_pages.fuss() (FUSS_KONTAKT) für alle übrigen Seiten. Prüfer: start-neu/fuss_pruefen.mjs
from fuss import FUSS_KONTAKT, fuss_neu  # noqa: E402  (eine Quelle für den Fuß)


# Kundenstimmen (Noah, 18.11.2026): „laufen da wirklich alle Bewertungen durch, oben sowie unten, gleich viele … alle 57 …
# zumindest überall, wo Text da steht? Ansonsten müssen wir da vielleicht auch noch mit (…) arbeiten, damit wir nicht das
# Zitat verfälschen“. Quelle: alle 52 Google-Bewertungen mit Text (57 gesamt, 5 ohne Text), Wortlaut unverändert; nur
# Emojis fallen weg. Lange Texte enden nach ganzen Sätzen mit „(…)“, ausgelassene Sätze in der Mitte ebenfalls „(…)“.
# Zwei Reihen à 26, gegenläufig. Logos nur in der weißen Fassung; ohne Logo die Initialen auf derselben Kachel.
REZENSIONEN = WURZEL.parent.parent / "marketing/google-rezensionen-2026-09-30.json"
STIMME_WER = {  # Google-Name → (Anzeige, Zeile darunter, weißes Logo in /static/assets/img/logos/w/)
    "Silvana Bock": ("Silvana Bock", "M+S Langmajer GmbH", "logo-elektro-langmajer.webp"),
    "Lukas Schwaighofer": ("Lukas Schwaighofer", "Schwaighofer Betontechnik", "logo-schwaighofer-betontechnik-logo.webp"),
    "Manfred Oswald": ("Manfred Oswald", "Oswald Bau", "logo-oswald-bau-weil.webp"),
    "Alexander Hindelang": ("Alexander Hindelang", "Planung Hindelang", "logo-planung-hindelang.webp"),
    "Elke Aumüller": ("Elke Aumüller", "Zimmerei Koller", "logo-zimmerei-koller.webp"),
    "Dieter Müller": ("Dieter Müller", "Malermeister Müller", "logo-malermeister-mueller-weiss.webp"),
    "Peter Ehle": ("Peter Ehle", "Malerbetrieb Ehle", None),
    "Thomas Gattinger": ("Thomas Gattinger", "Gattinger GmbH", "logo-gattinger-gmbh.webp"),
    "Maximilian Wegele": ("Maximilian Wegele", "Wegele Bau", "logo-wegele-bau-gmbh-utting.webp"),
    "Franz Pföderl": ("Franz Pföderl", "Zimmerei Pföderl", "logo-zimmerei-pfoederl.webp"),
    "Yannick Stimpfle": ("Yannick Stimpfle", "Stimpfle Sanitär &amp; Heizung", "logo-yannick-stimpfle-logo.webp"),
    "Maximilian Ruf": ("Maximilian Ruf", "Max Ruf Frischdienst", "logo-ruf-frischdienst.webp"),
    "Nico Wohner": ("Nico Wohner", "Wohner Elektrotechnik", "wohner_elektrotechnik_weiss_cropped.webp"),
    "Björn S.": ("Björn S.", "Schreinermeister Björn Schillinger", "logo-bjoern-schillinger.webp"),
    "Chris": ("Chris", "Google-Bewertung", None),
    "Ulrike Knappich": ("Ulrike Knappich", "Zimmerei Knappich", "logo-zimmerei-knappich.webp"),
    "Alexandra Rosenberg": ("Alexandra Rosenberg", "SD Hirsch", "logo-sd-hirsch-weiss.webp"),
    "Ralph Negele": ("Ralph Negele", "Allplast Laser", "logo-allplast-laser.webp"),
    "Stephan Rupp": ("Stephan Rupp", "Raumausstattung &amp; Schreinerei Rupp", "logo-schreinerei-rupp.webp"),
    "Lena": ("Lena", "Lagerhaus Graf", "logo-lagerhaus-graf.webp"),
    "Alfred Maser": ("Alfred Maser", "Maser Tankschutz", "logo-maser-tankschutz-logo.webp"),
    "Christoph Hirschvogel": ("Christoph Hirschvogel", "Küchenhaus Hirschvogel", "logo-kuechenhaus-hirschvogel.webp"),
    "EckRu": ("EckRu", "CNC-Technik", "logo-eckru-cnc.webp"),
    "Zimmerei Rauschmair": ("Zimmerei Rauschmair", "Zimmerei", "logo-zimmerei-rauschmair.webp"),
    "Raphael Weiß": ("Raphael Weiß", "Metallbau Weiß", "logo-metallbau-weiss.webp"),
    "Hannes Schmidt": ("Hannes Schmidt", "Hannes Schmidt GmbH", "logo-hannes-schmidt-gmbh-weiss.webp"),
    "Robert Musch": ("Robert Musch", "Franz Musch &amp; Co.", "logo-franz-musch.webp"),
    "Rudolf Damnig": ("Rudolf Damnig", "Schreinerei Damnig", "logo-schreinerei-damnig.webp"),
    "Michael Hohenester": ("Michael Hohenester", "Zimmerei Hohenester", "logo-hohenester-zimmerei.webp"),
    "Leonhard Rieger": ("Leonhard Rieger", "Selbstständig", "logo-leonhard-rieger.webp"),
    "Thomas Hilbenz": ("Thomas Hilbenz", "Gutachter", "logo-gutachter-hilbenz.webp"),
    "Andreas Schuster": ("Andreas Schuster", "Zimmerei Schuster", "logo-zimmerei-schuster.webp"),
    "Inna Illenseer": ("Inna Illenseer", "TCM-Praxis", "logo-inna-illenseer.webp"),
    "Jirka Ihr Hotelsanierer": ("Robert Jirka", "Hotelsanierung", "logo-jirka-ausbau.webp"),
    "Thomas Vogel": ("Thomas Vogel", "Vogel Holzbau", "logo-thomas-vogel-holzbau.webp"),
    "Andrea Süßmeier": ("Andrea Süßmeier", "Süßmeier Heizungstechnik", "logo-suessmeier-heizungstechnik.webp"),
    "F. G.": ("Franz Gallenberger", "Sanitär-Heizung-Klimatechnik", "logo-franz-gallenberger.webp"),
    "Alisa Kirchner": ("Alisa Kirchner", "Baustoffe Thaining Kirchner", "logo-baustoffe-thaining-kirchner.webp"),
    "Stefan Fritsch": ("Stefan Fritsch", "FlyIn BBQ", "logo-flyin-bbq-streetfood.webp"),
    "Dietmar Kreitner": ("Dietmar Kreitner", "Schreinerei Kreitner", "logo-schreinerei-kreitner.webp"),
    "Autohaus Ressle": ("Autohaus Ressle", "Autohaus", "logo-autohaus-ressle.webp"),
    "Christoph Berger": ("Christoph Berger", "Textilreinigung Berger", None),
    "Michael Wagenknecht": ("Michael Wagenknecht", "Juwelier Wagenknecht", "logo-juwelier-wagenknecht-weiss.webp"),
    "I. Weber": ("I. Weber", "Kfz-Sachverständigenbüro Eggert", "logo-eggert-kfz-sachverstaendigenbuero.webp"),
    "Lanzinger GmbH": ("Lanzinger GmbH", "Heizung &amp; Sanitär", "logo-lanzinger-gmbh-weiss.webp"),
    "K Dörfler": ("K. Dörfler", "Dörfler Bau", "logo-doerfler-bau.webp"),
    "Be Se": ("Fa. Senftleben", "Sanitär Heizung, Ehingen", "logo-senftleben-haustechnik.webp"),
    "Martin Führmann": ("Martin Führmann", "Schreinerei Die Führmänner", "logo-schreinerei-die-fuehrmaenner.webp"),
    "Matthias Happach": ("Matthias Happach", "Happach Maschinenbau", "logo-happach-maschinenbau.webp"),
    "Marcel Burkart": ("Marcel Burkart", "Google-Bewertung", None),
    "Noah Velte": ("Noah Velte", "Google-Bewertung", None),
    "Jules Frey": ("Jules Frey", "Zimmerei Schneider", "logo-zimmerei-schneider.webp"),
}
# Welche Sätze bei langen Bewertungen stehen bleiben (Index der Sätze); alles dazwischen und dahinter wird „(…)“.
STIMME_SAETZE = {"Autohaus Ressle": (0, 2), "F. G.": (0, 1, 6)}
STIMME_MAX = 260
STIMME_RAUS = {"Noah Velte", "Michael Hohenester"}


def _saetze(text):
    return [s for s in re.split(r'(?<!Hr\.)(?<=[.!?])\s+(?=[A-ZÄÖÜ„"])', text) if s]


def stimme_text(autor, text):
    import html as _h
    text = re.sub(r'[⭐\U0001F300-\U0001FAFF☀-➿]️?', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    s = _saetze(text)
    if autor in STIMME_SAETZE:
        wahl = STIMME_SAETZE[autor]
    else:
        wahl, laenge = [], 0
        for i, satz in enumerate(s):
            if wahl and laenge + len(satz) > STIMME_MAX: break
            wahl.append(i); laenge += len(satz) + 1
    teile, vorher = [], -1
    for i in wahl:
        if i != vorher + 1: teile.append('(…)')
        teile.append(s[i]); vorher = i
    if vorher < len(s) - 1: teile.append('(…)')
    aus = ' '.join(teile)
    # Prüfung: jedes stehen gebliebene Stück steht wörtlich in der Bewertung (nichts umformuliert)
    assert all(st in text for st in aus.split(' (…)') if st.strip() and st.strip() != '(…)'), (autor, aus)
    return _h.escape(aus, quote=False)


def stimmen_alle():
    import json, html as _h
    alle = [r for r in json.loads(REZENSIONEN.read_text(encoding="utf-8"))["rezensionen"] if (r["text"] or "").strip()]
    assert len(alle) == 52, len(alle)
    # Noah, 18.11.2026 (2.): „möglichst … immer … mit Logo“ → nur Bewertungen mit Betriebslogo laufen durch. Ohne erkennbaren
    # Betrieb (Ehle, Berger, Chris, Burkart) und Noah Velte (bewertet für die eigene Firma, kein Handwerk) bleiben draußen,
    # Hohenester (ein Satz) fällt für gleich viele Karten je Reihe weg.
    alle = [r for r in alle if STIMME_WER[r["autor"]][2] and r["autor"] not in STIMME_RAUS]
    assert len(alle) % 2 == 0, len(alle)
    karten = []
    for r in alle:
        name, zeile, logo = STIMME_WER[r["autor"]]
        if logo:
            assert (WURZEL / "static/assets/img/logos/w" / logo).exists(), logo
            marke = f'<span class="kreis logo dunkel"><img loading="lazy" src="/static/assets/img/logos/w/{logo}" alt="" decoding="async"></span>'
        else:
            ini = ''.join(w[0] for w in re.sub(r'[^A-Za-zÄÖÜäöü ]', '', name).split()[:2]).upper()
            marke = f'<span class="kreis logo dunkel"><span class="st-ini">{ini}</span></span>'
        laenge = len(stimme_text(r["autor"], r["text"]))
        art = "st-kurz" if laenge <= 95 else ("st-mittel" if laenge <= 175 else "st-lang")
        karten.append(f'<div class="stimme {art}"><div class="wer">{marke}<span><b>{name}</b><small>{zeile}</small></span></div>'
                      f'<span class="stern" aria-label="{r["sterne"]} von 5 Sternen">{"★" * r["sterne"]}</span><p>„{stimme_text(r["autor"], r["text"])}“</p></div>')
    # Reihen mischen, damit nicht alle langen oben stehen: abwechselnd verteilen
    oben, unten = karten[0::2], karten[1::2]
    assert len(oben) == len(unten), (len(oben), len(unten))
    # Tempo wie vorher (10 Karten in 90 s / 100 s), jetzt 26 Karten je Reihe
    return (f'<div class="bahn" aria-hidden="false" style="animation-duration:234s">{"".join(oben) * 2}</div>'
            f'<div class="bahn zurueck" style="animation-duration:260s">{"".join(unten) * 2}</div>'
            '<style>.stimme .st-ini{font-size:18px;font-weight:800;letter-spacing:.02em;color:var(--papier)}'
            # Gleich hohe Karten; die Schrift wächst bei kurzen Stimmen, ein großes Anführungszeichen trägt die Karte
            '.sek.stimmen .stimme{position:relative;overflow:hidden;min-height:330px;grid-template-rows:auto auto 1fr;align-content:stretch;transition:transform .35s cubic-bezier(.2,.8,.2,1),box-shadow .35s}'
            '.sek.stimmen .stimme:hover{transform:translateY(-4px);box-shadow:0 18px 40px -22px rgba(22,19,14,.35),0 0 0 1px rgba(22,19,14,.08)}'
            '.sek.stimmen .stimme::before{content:"\\201C";position:absolute;right:22px;top:6px;font-size:120px;line-height:1;font-weight:800;color:var(--bronze);opacity:.16;pointer-events:none}'
            '.sek.stimmen .stimme p{align-self:center;color:var(--tinte)}'
            '.sek.stimmen .st-kurz p{font-size:clamp(20px,1.6vw,23px);line-height:1.35;font-weight:600;letter-spacing:-.01em}'
            '.sek.stimmen .st-mittel p{font-size:17.5px;line-height:1.5}'
            '.sek.stimmen .st-lang p{font-size:15.5px;line-height:1.55}'
            '.sek.stimmen .kreis.logo{width:132px;height:58px}.sek.stimmen .kreis.logo img{max-width:108px;max-height:40px}'
            '@media (prefers-reduced-motion:reduce){.sek.stimmen .stimme{transition:none}}</style>')


STIMME_ALIAS = {"Hannes Schmidt GmbH": "Hannes Schmidt", "Fa. Senftleben": "Be Se", "Franz Gallenberger": "F. G.", "Jirka": "Jirka Ihr Hotelsanierer"}


def stimmen_woertlich(h):
    """Jede Stimme auf jeder Seite trägt den Google-Wortlaut (Kürzung nur mit „(…)“), nie eine still umformulierte Fassung."""
    import json
    roh = {r["autor"]: r for r in json.loads(REZENSIONEN.read_text(encoding="utf-8"))["rezensionen"] if (r["text"] or "").strip()}
    def ein(m):
        name = m.group(2)
        autor = STIMME_ALIAS.get(name, name)
        if autor not in roh:
            autor = next((a for a, w in STIMME_WER.items() if w[0] == name), None)
        if not autor or autor not in roh:
            return m.group(0)
        return f'{m.group(1)}„{stimme_text(autor, roh[autor]["text"])}“</p>'
    return re.sub(r'(<div class="stimme"><div class="wer">.*?<b>(.*?)</b>.*?<p>)„.*?“</p>', ein, h, flags=re.S)


class Seite:
    def __init__(self, quelle):
        # Noah, 15.11.2026: Kundenzahl überall 150 (Meta, Logoband, Hero); die Bewertungszeile unter „Kundenstimmen“
        # („5,0 auf Google · 57 Bewertungen · …“) ersatzlos raus, nur Kicker + Überschrift bleiben.
        quelle = quelle.replace("Über 130 Betriebe", "Über 150 Betriebe")
        quelle = re.sub(r'\n?<div class="zusammen reveal">[^<]*(?:<(?!/?div)[^<]*)*</div>', "", quelle)
        self.h = quelle

    def ersetze(self, alt, neu, menge=1):
        assert self.h.count(alt) == menge, (alt[:80], self.h.count(alt))
        self.h = self.h.replace(alt, neu)

    def bereich(self, anfang):
        """(start, ende) der <section>, die mit `anfang` beginnt, verschachtelte <section> mitgezählt."""
        assert self.h.count(anfang) == 1, (anfang, self.h.count(anfang))
        a = self.h.index(anfang)
        tiefe, pos = 0, a
        for m in re.compile(r"<section\b|</section>").finditer(self.h, a):
            tiefe += 1 if m.group() == "<section" else -1
            if tiefe == 0:
                return a, m.end()
        raise AssertionError(anfang)

    def heraus(self, anfang):
        a, e = self.bereich(anfang)
        teil = self.h[a:e]
        self.h = self.h[:a] + self.h[e:]
        return teil

    def vor(self, anfang, teil):
        a, _ = self.bereich(anfang)
        self.h = self.h[:a] + teil + self.h[a:]

    def nach(self, anfang, teil):
        _, e = self.bereich(anfang)
        self.h = self.h[:e] + teil + self.h[e:]

    def ohne_rechner(self):
        """Rechner vorerst raus (Noah, 15.11.2026): Knopf, Dialog und Hero-Knöpfe weg bzw. auf den Termin-Weg der Startseite.
        Die Rechner-Seiten selbst bleiben liegen, werden aber nirgends mehr verlinkt."""
        h = self.h
        h, n1 = re.subn(r'\n?<button type="button" class="uk-rechner" data-rechner>.*?</button>', "", h, flags=re.S)
        h, n2 = re.subn(r'<dialog class="rd" id="rechner-dialog".*?</dialog>', "", h, flags=re.S)
        h = h.replace('<a class="btn btn-bronze" href="#rechner-auf">Potenzial durchrechnen ', '<a class="btn btn-bronze" href="/kontakt/">Erstgespräch vereinbaren ')
        assert n1 == 1 and n2 == 1, (n1, n2)
        assert not re.search(r'rechner|durchrechnen|Rechner', h), re.findall(r'.{40}(?:rechner|durchrechnen|Rechner).{40}', h)[:3]
        self.h = h

    def entwurf(self):
        """noindex + alle Links auf Start und die fünf Leistungen in den Entwurf."""
        self.ohne_rechner()
        if not LIVE:
            self.ersetze('<meta name="robots" content="index,follow">', '<meta name="robots" content="noindex, nofollow, noarchive">')
            self.h = re.sub(r'href="/(#[^"]*)?"', lambda m: f'href="/start-neu/{m.group(1) or ""}"', self.h)
            self.h = re.sub(r'href="/(%s)/' % "|".join(LEISTUNGEN), r'href="/start-neu/\1/', self.h)
        self.h = self.h.replace('</head>', '<style>/* Entwurf: Tap-Ziele im Fuß mindestens 44 px breit */.fuss ul a,.fuss .unten a,.fuss-gewerke a{min-width:44px;display:inline-block;text-align:center}.lg-buehne li span b,.pb-marke,.ab-leiste span,.lang-marke,.pb-karte b,.fsz-legende span,.kal-fuss span,.kal-fuss b,.rg-lese,.pb-adr span,.pb-menue span,.pb-ruf,.pb-ok{letter-spacing:.01em!important}.ab-zoom{transition-duration:.4s!important}'
                                    # Ohne Bewertungszeile steht der Stimmen-Kopf mit demselben Abstand zum Inhalt wie jede andere Sektion
                                    # Ergebnis-Karten: gleiche Innenabstände in jeder Karte (Noah, 15.11.2026: „manchmal komisch hoch, manchmal komisch niedrig“).
                                    # Logo-Zeile in allen Karten gleich hoch (ein Name lief über drei Zeilen und schob Zahlen und Text nach unten),
                                    # Link im Rhythmus der übrigen Karteninhalte (12 statt 14), am Handy Karten in Eigenhöhe statt gestreckt
                                    # (gestreckt blieb unter dem Text bis zu 147 px Leerraum), Überschrift neben Lead startet oben wie überall.
                                    '.erg-wer{min-height:56px}.erg .textlink{margin-top:0}.kopfzeile:has(>.lead)>h2{align-self:start}.wisch-hinweis{margin-top:0}'
                                    '@media (max-width:760px){.ergebnisse{align-items:flex-start}}'
                                    '.stimmen .kopfzeile{margin-bottom:clamp(36px,5vw,64px)}'
                                    # Keine Sektions-H2 mit drei Zeilen am Desktop (Noah, 15.11.2026): die 16ch-Grenze lässt „Drei Baustellen übernehmen wir für dich.“ und
                                    # „Über 50 Fotos aus den Betrieben unserer Kunden.“ dreizeilig laufen, also bekommen diese beiden Köpfe die breitere Spalte
                                    '@media (min-width:901px){.leistungen-sek .kopfzeile,.fotowand-sek .kopfzeile{grid-template-columns:minmax(0,1.4fr) minmax(0,.6fr)!important}'
                                    '.leistungen-sek .kopfzeile>h2,.fotowand-sek .kopfzeile>h2{max-width:none!important}}'
                                    '@media (max-width:900px){.dsk-br{display:none}}' + KONTAKT_STIL + KARTEN_STIL + '</style>' + NEU_KOPF + '</head>', 1)
        assert self.h.count('</body>') == 1
        self.h = self.h.replace('</body>', NEU_FUSS + '</body>')

    def schreibe(self, pfad):
        # Sperre (Noah, 16.11.2026): „Generell darf [Betrieb] auch nicht erwähnt werden“ → kein `ueberall`-Betrieb auf irgendeiner Seite
        treffer = [m for e in NICHT_NENNEN if e.get("ueberall") for m in e["muster"] if m in self.h]
        assert not treffer, (pfad, treffer)
        # Sperren (Noah, 15.11.2026): kein Kicker mit Mittelpunkt, keine alte Kundenzahl, keine Bewertungszeile unter den Stimmen
        assert not re.findall(r'<span class="kicker">[^<]*·[^<]*</span>', self.h), (pfad, re.findall(r'<span class="kicker">[^<]*·[^<]*</span>', self.h))
        assert "130 Betriebe" not in self.h and 'class="zusammen' not in self.h, pfad
        self.h = fuss_neu(self.h)
        self.h = stimmen_woertlich(self.h)
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_text(self.h)
        print("✓", pfad.relative_to(WURZEL), len(self.h))


# ── Bausteine aus der Live-Startseite ──────────────────────────────────────────────────────────────
start = Seite(LIVE_START)
PROBLEME = start.heraus('<section class="sek grund lagen-sek probleme pb-sek">')
STIMMEN = start.bereich('<section class="sek stimmen">')
STIMMEN = start.h[STIMMEN[0]:STIMMEN[1]]


def szene(nr, kicker, titel, grund=True):
    """Eine einzelne Problem-Szene (Heute → Mit uns) aus dem Startseiten-Block, ohne Reiterleiste.
    Die Bühne und ihr Skript (main.js, .lg-buehne) bleiben dieselben; nur die Leiste ist ausgeblendet."""
    tab = re.search(r'<button type="button" class="lg-tab[^"]*"[^>]*id="lg-t%d".*?</button>' % nr, PROBLEME, re.S).group()
    a = PROBLEME.index('<div class="lg-panel pb-panel', PROBLEME.index(f'id="lg-p{nr}"') - 80)
    ende = '<span class="pb-vs" aria-hidden="true">vs</span></div>'
    panel = PROBLEME[a:PROBLEME.index(ende, a) + len(ende)]
    tab = re.sub(r'class="lg-tab[^"]*"', 'class="lg-tab an"', tab).replace('aria-selected="false"', 'aria-selected="true"')
    panel = re.sub(r'class="lg-panel pb-panel[^"]*"', 'class="lg-panel pb-panel an"', panel).replace(" hidden>", ">", 1)
    klasse = "sek grund lagen-sek probleme pb-sek einzel-szene" if grund else "sek lagen-sek probleme pb-sek einzel-szene"
    return (f'<section class="{klasse}"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">{kicker}</span>'
            f'<h2>{titel}</h2></div><div class="lg-buehne pb-buehne reveal"><div class="lg-tabs" role="tablist" aria-label="Woran es hängt">'
            f'{tab}</div><div class="lg-panels">{panel}</div></div></div></section>'
            '<style>/* Entwurf: eine Szene ohne Reiterleiste (start-neu/bauen.py) */'
            '.einzel-szene .lg-tabs,.einzel-szene .lgm-titel{display:none}'
            '.einzel-szene .lg-buehne{grid-template-columns:minmax(0,1fr)}</style>')


# ── Neu 18.11.2026 (Noah): „Bei Foto und Video: Ich weiß nicht, ob das mit den drei Kacheln so von Vorteil ist, immer oben
# bei den Unterseiten … Bei der Home-Seite können wir sicher auch nochmal das Logo so ein bisschen im Hintergrund mit
# reinnehmen … bei ESM Schäfer … das geisteskranke Ding … Wenn man auf Fotos und Videos geht, soll man eine richtig geile
# verspielte Seite sehen … Da müssen wir die besten Fotos und Videos haben … da stehe ich jetzt dreimal irgendwie mit Kunden“.
# → Startseite: Hero mit drei Säulen bleibt, das Signet steht groß und bewegt im Hintergrund von „Unsere Leistungen“ (wächst
#   Balken für Balken) und „Wer hinter der Handwerksmanufaktur steht“ (Umriss zeichnet sich, Bronze steigt).
# → Unterseiten: Film-Hero je Leistung statt der drei schrägen Säulen. → Foto & Video: Galerie mit Filter, Filmen beim
#   Drüberfahren, Lichtkasten und ein Kontaktabzug; kein Foto mit Noah und Kunde (die stehen auf /ueber-uns/).
# Stil und Verhalten: static/seiten-neu.css + static/seiten-neu.js, Medien: start-neu/medien_bauen.py → static/assets/fv/.
import html as _html
import json as _json

NEU_V = "2"
NEU_KOPF = f'<link rel="stylesheet" href="/static/seiten-neu.css?v={NEU_V}">'
NEU_FUSS = f'<script src="/static/seiten-neu.js?v={NEU_V}" defer></script>'
SIGNET = ('M0,39.667 L22,25 L22,91 L0,91 Z', 'M34,14.667 L56,0 L56,91 L34,91 L34,64.67 L27,68 L27,53.667 L34,49 Z',
          'M61,14.667 L83,0 L83,91 L61,91 Z')  # Fassung C (firma/branding/logo), dieselben Pfade wie das Zeichen im Kopf
SIGNET_WACHSEN = ('<div class="sg-buehne sg-wachsen" aria-hidden="true"><svg viewBox="0 0 83 91" preserveAspectRatio="xMidYMax meet"><defs>'
                  '<linearGradient id="sg-verlauf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9BE84"/><stop offset=".5" stop-color="#F0D6B1"/><stop offset="1" stop-color="#F4ECDF"/></linearGradient>'
                  '<linearGradient id="sg-glanz" x1="0" y1="0" x2="1" y2=".3"><stop offset=".38" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".95"/><stop offset=".62" stop-color="#fff" stop-opacity="0"/></linearGradient>'
                  '<radialGradient id="sg-zeiger" gradientUnits="userSpaceOnUse" cx="40" cy="45" r="0"><stop offset="0" stop-color="#E5B36E" stop-opacity=".6"/><stop offset="1" stop-color="#E5B36E" stop-opacity="0"/></radialGradient></defs>'
                  + "".join(f'<g class="sg-b"><path class="sg-k" d="{d}"/><path class="sg-glanz" d="{d}"/><path fill="url(#sg-zeiger)" d="{d}"/>'
                            f'<path class="sg-l" d="{d}" vector-effect="non-scaling-stroke"/></g>' for d in SIGNET) + '</svg></div>')
SIGNET_RUHE = ('<div class="sg-buehne sg-ruhe" aria-hidden="true"><svg viewBox="0 0 83 91"><defs><clipPath id="sg-steig">'
               '<rect class="sg-fuell-rect" x="-10" y="0" width="103" height="110"/></clipPath></defs>'
               + "".join(f'<g class="sg-b"><path class="sg-fuell" clip-path="url(#sg-steig)" d="{d}"/><path class="sg-umriss" pathLength="1" d="{d}"/></g>' for d in SIGNET)
               + '</svg></div>')

VID = "/static/assets/vid"
FV = "/static/assets/fv"


def _film(mp4, poster, sofort=False):
    p = f'poster="{poster}"' if sofort else f'poster="{poster}"'
    return f'<video muted loop playsinline preload="none" data-hand data-src="{mp4}" {p}></video>'


def _lage(name, film, an, url=""):
    return (f'<div class="hk-lage{" an" if an else ""}" data-name="{name}" data-url="{url}">'
            f'{_film(f"{VID}/{film}.mp4", f"{VID}/poster/{film}.jpg")}</div>')


def _chip(name, zeile, klasse="hk-chip"):
    return f'<span class="{klasse}"><i></i><span data-hk-name>{name}</span><small>{zeile}</small></span>'


def _telefone(reels, betrieb, art):
    tel = "".join(f'<div class="hk-tel"><div class="sc">{_film(f"{FV}/v/{r}.mp4", f"{FV}/v/{r}.jpg")}'
                  f'<span class="ad"><i></i><span>{betrieb}<small>{art}</small></span></span></div></div>' for r in reels)
    return f'<div class="hk-telefone" aria-hidden="true">{tel}</div>'


# Websites: Film des Betriebs im Hintergrund, seine Website (von uns) vorne im Browser — drei Betriebe im Wechsel
WEB_BETRIEBE = [("Schreinerei Kreitner", "kreitner", "h9", "schreinerei-kreitner.de"),
                ("Zimmerei Koller", "koller", "hkoller", "zimmerei-koller.com"),
                ("A. Resch Bau", "resch", "h7", "resch-kinsau.de")]


def hero_websites():
    lagen = "".join(_lage(n, f, i == 0, u) for i, (n, f, _, u) in enumerate(WEB_BETRIEBE))
    fenster = "".join(f'<video class="{"an" if i == 0 else ""}" muted loop playsinline preload="none" data-hand data-src="{VID}/hero/{h}.webm" '
                      f'poster="{VID}/hero/{h}.jpg"></video>' for i, (_, _, h, _) in enumerate(WEB_BETRIEBE))
    return (f'<div class="hk-film" aria-hidden="true">{lagen}</div>'
            f'<div class="hk-seite" aria-hidden="true"><div class="hk-browser"><div class="bl"><i></i><i></i><i></i><span>{WEB_BETRIEBE[0][3]}</span></div>'
            f'<div class="bs">{fenster}</div></div>{_chip(WEB_BETRIEBE[0][0], "Film und Website von uns")}</div>'
            + _chip(WEB_BETRIEBE[0][0], "Film und Website von uns", "hk-chip hk-chip-m"))


def hero_seo(seite):
    """Drohne steigt über die Halle; vorne tippt sich ein Suchbegriff und der Kunde steht auf Platz 1 (aus der Rangliste der Seite)."""
    gern = ("dachbau", "bauunternehmen", "spenglerei", "heizung", "elektriker", "tiefbau", "zimmerei", "schreinerei", "gebäudetechnik")
    eintraege = []
    for name, wort in re.findall(r'<li class="reveal"><span class="rl-platz">1</span><div><b>(.*?)</b><small>(.*?)</small></div></li>', seite.h):
        if wort.split()[0] in gern and len(wort) <= 30:
            eintraege.append({"name": _html.unescape(name), "wort": _html.unescape(wort)})
    assert len(eintraege) >= 3, eintraege
    daten = _html.escape(_json.dumps(eintraege[:6], ensure_ascii=False), quote=True)
    e0 = eintraege[0]
    zeilen = (f'<li><span class="pl">1</span><span><b>{_html.escape(e0["name"])}</b><small>Platz 1 bei Google</small></span></li>'
              '<li><span class="pl">2</span><span><b>·</b><small>·</small></span></li><li><span class="pl">3</span><span><b>·</b><small>·</small></span></li>')
    return (f'<div class="hk-film" aria-hidden="true"><div class="hk-lage an hk-einzel">{_film(f"{VID}/baureize.mp4", f"{VID}/poster/baureize.jpg")}</div></div>'
            f'<div class="hk-seite" aria-hidden="true"><div class="hk-suche" data-eintraege="{daten}"><div class="sf">'
            f'<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><b>{_html.escape(e0["wort"])}</b></div>'
            f'<ol>{zeilen}</ol></div>{_chip("Platz 1 bei Google", "echte Messungen unserer Kunden")}</div>'
            + _chip("Platz 1 bei Google", _html.escape(e0["wort"]), "hk-chip hk-chip-m"))


SHOWREEL = [("Zimmerei Koller", "koller"), ("CS Metalldesign", "cs-metall"), ("A. Resch Bau", "resch")]


def hero_foto_video():
    lagen = "".join(_lage(n, f, i == 0) for i, (n, f) in enumerate(SHOWREEL))
    leiste = "".join(f'<button type="button" class="{"an" if i == 0 else ""}" aria-pressed="{"true" if i == 0 else "false"}" aria-label="Film {n} zeigen">'
                     f'<img src="{VID}/poster/{f}.jpg" alt="" loading="lazy" decoding="async"></button>' for i, (n, f) in enumerate(SHOWREEL))
    return (f'<div class="hk-film" aria-hidden="true">{lagen}</div>'
            '<div class="hk-sucher" aria-hidden="true"><span class="ec"></span><span class="ec"></span><span class="ec"></span><span class="ec"></span>'
            '<span class="rec"><i></i>REC <b>00:00:00:00</b></span><span class="info">01 / 03</span><span class="mitte"></span></div>'
            f'<div class="hk-reel-leiste">{leiste}</div>' + _chip(SHOWREEL[0][0], "gedreht von uns"))


def hero_anzeigen(bild, reels, mobil, betrieb, art, chip):
    return (f'<div class="hk-film" aria-hidden="true"><img class="hk-kb hk-desk" src="{FV}/h/{bild}.webp" alt="" decoding="async" fetchpriority="high">'
            f'<video class="hk-mobil" muted loop playsinline preload="none" data-hand data-src="{FV}/v/{mobil}.mp4" poster="{FV}/v/{mobil}.jpg"></video></div>'
            + _telefone(reels, betrieb, art) + _chip(chip[0], chip[1], "hk-chip hk-tel-chip"))


def hero_neu(seite, slug, buehne, takt=None):
    """Die drei schrägen Säulen der Unterseite (.saeulen-k) weichen einem Film-Hero; Text, Knöpfe und Pause-Knopf bleiben."""
    a = seite.h.index('<section class="hero-klein">')
    e = seite.h.index('<button class="pause"', a)
    assert seite.h[a:e].count('class="saeulen-k"') == 1, slug
    t = f' data-takt="{takt}"' if takt else ''
    seite.h = seite.h[:a] + f'<section class="hero-klein hk-neu hk-{slug}"{t}>' + buehne + seite.h[e:]
    assert 'saeulen-k' not in seite.h, slug


# Galerie Foto & Video: 38 Fotos (medien_bauen.py, alle von Hand angesehen) + 7 Filme, Filter nach Gewerk
GALERIE = _json.loads((WURZEL / "static/assets/fv/galerie.json").read_text())
FILTER = [("alle", "Alle"), ("shk", "Sanitär &amp; Heizung"), ("holz", "Holz"), ("metall", "Metall"), ("bau", "Bau &amp; Ausbau"), ("film", "Filme")]
# (Stelle in der Fotoliste, Gewerk-Schlüssel, Gewerk, Betrieb, Seitenverhältnis, Film, Poster)
GALERIE_FILME = [(2, "holz", "Schreinerei", "Schreinerei Kreitner", 16 / 9, f"{VID}/kreitner.mp4", f"{VID}/poster/kreitner.jpg"),
                 (6, "shk", "Anzeige", "Erich Sussmann", 9 / 16, f"{FV}/v/su-dusche.mp4", f"{FV}/v/su-dusche.jpg"),
                 (11, "bau", "Bau &amp; Transporte", "Kirchner Thaining, 50 Jahre", 9 / 16, f"{VID}/kirchner.mp4", f"{VID}/poster/kirchner.jpg"),
                 (17, "shk", "Stellenanzeige", "Irlbacher Gebäudetechnik", 9 / 16, f"{FV}/v/ir-montage.mp4", f"{FV}/v/ir-montage.jpg"),
                 (23, "", "Drohnenflug", "Baureize", 16 / 9, f"{VID}/baureize.mp4", f"{VID}/poster/baureize.jpg"),
                 (28, "shk", "Anzeige", "Erich Sussmann", 9 / 16, f"{FV}/v/su-mirjana.mp4", f"{FV}/v/su-mirjana.jpg"),
                 (34, "shk", "Stellenanzeige", "Irlbacher Gebäudetechnik", 9 / 16, f"{FV}/v/ir-geselle.mp4", f"{FV}/v/ir-geselle.jpg")]


def galerie_sek():
    def foto(d):
        g, b = _html.escape(d["gewerk"]), _html.escape(d["betrieb"], quote=False) if d["betrieb"] else ""
        b = b.replace("&amp;amp;", "&amp;")
        alt = f'{g} bei {b}' if b else g
        return (f'<figure class="fv-k" data-g="{d["g"]}" style="--r:{d["w"] / d["h"]:.4f}"><button type="button" class="fv-auf" aria-label="{alt} groß ansehen">'
                f'<img src="{FV}/g/{d["k"]}-900.webp" srcset="{FV}/g/{d["k"]}-480.webp 480w, {FV}/g/{d["k"]}-900.webp 900w" sizes="(min-width:1100px) 22vw, (min-width:700px) 31vw, 48vw" data-gross="{FV}/g/{d["k"]}-1800.webp" alt="{alt}" loading="lazy" decoding="async" width="900" height="{round(900 * d["h"] / d["w"])}"></button>'
                f'<figcaption><b>{g}</b><span>{b or "Drehtag bei einem Kunden"}</span></figcaption></figure>')

    def film(g, gewerk, betrieb, r, mp4, poster):
        return (f'<figure class="fv-k ist-film" data-g="{(g + " film").strip()}" style="--r:{r:.4f}"><button type="button" class="fv-auf" aria-label="Film {betrieb} groß ansehen">'
                f'<video muted loop playsinline preload="none" data-hand data-src="{mp4}" poster="{poster}"></video><span class="fv-spiel">Film</span></button>'
                f'<figcaption><b>{gewerk}</b><span>{betrieb}</span></figcaption></figure>')
    karten = [foto(d) for d in GALERIE["fotos"]]
    for stelle, *rest in reversed(GALERIE_FILME):
        karten.insert(stelle, film(*rest))
    alle = "".join(karten)
    n = {k: len(re.findall(rf'data-g="[^"]*\b{k}\b', alle)) for k, _ in FILTER[1:]}
    n["alle"] = alle.count('class="fv-k')
    fotos, filme = len(GALERIE["fotos"]), len(GALERIE_FILME)
    knoepfe = "".join(f'<button type="button" data-f="{k}" aria-pressed="{"true" if k == "alle" else "false"}">{t}<sup>{n[k]}</sup></button>' for k, t in FILTER)
    pfeil = lambda d: f'<svg viewBox="0 0 24 24"><path d="{d}"/></svg>'
    return ('<section class="sek fv-galerie" id="ergebnisse"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Die Ergebnisse</span>'
            f'<h2>Abgedreht.</h2><p class="lead">{fotos} Fotos und {filme} Filme aus Drehtagen bei unseren Kunden.</p></div>'
            f'<div class="fv-filter" role="toolbar" aria-label="Nach Gewerk filtern">{knoepfe}</div><div class="fv-raster">{alle}</div></div></section>'
            '<dialog class="fv-licht" aria-label="Lichtkasten"><div class="lk-buehne"></div><div class="lk-fuss"><div><b></b><span></span></div><span class="lk-zahl"></span></div>'
            f'<button type="button" class="lk-knopf lk-zu" aria-label="Schließen">{pfeil("M6 6l12 12M18 6 6 18")}</button>'
            f'<button type="button" class="lk-knopf lk-zur" aria-label="Vorheriges">{pfeil("m15 5-7 7 7 7")}</button>'
            f'<button type="button" class="lk-knopf lk-vor" aria-label="Nächstes">{pfeil("m9 5 7 7-7 7")}</button></dialog>'
            '<div class="fv-cursor" aria-hidden="true"></div>')


def kontaktabzug_sek():
    """Ein Drehtag als Filmstreifen (Stimpfle, Aufnahme-Reihenfolge); Bilder, die schon in der Galerie stehen, bleiben draußen."""
    schon = {"st36", "st43", "st47"}
    bilder = [k for k in GALERIE["kontakt"] if k not in schon]
    kreis = '<svg viewBox="0 0 100 66" preserveAspectRatio="none"><path pathLength="1" d="M52,5 C83,3 97,18 95,34 C93,54 70,62 46,61 C20,60 4,49 5,32 C6,15 25,5 57,7"/></svg>'
    def rahmen(i, k, kopie):
        return (f'<span class="kb-bild"><img src="{FV}/k/{k}.webp" alt="" loading="lazy" decoding="async" width="420" height="280">'
                f'<em>{int(k[2:]):02d}A</em>{kreis if i % 7 == 3 and not kopie else ""}</span>')
    spur = "".join(rahmen(i, k, False) for i, k in enumerate(bilder)) + "".join(rahmen(i, k, True) for i, k in enumerate(bilder))
    return ('<section class="sek fv-kontakt"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Ein Drehtag</span>'
            '<h2>Ein Tag. Ein voller Ordner.</h2><p class="lead">Ausschnitt aus dem Drehtag bei Stimpfle Sanitär &amp; Heizung, in der Reihenfolge der Aufnahmen.</p></div></div>'
            f'<div class="kb-streifen" aria-label="Kontaktabzug eines Drehtags"><div class="kb-spur">{spur}</div></div></section>')


# ── 1 · Startseite ────────────────────────────────────────────────────────────────────────────────
s = Seite(LIVE_START)
s.ersetze('<h1><span class="w">Mehr Aufträge.</span> <span class="w">Mehr Bewerber.</span> <span class="w">Aus deinem Umkreis.</span></h1>',
          '<h1><span class="w">Dein Handwerk.</span> <span class="w">Unsere Baustelle.</span></h1>')  # Noah, 15.11.2026: „genau passend, ist perfekt“
s.ersetze('<p class="lead">Website, Fotos und Social-Media-Werbung für Handwerksbetriebe.</p>',
          '<p class="lead">Wir bauen deine Website und bringen dir qualifizierte Kunden<br class="dsk-br"> und Mitarbeiter aus deinem Umkreis.</p>')  # Noah, 18.11.2026: „und Mitarbeiter“ in die nächste Zeile
# Aufbau wie shk…/start-neu/: Firma → drei Leistungen (einfache Karten) → Ergebnisse → Stimmen → Team → Kontakt.
# Die drei Säulen in Logo-Form stehen schon im Hero und kommen hier nicht noch einmal (Noah, 14.11.2026);
# Problem-Szenen, Google-Mechanik und Foto-Band stehen auf den Unterseiten.
# Rechte Hero-Säule (Noah, 18.11.2026): „wo jetzt Anfragen und Bewerbungen steht, sollten … die Interviews, also wie auf der
# SHK-Seite … dieses Ding, wo die ganzen Kunden drin sind, wo das dann immer switcht“ → der Kunden-Zusammenschnitt der
# SHK-Seite (firma/website-shk/assets/reels/kunden-szenen.mp4, jeder Betrieb einmal, Match Cut) statt des Drohnen-Clips.
s.h = s.h.replace('/static/assets/vid/saeule/baureize.jpg', '/static/assets/vid/saeule/kunden-szenen.jpg?v=3')
s.ersetze('data-src="/static/assets/vid/saeule/baureize-d.mp4" data-src-mobil="/static/assets/vid/saeule/baureize-m.mp4"',
          'data-src="/static/assets/vid/saeule/kunden-szenen-d.mp4?v=3" data-src-mobil="/static/assets/vid/saeule/kunden-szenen-m.mp4?v=3"')
assert 'baureize' not in s.h.split('<div class="saeulen">', 1)[1].split('</div></div></div>', 1)[0]
# Noah, 18.11.2026: „das Video soll schon das ganz ausfüllen, aber … nicht, dass der Kopf … abgeschnitten ist“ → in den
# Originalen sitzt der Kopf ganz oben; die Beschriftung dieser Säule steht deshalb unten, damit sie nie auf einem Gesicht liegt.
s.h = s.h.replace('</head>', '<style>.saeule:nth-child(3) video{object-position:50% 0}.saeule:nth-child(3) .etikett{top:auto;bottom:clamp(220px,30vh,300px)}</style></head>', 1)  # Noah 18.11.: Kopf nie oben angeschnitten (breite Fenster schneiden sonst oben ab), Beschriftung wieder oben
s.heraus('<section class="sek system-sek" id="system"')
s.heraus('<section class="sek grund lagen-sek probleme pb-sek">')
s.heraus('<section class="sek google grund">')
s.heraus('<section class="sek band auf-dunkel" id="videos">')
PFEIL = '<svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'


def karte(bild, alt, pos, titel, zeile, text, ziel, knopf):
    return (f'<article class="erg reveal"><div class="erg-film"><img src="/start-neu/bilder/{bild}.webp" alt="{alt}" loading="lazy" decoding="async" style="object-position:{pos}"></div>'
            f'<div class="erg-in"><div class="erg-zeile"><em>{titel}</em><span>{zeile}</span></div><p>{text}</p>'
            f'<a class="textlink" href="/{ziel}/">{knopf} {PFEIL}</a></div></article>')


LEISTUNGS_SEK = ('<section class="sek leistungen-sek sg-sek" id="system">' + SIGNET_WACHSEN + '<div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Unsere Leistungen</span>'
                 '<h2>Drei Baustellen<br class="dsk-br"> übernehmen wir für dich.</h2><p class="lead">Jede Leistung gibt es einzeln.</p></div><div class="ergebnisse">'
                 # Fette Zeile = abgenommene H1 der Unterseite, Text je ein kurzer Satz (Noah, 15.11.2026)
                 + karte("zimmerei-schneider", "Zwei Zimmerer von Zimmerei Schneider in der Werkstatt", "50% 30%", "Website", "Wir bauen. Du ziehst ein.",
                         "Eine Seite je Leistung, mit deinem Ort drin.", "websites", "Mehr zur Website")
                 + karte("senftleben-team-wagen", "Das Team von Senftleben Haustechnik vor den Firmenwagen", "50% 30%", "Neue Kunden", "Wir füllen dein Auftragsbuch.",
                         "Anfragen aus deinem Umkreis, direkt an dich.", "neukundengewinnung", "Mehr zu neuen Kunden")
                 + karte("erwin-schmidt-team", "Das Team von Erwin Schmidt &amp; Sohn", "50% 30%", "Neue Mitarbeiter", "Verstärkung ist unterwegs.",
                         "Bewerbungen von Fachkräften aus deinem Umkreis.", "mitarbeitergewinnung", "Mehr zu neuen Mitarbeitern")
                 + f'</div><p class="leistungen-zusatz reveal">Die Fotos und Videos dafür drehen wir bei dir im Betrieb. <a class="textlink" href="/foto-video/">Foto &amp; Video {PFEIL}</a></p></div></section>'
                 '<style>/* Entwurf (start-neu/bauen.py) */.leistungen-zusatz{margin-top:28px;font-size:17px;line-height:1.5;color:var(--tinte-2)}'
                 '.leistungen-sek .erg-zeile em{font-size:clamp(24px,2.2vw,30px)}'
                 # Kartentext in allen drei Karten gleich viele Zeilen (der dritte Satz ist breiter als die Karte, also alle drei balanciert zweizeilig)
                 '.leistungen-sek .erg-in p{max-width:24ch;text-wrap:balance}'
                 # Sektionsköpfe der Startseite in EINER Machart (Noah, 15.11.2026): Ohne Lead lief die H2 über die volle
                 # Breite („Wir lassen unsere Kunden sprechen.“ einzeilig, .stimmen h2 max-width:none), mit Lead nur 16ch.
                 # Jetzt jede linksbündige H2 höchstens 16ch, text-wrap:balance verhindert ein Einzelwort in der letzten Zeile.
                 '.sek .kopfzeile:not(.mitte)>h2{max-width:16ch}'
                 '.uk-bild .collage img{background:var(--papier-2,#efe9df)}.uk-bild .collage img.raus{opacity:.35;transform:none}</style>')
s.vor('<section class="sek laufband" id="gefunden">', LEISTUNGS_SEK)
s.ersetze('<span class="kicker">Deine Website</span>', '<span class="kicker">Unsere Websites</span>')
# Kicker ohne Mittelpunkt, der wirkt maschinell (Noah, 15.11.2026)
s.ersetze('<span class="kicker">Kostenloses Beratungsgespräch · 30 Min.</span>', '<span class="kicker">Kostenloses Beratungsgespräch</span>')
# „Wer dahinter steht“: klare Überschrift, „Seit 2019 nur Handwerk“ als Kicker, Noahs Vorstellung als Text (Noah, 15.11.2026)
# Noah, 15.11.2026: die fünf Zeilen über die Familie waren zu lang, genau diese zwei Sätze (auch auf /ueber-uns/)
NOAH_TEXT = 'Servus, ich bin Noah, Gründer der Handwerksmanufaktur. Dass wir nur fürs Handwerk arbeiten, kommt nicht von ungefähr.</p><p class="lead" style="margin-top:20px">Meine drei Brüder haben alle im Handwerk gelernt. Zwei davon sind Meister. Zusätzlich haben wir in der Familie mehrere Handwerksbetriebe. Dadurch habe ich schon von klein auf täglich mitgekriegt, wie es im Handwerk wirklich zugeht.</p><p class="lead" style="margin-top:20px">In den letzten 8 Jahren haben wir über 150 Firmen betreut und wissen mittlerweile ganz genau, was ein Handwerksbetrieb online braucht, damit Kunden und Bewerber bei ihm landen.'
s.ersetze('<span class="kicker">Wer dahinter steht</span><h2>Die Leute hinter deinem Auftritt.</h2><p class="lead">Dieselben Leute von Anfang bis Ende.</p>',
          f'<span class="kicker">Du bist auf der Baustelle daheim. Wir im Internet.</span><h2 style="max-width:none;font-size:clamp(23px,3.75vw,54px)">Wer hinter der<br><span style="white-space:nowrap">Handwerksmanufaktur steht.</span></h2>')
# Noah, 18.11.2026: „bei der Home-Seite … den ‚Über uns‘-Text rausnehmen … dass da einfach nur das Team mit dabei steht.
# Dann ist halt noch der Button ‚Mehr über uns‘“ — der Text steht nur noch auf /ueber-uns/.


def ergebnisse_aktuell(seite):
    """Kundenfotos + Stimpfle-Zahlen wie auf der SHK-Seite abgenommen (Noah, 14.11.2026 nachts): Sussmann Foto 6, Stimpfle Foto 3."""
    h = seite.h
    h = re.sub(r"<img data-k='[^']*' src=\"/static/assets/img/_800/fall/sussmann-team\.webp\" alt=\"\"",
               '<img src="/start-neu/bilder/sussmann-wagen-duo.webp" alt="Patrick und Mirjana von Sussmann vor dem Firmenwagen" style="object-position:50% 30%"', h)
    h = h.replace('<img src="/static/assets/img/_800/fall/stimpfle-team.webp" alt="Drei Monteure von Stimpfle Sanitär und Heizung vor dem Firmenwagen" loading="lazy" decoding="async" style="object-position:50% 22%">',
                  '<img src="/start-neu/bilder/stimpfle-werkstatt.webp" alt="Das Team von Stimpfle Sanitär und Heizung in der Werkstatt" loading="lazy" decoding="async" style="object-position:50% 30%">')
    h = h.replace('<em>3 Bad-Anfragen</em><span>in den ersten 3 Tagen</span>', '<em>7 Bad-Anfragen</em><span>3 Vor-Ort-Termine in den ersten 3 Tagen</span>')
    h = h.replace('Die Werbung läuft seit dem 29. Oktober im Umkreis von Stadtbergen.', 'Die Anzeigen laufen seit dem 29. Oktober im Umkreis von Stadtbergen.')
    h = h.replace('die Werbung pausiert deshalb bis Februar.', 'die Anzeigen pausieren deshalb bis Februar.')
    h = h.replace('<p class="lead">Werbung im Umkreis des Betriebs. Gezählt ist', '<p class="lead">Anzeigen im Umkreis des Betriebs. Gezählt ist')
    h = h.replace('<h2>Du kümmerst dich um nichts davon.</h2>', '<h2>Wir lassen unsere Kunden sprechen.</h2>')
    seite.h = h


# Einleitung darunter war Füllstoff, die Karten sprechen für sich (Noah, 15.11.2026)
s.ersetze('<span class="kicker">Facebook &amp; Instagram</span><h2>Echte Betriebe, echte Zahlen.</h2><p class="lead">Werbung im Umkreis des Betriebs. Gezählt ist jede Anfrage und jede Bewerbung, die angekommen ist.</p>',
          '<span class="kicker">Fallstudien</span><h2>Ergebnisse unserer Kunden.</h2>')
ergebnisse_aktuell(s)
s.ersetze('<section class="sek team-sek" id="team">', '<section class="sek team-sek sg-sek" id="team">' + SIGNET_RUHE)
_a, _e = s.bereich('<section class="sek stimmen">')
_sek = s.h[_a:_e]
_sek2, _n = re.subn(r'<div class="bahn" aria-hidden="false">.*</div>(?=</section>)', lambda m: stimmen_alle(), _sek, count=1, flags=re.S)
assert _n == 1 and _sek2.count('class="stimme ') == 92, _sek2.count('class="stimme ')  # 46 mit Logo, je Reihe doppelt
s.h = s.h[:_a] + _sek2 + s.h[_e:]
assert s.h.count('<h2>So sehen unsere Seiten aus.</h2>') == 1
s.h = s.h.replace('<h2>So sehen unsere Seiten aus.</h2>', '<h2>Bezugsfertig.</h2>')  # wie auf der Websites-Seite
s.entwurf()
s.schreibe(ZIEL / "index.html")


def unterseite(slug):
    return Seite((QUELLE / f"{slug}.html").read_text())


def hero_knopf(seite, alt_href, neu_href, text="Ergebnisse ansehen"):
    seite.ersetze(f'<a class="btn btn-umriss" href="{alt_href}">Arbeiten ansehen</a>',
                  f'<a class="btn btn-umriss" href="{neu_href}">{text}</a>')


# ── 2–6 · Unterseiten: so einfach wie die Startseite (Noah, 14.11.2026 abends: „alle unterseiten müssen simpler … die
# simpelheit muss komplett übernommen werden, copy auch“). Je Seite höchstens sieben Sektionen mit einem Faden:
# Hero → Das Problem (zwei Karten Heute / Mit uns) → Was wir übernehmen (drei Karten) → Die Ergebnisse → Kundenstimmen
# → Häufige Fragen → Kontakt. Reiter-Szenen, Bento, Abläufe, Ratgeber-Raster, Gewerke-Listen stehen im Entwurf nicht mehr.
UNTER_STIL = ('<style>/* Entwurf Unterseiten (start-neu/bauen.py) */'
              '.pv{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--gap);margin-top:clamp(26px,3vw,40px)}'
              '.pv-k{background:var(--papier);border-radius:var(--radius);box-shadow:0 0 0 1px rgba(22,19,14,.06);padding:clamp(24px,3vw,40px);transition:transform var(--schnell),box-shadow var(--schnell)}'
              '.pv-k:hover{transform:translateY(-4px);box-shadow:0 30px 60px -30px rgba(22,19,14,.4),0 0 0 1px rgba(22,19,14,.08)}'
              '.pv-k.mit{background:var(--tinte);color:var(--papier)}'
              '.pv-m{display:block;font-size:14px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--tinte-2)}'
              '.pv-k.mit .pv-m{color:var(--bronze)}'
              '.pv-k ul{list-style:none;padding:0;margin:20px 0 0;display:grid;gap:16px}'
              '.pv-k li{display:grid;grid-template-columns:28px minmax(0,1fr);gap:14px;align-items:start;font-size:18px;line-height:1.45}'
              '.pv-k li::before{content:"✕";display:grid;place-items:center;width:28px;height:28px;border-radius:50%;background:var(--papier-2);color:var(--tinte-2);font-size:14px;font-weight:700;letter-spacing:.01em}'
              '.pv-k.mit li::before{content:"✓";background:var(--bronze);color:var(--tinte)}'
              '.uebernehmen-sek .erg-zeile em{font-size:clamp(24px,2.2vw,30px)}'
              '@media (max-width:900px){.pv{grid-template-columns:1fr}.pv-k li{font-size:17px}}</style>')


def problem(h2, heute, mit):
    li = lambda zeilen: "".join(f"<li><span>{z}</span></li>" for z in zeilen)
    return ('<section class="sek grund problem-sek"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Das Problem</span>'
            f'<h2>{h2}</h2></div><div class="pv reveal"><div class="pv-k"><b class="pv-m">Heute</b><ul>{li(heute)}</ul></div>'
            f'<div class="pv-k mit"><b class="pv-m">Mit uns</b><ul>{li(mit)}</ul></div></div></div></section>')


def uebernehmen(h2, karten):
    k = "".join(f'<article class="erg reveal"><div class="erg-film"><img src="/start-neu/bilder/{b}.webp" alt="{alt}" loading="lazy" decoding="async" style="object-position:{pos}"></div>'
                f'<div class="erg-in"><div class="erg-zeile"><em>{titel}</em><span>{zeile}</span></div><p>{text}</p></div></article>'
                for b, alt, pos, titel, zeile, text in karten)
    return ('<section class="sek uebernehmen-sek"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Was wir übernehmen</span>'
            f'<h2>{h2}</h2></div><div class="ergebnisse">{k}</div></div></section>' + UNTER_STIL)


def einfach(seite, lead, behalten, fragen_lead=None):
    """Hero-Einleitung auf einen Satz, alle Sektionen außer Hero, `behalten` (Kicker der Ergebnis-Sektionen), Fragen, Kontakt raus."""
    a, e = seite.bereich('<section class="hero-klein">')
    hero = seite.h[a:e]
    assert hero.count('<p class="lead">') == 1
    hero = re.sub(r'<p class="lead">.*?</p>', f'<p class="lead">{lead}</p>', hero, count=1, flags=re.S)
    seite.h = seite.h[:a] + hero + seite.h[e:]
    for m in reversed(list(re.finditer(r'<section class="sek[^"]*"[^>]*>', seite.h))):
        kopf = seite.h[m.start():m.start() + 1500]
        k = re.search(r'<span class="kicker">([^<]*)</span>', kopf)
        if 'umkreis-kontakt' in m.group() or 'sek faq' in m.group() or (k and k.group(1) in behalten):
            continue
        tiefe = 0
        for n in re.compile(r"<section\b|</section>").finditer(seite.h, m.start()):
            tiefe += 1 if n.group() == "<section" else -1
            if tiefe == 0:
                seite.h = seite.h[:m.start()] + seite.h[n.end():]
                break
    a, e = seite.bereich('<section class="sek faq">')
    faq = seite.h[a:e]
    faq = re.sub(r'<span class="kicker">[^<]*</span><h2>Häufige Fragen\.</h2>', '<span class="kicker">Häufige Fragen</span><h2>Das fragen fast alle vorher.</h2>', faq, count=1)
    assert 'Das fragen fast alle vorher.' in faq
    if fragen_lead:
        faq = re.sub(r'(<h2>Das fragen fast alle vorher\.</h2>)<p class="lead">.*?</p>', rf'\1<p class="lead">{fragen_lead}</p>', faq, count=1, flags=re.S)
    assert len(re.findall(r'<details|class="frage"|<summary', faq)) >= 1
    seite.h = seite.h[:a] + faq + seite.h[e:]


# Überschriften im Ton von oevermann & oevermann, von Noah am 15.11.2026 für alle Unterseiten freigegeben
# (Startseite folgt, sobald er dort gewählt hat). Je Seite: H1, „Was wir übernehmen“, Ergebnisse.
FASSUNG = {
    "websites": [('<h1>Die Website, die abends um zehn den Auftrag holt.</h1>', '<h1>Wir bauen. Du ziehst ein.</h1>'),
                 ('<h2>Die ganze Seite übernehmen wir.</h2>', '<h2>Vom Rohbau bis zur Schlüsselübergabe.</h2>'),
                 ('<h2>So sehen unsere Seiten aus.</h2>', '<h2>Bezugsfertig.</h2>')],
    "suchmaschinenoptimierung": [('<h1>Dein nächster Kunde googelt gerade.</h1>', '<h1>Ganz oben ist dein Platz.</h1>'),
                 ('<h2>Den Weg nach vorn übernehmen wir.</h2>', '<h2>Vom ersten Suchwort bis Seite 1.</h2>'),
                 ('<h2>{SEITE1} Kundenseiten stehen auf Seite 1.</h2>', '<h2>{SEITE1}-mal Richtfest.</h2><p class="lead">{SEITE1} Kundenseiten stehen bei Google auf Seite 1.</p>')],
    "foto-video": [('<h1>Fotos, auf denen man deinen Betrieb wiedererkennt.</h1>', '<h1>Wir setzen dein Handwerk ins Licht.</h1>'),
                 ('<h2>Den Drehtag übernehmen wir.</h2>', '<h2>Vom ersten Bild bis zum fertigen Film.</h2>')],
    "neukundengewinnung": [('<h1>Die Aufträge, die du willst. Nur für deinen Betrieb.</h1>', '<h1>Wir füllen dein Auftragsbuch.</h1>'),
                 ('<h2>Die Anzeigen übernehmen wir.</h2>', '<h2>Von der Anzeige bis zum Aufmaß.</h2>'),
                 ('<h2>„Dass so schnell so viele Anfragen kommen, hätte ich nicht gedacht.“</h2>', '<h2>Schwarz auf weiß.</h2><p class="lead">„Dass so schnell so viele Anfragen kommen, hätte ich nicht gedacht.“</p>')],
    "mitarbeitergewinnung": [('<h1>Leute, die bei dir anfangen wollen. Aus deinem Umkreis.</h1>', '<h1>Verstärkung ist unterwegs.</h1>'),
                 ('<h2>Die Suche übernehmen wir.</h2>', '<h2>Von der Anzeige bis zum Handschlag.</h2>'),
                 ('<h2>„Wir haben nur nicht gedacht, dass es so viele sind.“</h2>', '<h2>25 Bewerbungen. 4 Wochen. 1 Neuer.</h2><p class="lead">„Wir haben nur nicht gedacht, dass es so viele sind.“</p>')],
}


def fertig(seite, slug, hero=None):
    ergebnisse_aktuell(seite)
    hero_neu(seite, slug, *hero)
    for alt, neu in FASSUNG.get(slug, []):
        # Zahl der Seite-1-Kundenseiten rechnet nur_website_kunden() aus der Liste, nie fest verdrahtet (16.11.2026)
        alt, neu = (x.replace("{SEITE1}", str(globals().get("SEITE1"))) for x in (alt, neu))
        assert seite.h.count(alt) == 1, (slug, alt, seite.h.count(alt))
        seite.h = seite.h.replace(alt, neu)
    seite.entwurf()
    assert 'Werbung' not in "".join(re.findall(r'<h[123][^>]*>.*?</h[123]>', seite.h, re.S)), slug
    seite.schreibe(ZIEL / slug / "index.html")


# ── 2 · Websites
w = unterseite("websites")
einfach(w, 'Wir bauen deine Website mit Fotos aus deinem Betrieb und einer eigenen Seite je Leistung, damit der Kunde bei dir anruft.', ('Unsere Seiten',),
        fragen_lead='Preis, Dauer und was mit der alten Seite passiert.')
w.ersetze('<span class="kicker">Unsere Seiten</span><h2>Jedes Gewerk bekommt seine eigene Seite.</h2>', '<span class="kicker">Die Ergebnisse</span><h2>So sehen unsere Seiten aus.</h2>')
# Füll-Einleitungen auf einen schlichten Satz (Noah, 15.11.2026)
w.ersetze('<p class="lead">Jede mit Fotos aus dem eigenen Betrieb, jede auf ihr Gewerk und ihren Umkreis gebaut. Fahr über eine Seite, dann scrollt sie durch.</p>',
          '<p class="lead">Alle live. Tipp eine an.</p>')
w.nach('<section class="hero-klein">',
       problem('Gute Arbeit, aber keiner findet dich.',
               ['Wer abends dein Gewerk und deinen Ort googelt, findet den Wettbewerber auf Seite 1.', 'Dich findet er auf Seite 3.', 'Die alte Seite kostet dich Anfragen.'],
               ['Jede Leistung hat ihre eigene Seite, mit deinem Ort drin.', 'Auf der Seite stehen Fotos aus deinem Betrieb statt Katalogbilder.', 'Die Anfrage steht im ersten Bild, bevor jemand scrollt.'])
       + uebernehmen('Die ganze Seite übernehmen wir.', [
           ('u-ziel', 'Zwei Männer am Tisch mit Laptop im Küchenhaus Hirschvogel', '50% 30%', 'Das Ziel', 'Zuerst klären wir die Richtung.', 'Welche Aufträge die Seite bringen soll und wo dich die alte Seite heute Anfragen kostet.'),
           ('u-aufnahmen', 'Zwei Männer in der Halle von CS Metalldesign', '50% 30%', 'Die Aufnahmen', 'Kamera und Drohne bei dir vor Ort.', 'Deine Leute und deine Baustellen statt Katalogbilder.'),
           ('u-freigabe', 'Handschlag in der Werkstatt der Schreinerei Kreitner', '50% 30%', 'Die Seite', 'Wir bauen, du schaust drüber.', 'Die fertige Seite kommt als Link aufs Handy und du gibst sie frei.')]))
w.vor('<section class="sek faq">', STIMMEN)
fertig(w, "websites", (hero_websites(), 7000))

# ── 3 · Suchmaschinenoptimierung
g = unterseite("suchmaschinenoptimierung")
SEITE1 = nur_website_kunden(g)
einfach(g, 'Dein nächster Kunde tippt dein Gewerk und deinen Ort ein und ruft den an, der oben steht.', ('Nachgemessen, nicht behauptet',),
        fragen_lead='Wie lange es dauert und ob es auch in der Großstadt geht.')
hero_knopf(g, "/websites/#arbeiten", "#ergebnisse")
g.ersetze('<section class="sek grund rangliste-sek"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Nachgemessen, nicht behauptet</span><h2>Wo unsere Kunden bei Google wirklich stehen.</h2>',
          f'<section class="sek grund rangliste-sek" id="ergebnisse"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Die Ergebnisse</span><h2>{SEITE1} Kundenseiten stehen auf Seite 1.</h2>')
g.nach('<section class="hero-klein">',
       problem('Der Wettbewerber steht vor dir.',
               ['Heizung, Bad und Wartung stehen auf einer Seite. Gefunden wird davon nichts.', 'Das Google-Profil ist nicht gepflegt.', 'Die Seite lädt am Handy vier Sekunden und rutscht ab.'],
               ['Jede Leistung hat ihre eigene Seite mit Ort.', 'Dein Google-Profil ist aufgebaut und gepflegt.', 'Die Seite lädt schnell, auch am Handy.'])
       + uebernehmen('Den Weg nach vorn übernehmen wir.', [
           ('u-leistung-ort', 'Haus mit Photovoltaik-Anlage von Wohner Elektrotechnik aus der Luft', '50% 50%', 'Die Seiten', 'Eine je Leistung, mit Ort.', '„Badsanierung Landsberg“ bekommt eine eigene Seite.'),
           ('u-profil', 'Dach mit Blecheindeckung von Dachbau Kraus', '50% 50%', 'Das Google-Profil', 'Aufgebaut und gepflegt.', 'Mit Leistungen und Fotos, damit dich die Karte zeigt.'),
           ('u-bewertung', 'Handschlag auf dem Hof von Kirchner in Thaining', '50% 30%', 'Die Bewertungen', 'Sie kommen von selbst.', 'Ein Link nach jedem Auftrag, der Rest läuft.')]))
g.vor('<section class="sek faq">', STIMMEN)
fertig(g, "suchmaschinenoptimierung", (hero_seo(g),))

# ── 4 · Foto & Video (zwei Ergebnis-Sektionen wie die Startseite: Filme + Fotos; dafür ohne Kundenstimmen)
f = unterseite("foto-video")
einfach(f, 'Wir kommen einen Tag mit Kamera und Drohne zu dir, danach hast du Bilder und Filme für deine Website und deine Anzeigen.',
        ('Am Drehtag entstanden', 'Aus unseren Shootings'))
hero_knopf(f, "/websites/#arbeiten", "#ergebnisse", "Arbeiten ansehen")
f.ersetze('<section class="sek band auf-dunkel"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Am Drehtag entstanden</span><h2>Ein Drehtag, daraus der Film für deine Startseite und die Clips für deine Anzeigen.</h2>',
          '<section class="sek band auf-dunkel" id="ergebnisse"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Die Filme</span><h2>Diese Filme sind am Drehtag entstanden.</h2>')
f.ersetze('<span class="kicker">Aus unseren Shootings</span>', '<span class="kicker">Die Fotos</span>')
f.ersetze('<p class="lead">Der Chef erzählt, die Drohne zeigt den Hof, die Kamera steht an der Maschine. Diese sechs Filme sind so bei unseren Kunden entstanden, gedreht im laufenden Betrieb. Die Fragen schreiben wir vorher, du musst nichts auswendig lernen.</p>',
          '<p class="lead">Entstanden im laufenden Betrieb unserer Kunden.</p>')
f.ersetze('<p class="lead">Hallen, Baustellen, Bäder und Werkstätten, von der Zimmerei bis zur Haustechnik. Jedes Bild ist an einem Drehtag bei einem Kunden entstanden, mit den Leuten, die dort arbeiten.</p>',
          '<p class="lead">Jedes Bild ist an einem Drehtag bei einem Kunden entstanden.</p>')
f.nach('<section class="hero-klein">',
       problem('Deine Arbeit ist besser als deine Bilder.',  # Noah, 18.11.2026: „bitte nicht so schlechte copy“

               ['„Aktuelle Fotos haben wir keine“, hören wir fast in jedem Erstgespräch.', 'Auf der Seite stehen Katalogbilder.', 'Wer vergleicht, erkennt deinen Betrieb nicht wieder.'],
               ['Auf den Bildern stehen deine Leute vor deinen Fahrzeugen.', 'Fotografiert wird im laufenden Betrieb.', 'Alle Fotos und Filme gehören dir, in voller Auflösung.'])
       + uebernehmen('Den Drehtag übernehmen wir.', [
           ('fv-motivliste', 'Hand zeichnet auf einem Plan bei Küchenhaus Hirschvogel', '50% 45%', 'Die Motivliste', 'Vorher am Telefon.', 'Wir klären, was Website und Anzeigen brauchen, und haken die Liste am Drehtag ab.'),
           ('fv-drehtag', 'Fotograf Robert mit der Fernsteuerung der Drohne', '50% 8%', 'Der Drehtag', 'Ein Tag bei dir.', 'Wir fotografieren und filmen, was bei dir ohnehin passiert, und dein Betrieb läuft weiter.'),
           ('fv-uebergabe', 'Hände legen Holzmuster bei Küchenhaus Hirschvogel auf den Tisch', '50% 50%', 'Die Übergabe', 'Alles gehört dir.', 'Du bekommst alle Fotos und Filme in voller Auflösung.')]))
# Filme + Fotowand weichen der Galerie direkt unter dem Hero; der Kontaktabzug steht vor den Fragen (sieben Sektionen bleiben)
f.heraus('<section class="sek band auf-dunkel" id="ergebnisse">')
f.heraus('<section class="sek fotowand-sek">')
f.nach('<section class="hero-klein">', galerie_sek())
f.vor('<section class="sek faq">', kontaktabzug_sek())
# Collage im Kontakt-Block: auf Foto & Video ohne die Bilder, auf denen Noah mit Kunden steht (Noah, 18.11.2026)
NOAH_MIT_KUNDEN = ("c07", "c18", "c25", "c27", "c39", "c50", "c60", "c69")
_m = re.search(r"data-pool='(\[.*?\])'", f.h)
_pool = [e for e in _json.loads(_m.group(1)) if not any(f"/{c}.webp" in e[0] for c in NOAH_MIT_KUNDEN)]
assert len(_pool) == len(_json.loads(_m.group(1))) - len(NOAH_MIT_KUNDEN), len(_pool)
f.h = f.h[:_m.start(1)] + _json.dumps(_pool, separators=(",", ":")) + f.h[_m.end(1):]
fertig(f, "foto-video", (hero_foto_video(), 6500))

# ── 5 · Neukundengewinnung
n = unterseite("neukundengewinnung")
einfach(n, 'Anzeigen mit deinen Leuten, nur in deinem Umkreis, und jede Anfrage gehört dir allein.', ('Fallstudie · Badsanierung',))
hero_knopf(n, "/websites/#arbeiten", "#ergebnisse")
n.ersetze('<section class="sek grund"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Fallstudie · Badsanierung</span>',
          '<section class="sek grund" id="ergebnisse"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Die Ergebnisse</span>')
n.ersetze('<span class="nr" data-zahl="14">14</span><span class="fz-einheit">Bad-Anfragen</span></div><p>Daraus sieben Termine vor Ort und nach 18 Tagen der erste Auftrag.</p>',
          '<span class="nr" data-zahl="37">37</span><span class="fz-einheit">Bad-Anfragen</span></div><p>Daraus zwölf Termine vor Ort, der erste Auftrag kam nach 18 Tagen.</p>')  # Stand wie Startseite (37 / 12)
n.ersetze('Pflicht ist es nicht — es geht auch mit deinem Vorarbeiter.', 'Pflicht ist es nicht, es geht auch mit deinem Vorarbeiter.', 2)
n.ersetze('Sein Argument: Werbung macht man nicht erst, wenn es schlechter läuft, sondern damit man dann schon bekannt ist.',
          'Sein Argument: Wer erst wirbt, wenn es schlechter läuft, ist dann noch nicht bekannt.', 2)
n.nach('<section class="hero-klein">',
       problem('Drei Wochen voll, dann wieder Zufall.',
               ['Empfehlungen kannst du nicht bestellen, wenn ein großes Projekt wegbricht.', 'Im Lead-Portal geht dieselbe Anfrage an vier Betriebe gleichzeitig.', 'Auf der Vergabeplattform bekommt den Auftrag, wer am billigsten ist.'],
               ['Die Anzeige läuft nur 25 Kilometer um deinen Betrieb.', 'Vier Filterfragen stehen vor jeder Anfrage.', 'Jede Anfrage gehört dir allein.'])
       + uebernehmen('Die Anzeigen übernehmen wir.', [
           ('u-anzeige', 'Patrick und Mirjana von Sussmann vor dem Firmenschild', '50% 30%', 'Die Anzeige', 'Mit deinen Leuten drauf.', 'Man erkennt den Betrieb aus dem Nachbarort, deshalb bleibt sie im Feed hängen.'),
           ('u-umkreis', 'Senftleben Haustechnik mit Team und Firmenwagen aus der Luft', '50% 50%', 'Der Umkreis', 'Nur 25 Kilometer um deinen Betrieb.', 'Wer 60 Kilometer weiter ein Projekt plant, sieht sie nicht.'),
           ('u-filter', 'Zwei Mitarbeiter von Sussmann neben einem Speicher', '50% 30%', 'Die Filterfragen', 'Vier Fragen vor jeder Anfrage.', 'Bei dir kommt an, wer sein Projekt ernst meint, mit Name und Nummer.')]))
n.vor('<section class="sek faq">', STIMMEN)
fertig(n, "neukundengewinnung", (hero_anzeigen("h-sussmann", ("su-patrick", "su-dusche", "su-mirjana"), "su-dusche", "Erich Sussmann", "Gesponsert",
                                                 ("Unsere Anzeigen", "für Erich Sussmann, Kirchheim")),))

# ── 6 · Mitarbeitergewinnung
m = unterseite("mitarbeitergewinnung")
einfach(m, 'Die Guten suchen nicht, also bringen wir deine Stelle dorthin, wo sie jeden Abend sind.', ('Fallstudie · Anlagenmechaniker SHK',),
        fragen_lead='Was es kostet, wie lange es dauert und was du selbst dafür tun musst.')
hero_knopf(m, "/websites/#arbeiten", "#ergebnisse")
m.ersetze('<section class="sek grund"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Fallstudie · Anlagenmechaniker SHK</span>',
          '<section class="sek grund" id="ergebnisse"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Die Ergebnisse</span>')
m.nach('<section class="hero-klein">',
       problem('Die Guten suchen nicht.',
               ['Im Stellenportal meldet sich, wer gerade keine Arbeit hat.', 'Den Aufkleber am Firmenwagen liest, wer an der Ampel hinter dir steht.', '„Wir suchen dich“ auf der eigenen Seite liest nur, wer den Betrieb schon kennt.'],
               ['Deine Stelle läuft auf Instagram und Facebook, 30 Kilometer um deinen Betrieb.', 'Deine Mannschaft steht in der Anzeige.', 'Die Bewerbung dauert zwei Minuten, ohne Anschreiben und Lebenslauf.'])
       + uebernehmen('Die Suche übernehmen wir.', [
           ('u-mannschaft', 'Das Team von Erwin Schmidt &amp; Sohn trägt lachend eine Kollegin', '50% 30%', 'Die Anzeige', 'Mit deiner Mannschaft.', 'Sie läuft abends auf Instagram und Facebook, nur im Umkreis um den Betrieb.'),
           ('u-bewerbung', 'Monteur von Erwin Schmidt &amp; Sohn mit Zange im Lager', '50% 25%', 'Die Bewerbung', 'Zwei Minuten am Handy.', 'Vier Filterfragen statt Anschreiben und Lebenslauf.'),
           ('u-gespraech', 'Drei Monteure von Heizung-Sanitär Klaß vor dem Firmenwagen', '50% 30%', 'Das Gespräch', 'Du rufst an.', 'Die Bewerbung kommt mit Nummer und Antworten, du führst nur noch die Gespräche.')]))
m.vor('<section class="sek faq">', STIMMEN)
fertig(m, "mitarbeitergewinnung", (hero_anzeigen("h-irlbacher", ("ir-nummer", "ir-montage", "ir-geselle"), "ir-montage", "Irlbacher", "Gesponsert",
                                                   ("Unsere Stellenanzeigen", "für Irlbacher")),))

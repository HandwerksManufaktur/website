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
sys.path.insert(0, str(Path(__file__).resolve().parent))
from kunden_links import entlinken, rest as kunden_rest
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


def farblogo_marke(k):
    """Farblogo ohne dunklen Kasten, optisch gleich groß: gleiche Fläche im festen Rahmen 104 × 44 (Noah, 21.11.2026)."""
    from PIL import Image as _Im
    _w, _h = _Im.open(WURZEL / f"static/assets/img/logos/farbe/{k}.png").size
    _r = _w / _h
    _RB, _RH, _FL = 104, 44, 3900
    _rb = 130 if _r > 3.5 else _RB   # sehr flache Schriftzüge (Süßmeier) breiter, sonst winzig
    _rh = 60 if _r < 1.1 else _RH    # hohe/quadratische Marken (Rieger) höher, sonst winzig
    lb = min((_FL * _r) ** .5, _rb); lh = lb / _r
    if lh > _rh:
        lh = _rh; lb = lh * _r
    return (f'<span class="st-logo"><img loading="lazy" src="/static/assets/img/logos/farbe/{k}.png" alt="" '
            f'width="{round(lb)}" height="{round(lh)}" decoding="async"></span>')


ST_LOGO_CSS = ('.sek.stimmen .st-logo{display:flex;align-items:center;justify-content:center;flex:none;width:130px;height:60px;background:none;padding:0;border-radius:0}'
               '.sek.stimmen .st-logo img{display:block;max-width:130px;max-height:60px}')  # Breite/Höhe aus den Attributen (gleiche Fläche), nicht die natürliche Bildgröße


def stimmen_farblogos(h):
    """Unterseiten: weiße Logos im dunklen Kasten → Farblogos ohne Kasten (Auswahl der Stimmen bleibt)."""
    def ein(m):
        return farblogo_marke(STIMME_FARBE[m.group(1)])
    h, n = re.subn(r'<span class="kreis logo dunkel"><img[^>]*src="/static/assets/img/logos/w/([^"]+)"[^>]*></span>', ein, h)
    assert 'kreis logo dunkel' not in h, "Stimme ohne Logo"
    return h + f'<style>{ST_LOGO_CSS}</style>'


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
            marke = farblogo_marke(STIMME_FARBE[logo])
        else:
            ini = ''.join(w[0] for w in re.sub(r'[^A-Za-zÄÖÜäöü ]', '', name).split()[:2]).upper()
            marke = f'<span class="st-logo"><span class="st-ini">{ini}</span></span>'
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
            '<style>.stimme .st-ini{font-size:18px;font-weight:800;letter-spacing:.02em;color:var(--tinte)}'
            # Gleich hohe Karten; die Schrift wächst bei kurzen Stimmen, ein großes Anführungszeichen trägt die Karte
            '.sek.stimmen .stimme{position:relative;overflow:hidden;min-height:330px;grid-template-rows:auto auto 1fr;align-content:stretch;transition:transform .35s cubic-bezier(.2,.8,.2,1),box-shadow .35s}'
            '.sek.stimmen .stimme:hover{transform:translateY(-4px);box-shadow:0 18px 40px -22px rgba(22,19,14,.35),0 0 0 1px rgba(22,19,14,.08)}'
            '.sek.stimmen .stimme::before{content:"\\201C";position:absolute;right:22px;top:6px;font-size:120px;line-height:1;font-weight:800;color:var(--bronze);opacity:.16;pointer-events:none}'
            # Eine Schrift für alle Stimmen, oben bündig unter den Sternen (Noah, 20.11.2026: „die Abstände passen nicht … auf
            # einmal ist da Knappich … fett“ — kurze Stimmen standen größer, fett und tiefer)
            '.sek.stimmen .stimme p{align-self:start;color:var(--tinte);font-size:16px;line-height:1.55;font-weight:400;letter-spacing:0}'
            '.sek.stimmen .st-logo{display:flex;align-items:center;justify-content:center;flex:none;width:130px;height:60px;background:none;padding:0;border-radius:0}.sek.stimmen .st-logo img{display:block;max-width:130px;max-height:60px}'
            '@media (prefers-reduced-motion:reduce){.sek.stimmen .stimme{transition:none}}</style>')


STIMME_FARBE = {'logo-elektro-langmajer.webp': 'langmajer', 'logo-schwaighofer-betontechnik-logo.webp': 'schwaighofer', 'logo-oswald-bau-weil.webp': 'oswald-bau', 'logo-planung-hindelang.webp': 'hindelang', 'logo-zimmerei-koller.webp': 'koller', 'logo-malermeister-mueller-weiss.webp': 'mueller', 'logo-gattinger-gmbh.webp': 'gattinger', 'logo-wegele-bau-gmbh-utting.webp': 'wegele-bau', 'logo-zimmerei-pfoederl.webp': 'pfoederl', 'logo-yannick-stimpfle-logo.webp': 'stimpfle', 'logo-ruf-frischdienst.webp': 'ruf-frischdienst', 'wohner_elektrotechnik_weiss_cropped.webp': 'wohner', 'logo-bjoern-schillinger.webp': 'schillinger', 'logo-zimmerei-knappich.webp': 'knappich', 'logo-sd-hirsch-weiss.webp': 'sdhirsch', 'logo-allplast-laser.webp': 'allplast-laser', 'logo-schreinerei-rupp.webp': 'schreinerei-rupp', 'logo-lagerhaus-graf.webp': 'lagerhaus-graf', 'logo-maser-tankschutz-logo.webp': 'maser', 'logo-kuechenhaus-hirschvogel.webp': 'hirschvogel', 'logo-eckru-cnc.webp': 'eckru-cnc', 'logo-zimmerei-rauschmair.webp': 'zimmerei-rauschmair', 'logo-metallbau-weiss.webp': 'metallbau-weiss', 'logo-hannes-schmidt-gmbh-weiss.webp': 'hannes-schmidt', 'logo-franz-musch.webp': 'franz-musch', 'logo-schreinerei-damnig.webp': 'schreinerei-damnig', 'logo-hohenester-zimmerei.webp': 'hohenester-zimmerei', 'logo-leonhard-rieger.webp': 'leonhard-rieger', 'logo-gutachter-hilbenz.webp': 'gutachter-hilbenz', 'logo-zimmerei-schuster.webp': 'zimmerei-schuster', 'logo-inna-illenseer.webp': 'inna-illenseer', 'logo-jirka-ausbau.webp': 'jirka-ausbau', 'logo-thomas-vogel-holzbau.webp': 'vogel', 'logo-suessmeier-heizungstechnik.webp': 'suessmeier', 'logo-franz-gallenberger.webp': 'gallenberger', 'logo-baustoffe-thaining-kirchner.webp': 'kirchner', 'logo-flyin-bbq-streetfood.webp': 'flyin-bbq', 'logo-schreinerei-kreitner.webp': 'kreitner', 'logo-autohaus-ressle.webp': 'autohaus-ressle', 'logo-juwelier-wagenknecht-weiss.webp': 'wagenknecht', 'logo-eggert-kfz-sachverstaendigenbuero.webp': 'eggert-kfz', 'logo-lanzinger-gmbh-weiss.webp': 'lanzinger', 'logo-doerfler-bau.webp': 'doerfler-bau', 'logo-senftleben-haustechnik.webp': 'senftleben', 'logo-schreinerei-die-fuehrmaenner.webp': 'fuehrmaenner', 'logo-zimmerei-schneider.webp': 'zimmerei-schneider', 'logo-happach-maschinenbau.webp': 'happach'}
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
        assert (n1, n2) in ((1, 1), (0, 0)), (n1, n2)  # (0, 0): fertig() hat Knopf und Dialog schon entfernt
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
                                    '@media (min-width:901px){.leistungen-sek .kopfzeile:has(>.lead),.fotowand-sek .kopfzeile:has(>.lead){grid-template-columns:minmax(0,1.4fr) minmax(0,.6fr)!important}'
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
        # Neue Seitenbilder (Durchlauf beim Drüberfahren) bekommen eine Version, sonst zeigt der Browser das alte (20.11.2026:
        # Schillinger mit dem neu gesetzten Porträt)
        for _k, _v in SEITENBILD_V.items():
            self.h = self.h.replace(f'/static/assets/vid/hero/s{_k}.webp"', f'/static/assets/vid/hero/s{_k}.webp?v={_v}"')
            for _e in ('webm', 'jpg'):  # Laufband-Film + Vorschaubild ebenfalls (Erwin Schmidt, 22.11.2026)
                self.h = self.h.replace(f'/static/assets/vid/hero/h{_k}.{_e}"', f'/static/assets/vid/hero/h{_k}.{_e}?v={_v}"')
        # Kurze Zeile („Alle live.“) steht unter der Überschrift, nicht allein rechts in der Mitte (Noah, 19.11.2026: „random“)
        def _kurz(m):
            lead = re.sub(r"<[^>]+>", "", m.group(2)).strip()
            return m.group(0).replace('<div class="kopfzeile', '<div class="kopfzeile kurz', 1) if len(lead) < 40 else m.group(0)
        self.h = re.sub(r'(<div class="kopfzeile(?! kurz)(?:(?!</div>).)*?<p class="lead">)(.*?)</p></div>', _kurz, self.h, flags=re.S)
        # Kundenseiten zeigen, nie verlinken (Noah, 19.11.2026: „nicht zum Anklicken, nicht zum Antippen“)
        self.h = entlinken(self.h)
        assert not kunden_rest(self.h), (pfad, kunden_rest(self.h)[:3])
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_text(self.h)
        print("✓", pfad.relative_to(WURZEL), len(self.h))


# ── Bausteine aus der Live-Startseite ──────────────────────────────────────────────────────────────
start = Seite(LIVE_START)
PROBLEME = start.heraus('<section class="sek grund lagen-sek probleme pb-sek">')
STIMMEN = start.bereich('<section class="sek stimmen">')
STIMMEN = stimmen_farblogos(start.h[STIMMEN[0]:STIMMEN[1]])


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

NEU_V = "9"
SEITENBILD_V = {"schillinger": 3,  # Porträt „Der Meister“ neu gesetzt (20.11.2026)
                "15": 2,  # Schuster Erisried: Über-uns-Bild + Überschrift neu aufgenommen (22.11.2026)
                "ess": 2}  # Erwin Schmidt: neues Hero-Video der Live-Seite (Noah, 22.11.2026: „läuft noch die alte fassung“)
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


# Showreel (Noah, 18.11.2026): „da müssen die geilsten rein … Start von Zimmerei Koller … CS Metall Design … ein bisschen mehr
# durchmischen. Bei Resch Bau: Das erste Video bei Resch kommt raus, das in der Halle bei Resch kommt raus … eine Quere von
# Kirchner und irgendeines von Baureize“ → je Lage ein Betrieb mit 1–4 Einstellungen, nie zwei Lagen vom selben Betrieb
# hintereinander (auch nicht beim Rücksprung). Clips sr-*.mp4 (1280×720, stumm, letztes Bild 1,2 s stehend für die Überblendung):
#   sr-koller-a  Final Zimmerei Koller 1,86 s (Akkuschrauber) + 3,68 s (Säge, Späne)
#   sr-cs-a      CS Metalldesign 2,04 s (Schweißen, rote Handschuhe) + 5,97 s (Schweißen mit Maske)
#   sr-resch     Resch Bau 1,37 s (Bohrer an der Bewehrung) + 2,70 s (Laser, zwei Mann) + 6,70 s (Schalung) + 8,03 s (Bewehrung binden)
#                — Schild am Anfang (0–1,3 s) und Stallhalle (5,3–6,7 s) raus
#   sr-koller-b  Final 5,48 s (Hof von oben) + 7,28 s (Stapler-Kabine)
#   sr-kirchner  Drohnenflug Kirchner 0503 1,9–3,7 s (Bagger hebt Betonblock, quer) — Noah 18.11. abends: „darf drin bleiben, aber nur kurz“
#   sr-cs-b      CS Metalldesign 7,97 s (Schleifen am Zylinder, 0,92 s) + 9,96–11,90 s (Schleifer lacht, ganze Einstellung, alle
#                30-fps-Bilder mit 25 fps = 2,33 s) — Noah 18.11. abends: „ein geiles Video“ → mehr Zeit
#   sr-koller-c  Final 12,68 s (Kappsäge, Gehörschutz) + 14,48 s (Sägeblatt im Balken)
#   sr-baureize  Baureize 12,67 s (Formatkreissäge) + 20,67 s (grüner Linienlaser)
#   sr-baureize  (19.11.2026) erst der grüne Linienlaser, dann Wolfgang an der Formatkreissäge als letzte Einstellung
#                (Noah: „bei baureize das video wo er an der säge steht mach da bei ihm als letztes hin“)
#   sr-fischer   (19.11.2026) aus dem Imagefilm 2026: Team am Transporter 7,6 s · Drohne Haus mit PV 101,2 s · Drohne Firmengebäude
#                112,8 s — Noah: „Fischer schon … das mit dem Team … Drohnen-Aufnahmen … drei kurze Sachen zusammenschneiden“, Bettina
#                selbst nicht auf Foto & Video (sie steht stehend und lächelnd im Kundenvideo der Startseite)
# Stand 19.11.2026 abends: jede Lage DREI Einstellungen (showreel_szenen.py), CS-Schleifer zuerst (Noah: „das kommt als
# Allererstes, weil dieses Video richtig geil ist“); nie zwei Lagen vom selben Betrieb hintereinander, auch nicht über die Schleife.
SHOWREEL = [("CS Metalldesign", "sr-cs-b", 4.45), ("Zimmerei Koller", "sr-koller-a", 4.2), ("A. Resch Bau", "sr-resch", 5.02),
            ("Fischer Bad Heizung Solar", "sr-fischer", 4.4), ("Zimmerei Koller", "sr-koller-b", 4.0), ("Kirchner Thaining", "sr-kirchner", 2.6),
            ("CS Metalldesign", "sr-cs-a", 4.5), ("Zimmerei Koller", "sr-koller-c", 3.9), ("Baureize", "sr-baureize", 4.8)]
SHOWREEL_V = {"sr-cs-b": 3, "sr-koller-a": 2, "sr-fischer": 3, "sr-koller-b": 2, "sr-kirchner": 3, "sr-cs-a": 2, "sr-koller-c": 2, "sr-baureize": 3}
assert all(SHOWREEL[i][0] != SHOWREEL[i - 1][0] for i in range(len(SHOWREEL))), "zwei Lagen vom selben Betrieb hintereinander"


def _sr_v(html, f):
    v = SHOWREEL_V.get(f)
    return html.replace(f'{VID}/{f}.mp4"', f'{VID}/{f}.mp4?v={v}"').replace(f'{VID}/poster/{f}.jpg"', f'{VID}/poster/{f}.jpg?v={v}"') if v else html


def hero_foto_video():
    lagen = "".join(_sr_v(_lage(n, f, i == 0).replace('" data-url=""', f'" data-url="" data-dauer="{round(d * 1000)}"', 1), f)
                    for i, (n, f, d) in enumerate(SHOWREEL))
    leiste = "".join(_sr_v(f'<button type="button" class="{"an" if i == 0 else ""}" aria-pressed="{"true" if i == 0 else "false"}" aria-label="Film {n} zeigen">'
                     f'<img src="{VID}/poster/{f}.jpg" alt="" loading="lazy" decoding="async"></button>', f) for i, (n, f, _) in enumerate(SHOWREEL))
    return (f'<div class="hk-film" aria-hidden="true">{lagen}</div>'
            '<div class="hk-sucher" aria-hidden="true"><span class="ec"></span><span class="ec"></span><span class="ec"></span><span class="ec"></span>'
            f'<span class="rec"><i></i>REC <b>00:00:00:00</b></span><span class="info">01 / {len(SHOWREEL):02d}</span><span class="mitte"></span></div>'
            f'<div class="hk-reel-leiste" style="--n:{len(SHOWREEL)}">{leiste}</div>' + _chip(SHOWREEL[0][0], "gedreht von uns"))


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


def hero_unter(seite):
    """Ein eigener Film je Unterseite über die volle Breite (Noah, 21.11.2026), geschnitten von hero_unterseiten_schneiden.py."""
    d = f"{VID}/hero-unter"
    # Versionsnummer aus der Dateizeit: nach neuem Schnitt/Grading zeigt kein Browser den alten Film (21.11.2026)
    v = lambda n: f"{d}/{n}?v={int((WURZEL / 'static/assets/vid/hero-unter' / n).stat().st_mtime)}"
    return (f'<div class="hk-film" aria-hidden="true"><div class="hk-lage an hk-einzel">'
            f'<video class="hk-desk" muted loop playsinline preload="none" data-hand data-src="{v(seite + "-d.mp4")}" poster="{v(seite + ".jpg")}"></video>'
            f'<video class="hk-mobil" muted loop playsinline preload="none" data-hand data-src="{v(seite + "-m.mp4")}" poster="{v(seite + "-m.jpg")}"></video>'
            '</div></div>', None)


# Galerie Foto & Video: 69 Fotos (medien_bauen.py, alle von Hand angesehen) + 11 Filme, als Mauerwerk ohne Filter
# (Noah, 18.11.2026: „Da muss man es sich nicht unbedingt noch extra eingeordnet lassen“). Nie zwei Karten vom selben
# Betrieb nebeneinander (assert in galerie_sek).
GALERIE = _json.loads((WURZEL / "static/assets/fv/galerie.json").read_text())
# Nur, was unser Foto-/Videograf gedreht hat (Noah, 20.11.2026: „ausschließlich Content, den wir gemacht haben … Stockfoto … muss raus
# … Martin Wörner … das Bild hat er mir geschickt“): die vier Bilder aus static/assets/img/praxis sind Kunden- bzw. Stockbilder
NICHT_GEDREHT = {"dach", "pv", "galabau", "maler"}
GALERIE["fotos"] = [d for d in GALERIE["fotos"] if d["k"] not in NICHT_GEDREHT]
assert not any(d["k"] in NICHT_GEDREHT for d in GALERIE["fotos"])
# (Stelle in der Fotoliste, Gewerk-Schlüssel, Gewerk, Betrieb, Seitenverhältnis, Film, Poster)
GALERIE_FILME = [(3, "holz", "Schreinerei", "Schreinerei Kreitner", 16 / 9, f"{VID}/kreitner.mp4", f"{VID}/poster/kreitner.jpg"),
                 # Bettina selbst nicht auf Foto & Video (Noah, 19.11.2026: „Ich will Bettina nicht in der Foto- und Videoseite haben … Fischer schon“)
                 (10, "bau", "Bau &amp; Transporte", "Kirchner Thaining, 50 Jahre", 9 / 16, f"{VID}/kirchner.mp4", f"{VID}/poster/kirchner.jpg"),
                 (17, "holz", "Zimmerei", "Zimmerei Koller", 16 / 9, f"{VID}/koller-galerie.mp4", f"{VID}/poster/koller.jpg"),
                 (24, "", "Drohnenflug", "Baureize", 16 / 9, f"{VID}/baureize.mp4", f"{VID}/poster/baureize.jpg"),
                 (31, "metall", "Metallbau", "CS Metalldesign", 16 / 9, f"{VID}/cs-metall.mp4", f"{VID}/poster/cs-metall.jpg"),
                 # Fischer-Team am Transporter, aus dem neu gedrehten Imagefilm 2026 (Crafter-Intro) — Noah, 19.11.2026: „Video-Sequenz … was wir bei Fischer gemacht haben“
                 (38, "shk", "Imagefilm", "Fischer Bad Heizung Solar", 16 / 9, f"{FV}/v/fi-team.mp4", f"{FV}/v/fi-team.jpg"),
                 (45, "bau", "Bau", "A. Resch Bau", 16 / 9, f"{FV}/v/g-resch.mp4", f"{FV}/v/g-resch.jpg"),
                 (52, "shk", "Drohnenflug", "Fischer Bad Heizung Solar", 16 / 9, f"{FV}/v/fi-drohne-g.mp4", f"{FV}/v/fi-drohne.jpg"),
                 (59, "bau", "Drohnenflug", "Wohner Elektrotechnik", 16 / 9, f"{FV}/v/g-wohner.mp4", f"{FV}/v/g-wohner.jpg")]


def galerie_sek():
    def foto(d):
        g, b = _html.escape(d["gewerk"]), _html.escape(d["betrieb"], quote=False) if d["betrieb"] else ""
        b = b.replace("&amp;amp;", "&amp;")
        alt = f'{g} bei {b}' if b else g
        return (f'<figure class="fv-k" data-g="{d["g"]}" data-b="{_html.escape(_html.unescape(d["betrieb"] or ""))}" style="--r:{d["w"] / d["h"]:.4f}"><button type="button" class="fv-auf" aria-label="{alt} groß ansehen">'
                f'<img src="{FV}/g/{d["k"]}-900.webp" srcset="{FV}/g/{d["k"]}-480.webp 480w, {FV}/g/{d["k"]}-900.webp 900w" sizes="(min-width:1100px) 22vw, (min-width:700px) 31vw, 48vw" data-gross="{FV}/g/{d["k"]}-1800.webp" alt="{alt}" loading="lazy" decoding="async" width="900" height="{round(900 * d["h"] / d["w"])}"></button>'
                f'<figcaption><b>{g}</b><span>{b or "Drehtag bei einem Kunden"}</span></figcaption></figure>')

    def film(g, gewerk, betrieb, r, mp4, poster):
        return (f'<figure class="fv-k ist-film" data-g="{(g + " film").strip()}" data-b="{_html.escape(_html.unescape(betrieb).split(",")[0])}" style="--r:{r:.4f}"><button type="button" class="fv-auf" aria-label="Film {betrieb} groß ansehen">'
                f'<video muted loop playsinline preload="none" data-hand data-src="{mp4}" poster="{poster}"></video><span class="fv-spiel">Film</span></button>'
                f'<figcaption><b>{gewerk}</b><span>{betrieb}</span></figcaption></figure>')
    karten = [foto(d) for d in GALERIE["fotos"]]
    betriebe = [_html.unescape(d["betrieb"]) for d in GALERIE["fotos"]]
    for stelle, *rest in reversed(GALERIE_FILME):
        karten.insert(stelle, film(*rest))
        betriebe.insert(stelle, _html.unescape(rest[2]).split(",")[0])
    # Nach dem Herausnehmen fremder Bilder (20.11.2026) kann ein Betrieb doppelt nebeneinander stehen: mit der nächsten passenden Karte tauschen
    for i in range(1, len(betriebe)):
        if betriebe[i] and betriebe[i] == betriebe[i - 1]:
            j = next((x for x in range(len(betriebe)) if x not in (i - 1, i) and betriebe[x] != betriebe[i]
                      and (x == 0 or betriebe[x - 1] != betriebe[i]) and (x + 1 >= len(betriebe) or betriebe[x + 1] != betriebe[i])
                      and betriebe[i - 1] != betriebe[x] and (i + 1 >= len(betriebe) or betriebe[i + 1] != betriebe[x])), None)
            if j is not None:
                betriebe[i], betriebe[j] = betriebe[j], betriebe[i]; karten[i], karten[j] = karten[j], karten[i]
    nachbarn = [(i, betriebe[i]) for i in range(1, len(betriebe)) if betriebe[i] and betriebe[i] == betriebe[i - 1]]
    assert not nachbarn, f"zwei Karten vom selben Betrieb nebeneinander: {nachbarn}"
    alle = "".join(karten)
    fotos, filme = len(GALERIE["fotos"]), len(GALERIE_FILME)
    pfeil = lambda d: f'<svg viewBox="0 0 24 24"><path d="{d}"/></svg>'
    return ('<section class="sek fv-galerie" id="ergebnisse"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Die Ergebnisse</span>'
            f'<h2>Abgedreht.</h2><p class="fv-klappe" aria-hidden="true"><i></i>REC <b>00:00:00:00</b></p></div>'
            # Noah, 18.11.2026: Zahl-Zeile rechts raus („ist scheiße“), dafür eine Klappe im Stil des Showreel-Suchers
            '<style>.fv-galerie .kopfzeile{display:grid!important;grid-template-columns:minmax(0,1fr) auto;align-items:end;column-gap:24px;row-gap:14px;max-width:none}'
            '.fv-galerie .kopfzeile>.kicker{grid-column:1/-1}'
            '.fv-galerie h2{font-size:clamp(56px,9vw,148px);line-height:.88;letter-spacing:-.045em;margin:0}.fv-galerie h2::before{display:none}'
            '.fv-klappe{display:flex;align-items:center;gap:14px;margin:0 0 .5em;font:700 clamp(20px,2.4vw,36px)/1 var(--schrift);letter-spacing:.06em;font-variant-numeric:tabular-nums;color:var(--tinte)}'
            '.fv-klappe i{width:.5em;height:.5em;border-radius:50%;background:#E5483A;box-shadow:0 0 14px rgba(229,72,58,.6);animation:hk-rec 1.2s steps(1) infinite}'
            '.fv-klappe b{font-weight:700;color:var(--bronze-tief)}'
            '@media (max-width:700px){.fv-galerie .kopfzeile{grid-template-columns:1fr}.fv-klappe{margin:0}}'
            '@media (prefers-reduced-motion:reduce){.fv-klappe i{animation:none}}</style>'
            '<script>(()=>{const b=document.querySelector(".fv-klappe b");if(!b||matchMedia("(prefers-reduced-motion: reduce)").matches)return;const t0=performance.now();'
            'const z=n=>String(n).padStart(2,"0");const lauf=t=>{const f=Math.floor((t-t0)/40),s=Math.floor(f/25);b.textContent=z(Math.floor(s/3600))+":"+z(Math.floor(s/60)%60)+":"+z(s%60)+":"+z(f%25);requestAnimationFrame(lauf)};requestAnimationFrame(lauf)})()</script>'
            f'<div class="fv-raster">{alle}</div></div></section>'
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
          '<p class="lead">Wir bauen deine Website und bringen dir<br class="dsk-br"> qualifizierte Kunden und Mitarbeiter aus deinem Umkreis.</p>')  # Noah, 20.11.2026: „qualifizierte Kunden und Mitarbeiter aus deinem Umkreis.“ in die nächste Zeile (ersetzt 18.11.)
# Aufbau wie shk…/start-neu/: Firma → drei Leistungen (einfache Karten) → Ergebnisse → Stimmen → Team → Kontakt.
# Die drei Säulen in Logo-Form stehen schon im Hero und kommen hier nicht noch einmal (Noah, 14.11.2026);
# Problem-Szenen, Google-Mechanik und Foto-Band stehen auf den Unterseiten.
# Rechte Hero-Säule (Noah, 18.11.2026): „wo jetzt Anfragen und Bewerbungen steht, sollten … die Interviews, also wie auf der
# SHK-Seite … dieses Ding, wo die ganzen Kunden drin sind, wo das dann immer switcht“ → der Kunden-Zusammenschnitt der
# SHK-Seite (firma/website-shk/assets/reels/kunden-szenen.mp4, jeder Betrieb einmal, Match Cut) statt des Drohnen-Clips.
# Noah 18.11. abends: „nur der Ausschnitt von Patrick“ wird getauscht (alle anderen Stellen bleiben) → Szene 1 jetzt Sussmann Hooks (34)
# ab 0,9 s (Patrick redet im Lager, Kopf ganz im Bild, gleiche Match-Cut-Lage 50 %/21,5 %), Szenen 2–8 Bild für Bild aus
# firma/website-shk/neu/video/szenen/*.mp4 (SHK-Seite selbst unverändert).
s.h = s.h.replace('/static/assets/vid/saeule/baureize.jpg', '/static/assets/vid/saeule/kunden-shk.jpg?v=4')
s.ersetze('data-src="/static/assets/vid/saeule/baureize-d.mp4" data-src-mobil="/static/assets/vid/saeule/baureize-m.mp4"',
          'data-src="/static/assets/vid/saeule/kunden-shk-d.mp4?v=10" data-src-mobil="/static/assets/vid/saeule/kunden-shk-m.mp4?v=10"')  # v10 (22.11.2026): + Mitarbeiterin von Stimpfle (Hooks (3) ab 3,33 s, spricht in die Kamera; Noah: „da sollte sie halt schon grade sprechen“) als letzte Szene, Noah: „nicht yannick, sondern das mädl bei yannick“  # v4 (19.11.2026): Bettina stehend und lächelnd (Kampagnen-Aufnahme Bodys (2) ab 2,4 s) statt im Lager an der Kiste, an Stelle 4 zwischen Benjamin Senftleben und Yannick Stimpfle (Noah: „nicht direkt nach Erwin Schmidt“)
assert 'baureize' not in s.h.split('<div class="saeulen">', 1)[1].split('</div></div></div>', 1)[0]
# Noah, 18.11.2026: „das Video soll schon das ganz ausfüllen, aber … nicht, dass der Kopf … abgeschnitten ist“ → in den
# Originalen sitzt der Kopf ganz oben → weiter gefilmte Takes (start-neu/kunden_szenen_saeule.py), Beschriftung wieder oben.
s.h = s.h.replace('</head>', '<style>/* Noah 18.11.: Logo wie bei den Website-Konzepten „100 Mal dahinter“, nicht in Sektionen gedacht → ein Muster über die ganze helle Seite */main{background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%22168%22%20height%3D%22168%22%20viewBox%3D%220%200%20168%20168%22%3E%3Cg%20fill%3D%22%23C8873A%22%20fill-opacity%3D%22.12%22%20transform%3D%22translate%2824%2026%29%20scale%28.3%29%22%3E%3Cpath%20d%3D%22M0%2C39.667%20L22%2C25%20L22%2C91%20L0%2C91%20Z%22/%3E%3Cpath%20d%3D%22M34%2C14.667%20L56%2C0%20L56%2C91%20L34%2C91%20L34%2C64.67%20L27%2C68%20L27%2C53.667%20L34%2C49%20Z%22/%3E%3Cpath%20d%3D%22M61%2C14.667%20L83%2C0%20L83%2C91%20L61%2C91%20Z%22/%3E%3C/g%3E%3Cg%20fill%3D%22%23C8873A%22%20fill-opacity%3D%22.085%22%20transform%3D%22translate%28108%20110%29%20scale%28.22%29%22%3E%3Cpath%20d%3D%22M0%2C39.667%20L22%2C25%20L22%2C91%20L0%2C91%20Z%22/%3E%3Cpath%20d%3D%22M34%2C14.667%20L56%2C0%20L56%2C91%20L34%2C91%20L34%2C64.67%20L27%2C68%20L27%2C53.667%20L34%2C49%20Z%22/%3E%3Cpath%20d%3D%22M61%2C14.667%20L83%2C0%20L83%2C91%20L61%2C91%20Z%22/%3E%3C/g%3E%3C/svg%3E");background-size:168px 168px;background-repeat:repeat}/* große Signets laufen unten weich aus statt an der Sektionskante abzubrechen */.sg-wachsen{top:auto!important;bottom:0;height:min(96%,1000px)!important}.sg-ruhe{top:auto!important;bottom:0;height:min(92%,880px)!important;transform:translateX(-50%)!important}.sg-wachsen{opacity:1!important}.sg-wachsen .sg-k{fill:var(--tinte)!important;fill-opacity:.07}.sg-wachsen .sg-l{stroke:var(--tinte)!important;opacity:.22!important}.sg-ruhe .sg-fuell{fill:var(--tinte)!important;opacity:.06!important}.sg-ruhe .sg-umriss{stroke:var(--tinte)!important;opacity:.35!important}@media (max-width:760px){.sg-wachsen{height:auto!important;width:min(70vw,320px)}.sg-ruhe{height:auto!important;width:min(84vw,360px)}}/* Lead neben der Überschrift auf derselben Grundlinie */.sek .kopfzeile:has(>h2+.lead)>h2,.sek .kopfzeile:has(>h2+.lead)>.lead{align-self:last baseline!important;margin-bottom:0!important}@media (min-width:901px){.sek .kopfzeile:has(>h2+.lead)>.lead{justify-self:end;text-align:right}}</style>' + '</head>', 1)
s.h = s.h.replace('</head>', '<style>.saeule:nth-child(3) video{object-position:50% 0;transform:none}</style></head>', 1)
# Noah 18.11.: „Wir hatten doch beim SHK-Video die perfekten Stellen“ → das SHK-Video (kunden-shk-*.mp4 = firma/website-shk/assets/reels/kunden-szenen.mp4, seit 18.11. abends nur Patricks Szene getauscht),
# oben verankert (Kopf nie angeschnitten). Die Köpfe sitzen dort weit oben; eine Beschriftung oben läge auf der Stirn → in dieser Säule ohne Beschriftung.
# Linke + mittlere Hero-Säule (Noah, 18.11.2026): „links machen wir das mit den Drohnen, dass die Drohnen geschnitten werden
# … eine von Kreitner, eine kurze Stelle, wo man Leute sieht“ / Mitte „die vor Ort gedrehten Sachen … Detailaufnahmen von
# Resch, Koller, Kirchner, Baureize“. Beide aus Kundenmaterial geschnitten (Drive-Rohmaterial, 600×800 Desktop, Handy 360×480
# bzw. 360×640, stumm), Quelle/Sekunde je Clip:
#   drohnen-*  (harte Schnitte, 8 Szenen je ~1,3 s = 10,8 s; Stand 21.11.2026, Skript start-neu/saeule_links_schneiden.py;
#              Noah: „bei der linken säule … szenen … neuer Entenmann Shooting … Zimmerei Koller … mäßig action, wo mans sieht“;
#              nie zwei Szenen vom selben Betrieb nacheinander, auch nicht über die Schleife):
#              Kreitner Werkstattflug (Drohne 0,8 s) · Entenmann Trennschleifer mit Funken (Headervideo 4K 9,55 s) ·
#              Koller Zimmerer mit Akkuschrauber (Final 1,96 s) · Wohner Drohne über das PV-Dach (Drohnenvideo 10, 0,3 s) ·
#              Entenmann Wärmepumpe durch den Garten (4,34 s) · Koller Kappsäge mit Gehörschutz (Final 13,9 s) ·
#              CS Metalldesign Hallenflug (Drohne 1,0 s) · Entenmann Akkuschrauber am Rohr (25,12 s)
#   details-*  (0,4 s Überblendung; Stand 19.11.: Kirchner und Brandstempel raus, Noah: „das Video mit Reize … wo er die Treppe
#              hochgeht“ = die Einstellung aus dem fertigen Baureize-Film): Koller Bohrer in Spänen (Final 9,1 s) ·
#              Resch Bewehrung binden (Resch Bau 8,0 s) · Wolfgang Reize geht die Treppe hoch (Drive „Baureize original.mp4“
#              4,60–6,44 s, echte Geschwindigkeit, Ausschnitt folgt dem Logo) · CS Schweißen (CS Metalldesign 2,05 s) ·
#              Koller Werkzeugbank (Final 21,7 s)
# Links und Mitte getauscht (Noah, 21.11.2026: „linke und mittlere säule bei start hero tauschen, also der content der linken säule
# in die mitte, und andersrum“): links jetzt die Detailaufnahmen (details-*), in der Mitte die Szenen mit CS/Entenmann/Koller (drohnen-*)
s.h = s.h.replace('/static/assets/vid/saeule/kreitner.jpg', '/static/assets/vid/saeule/details.jpg?v=3')
s.ersetze('data-src="/static/assets/vid/saeule/kreitner-d.mp4" data-src-mobil="/static/assets/vid/saeule/kreitner-m.mp4"',
          'data-src="/static/assets/vid/saeule/details-d.mp4?v=3" data-src-mobil="/static/assets/vid/saeule/details-m.mp4?v=3"')
s.h = s.h.replace('/static/assets/vid/saeule/hero-loop.jpg', '/static/assets/vid/saeule/drohnen.jpg?v=7')
s.ersetze('data-src="/static/assets/vid/saeule/hero-loop-d.mp4" data-src-mobil="/static/assets/vid/saeule/hero-loop-m.mp4"',
          'data-src="/static/assets/vid/saeule/drohnen-d.mp4?v=7" data-src-mobil="/static/assets/vid/saeule/drohnen-m.mp4?v=7"')
s.heraus('<section class="sek system-sek" id="system"')
s.heraus('<section class="sek grund lagen-sek probleme pb-sek">')
s.heraus('<section class="sek google grund">')
s.heraus('<section class="sek band auf-dunkel" id="videos">')
PFEIL = '<svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'


def karte(bild, alt, pos, titel, zeile, text, ziel, knopf):
    return (f'<article class="erg reveal"><div class="erg-film"><img src="/start-neu/bilder/{bild}.webp" alt="{alt}" loading="lazy" decoding="async" style="object-position:{pos}"></div>'
            f'<div class="erg-in"><div class="erg-zeile"><em>{titel}</em><span>{zeile}</span></div><p>{text}</p>'
            f'<a class="textlink" href="/{ziel}/">{knopf} {PFEIL}</a></div></article>')


# Große Bühnen-Signets raus (Noah, 19.11.2026: „als wären die Sachen abgeschnitten, mit dem Haar, was daraus überall rausfährt“):
# die Balken standen als graue Kästen unter den Karten, ihre Umrisslinien liefen durch die Team-Überschrift. Das Logo-Muster bleibt.
LEISTUNGS_SEK = ('<section class="sek leistungen-sek" id="system">' + '<div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Unsere Leistungen</span>'
                 '<h2>Drei Baustellen<br class="dsk-br"> übernehmen wir für dich.</h2></div><div class="ergebnisse">'
                 # Fette Zeile = abgenommene H1 der Unterseite, Text je ein kurzer Satz (Noah, 15.11.2026)
                 + karte("zimmerei-schneider", "Zwei Zimmerer von Zimmerei Schneider in der Werkstatt", "50% 30%", "Website", "Wir bauen. Du ziehst ein.",
                         "Eine Seite je Leistung, mit deinem Ort drin.", "websites", "Mehr zur Website")
                 + karte("senftleben-team-wagen", "Das Team von Senftleben Haustechnik vor den Firmenwagen", "50% 30%", "Neue Kunden", "Du fährst hin. Den Rest machen wir.",
                         "Anfragen aus deinem Umkreis, direkt an dich.", "neukundengewinnung", "Mehr zu neuen Kunden")
                 + karte("erwin-schmidt-team", "Das Team von Erwin Schmidt &amp; Sohn", "50% 30%", "Neue Mitarbeiter", "Wir suchen. Du stellst ein.",
                         "Bewerbungen von Fachkräften aus deinem Umkreis.", "mitarbeitergewinnung", "Mehr zu neuen Mitarbeitern")
                 + f'</div><p class="leistungen-zusatz reveal">Die Fotos und Videos dafür drehen wir bei dir im Betrieb. <a class="textlink" href="/foto-video/">Foto &amp; Video {PFEIL}</a></p></div></section>'
                 '<style>/* Entwurf (start-neu/bauen.py) */.leistungen-zusatz{margin-top:28px;font-size:17px;line-height:1.5;color:var(--tinte-2);text-align:center}'
                 '.leistungen-sek .erg-zeile em{font-size:clamp(24px,2.2vw,30px)}'
                 # Kartentext in allen drei Karten gleich viele Zeilen (der dritte Satz ist breiter als die Karte, also alle drei balanciert zweizeilig)
                 '.leistungen-sek .erg-in p{max-width:24ch;text-wrap:balance}'
                 # Sektionsköpfe der Startseite in EINER Machart (Noah, 15.11.2026): Ohne Lead lief die H2 über die volle
                 # Breite („Wir lassen unsere Kunden sprechen.“ einzeilig, .stimmen h2 max-width:none), mit Lead nur 16ch.
                 # Jetzt jede linksbündige H2 höchstens 16ch, text-wrap:balance verhindert ein Einzelwort in der letzten Zeile.
                 '.sek .kopfzeile:not(.mitte)>h2{max-width:16ch}'
                 '.uk-bild .collage img{background:var(--papier-2,#efe9df)}.uk-bild .collage img.raus{opacity:.35;transform:none}</style>')
s.vor('<section class="sek laufband" id="gefunden">', LEISTUNGS_SEK)
# Bezugsfertig: die neuesten Seiten vorne in die Leiste (Noah, 19.11.2026: Schillinger, Wagenknecht, „die ich jetzt fertig gemacht habe“, Irlbacher)
def _lb_karte(name, art, url, k):
    return (f'<a class="lb-k" href="{url}" rel="noopener" title="{name} — Website live ansehen"><div class="lb-schirm">'
            f'<video class="hero-lauf" muted loop playsinline preload="none" data-src="/static/assets/vid/hero/h{k}.webm" data-poster="/static/assets/vid/hero/h{k}.jpg" width="640" height="400" aria-label="{name} — Startseite, wie sie live läuft"></video>'
            f'<img class="seite-bild" data-src="/static/assets/vid/hero/s{k}.webp" alt="" aria-hidden="true" loading="eager" decoding="async"></div>'
            f'<div class="lb-fuss"><b>{name}</b><small>{art}</small></div></a>')
# Irlbacher vorne (Noah, 19.11.2026: „irlbacher ruhig bisschen präsent“)
LB_NEU_1 = "".join(_lb_karte(*k) for k in [("Irlbacher Gebäudetechnik", "SHK · Heizung &amp; Sanitär", "https://www.hs-irlbacher.de", "irlbacher"),
                                           ("Juwelier Wagenknecht", "Uhren &amp; Schmuck", "https://juwelier-wagenknecht.de", "wagenknecht"),
                                           ("Björn Schillinger", "Schreinerei · Möbelbau", "https://meisterschillinger.de", "schillinger")])
LB_NEU_2 = "".join(_lb_karte(*k) for k in [("Malermeister Müller", "Malerbetrieb", "https://mueller-maler-meister.de", "mueller"),
                                           ("W&amp;W Bau", "Bauunternehmen", "https://w-w-bau.com", "ww"),
                                           ("Mehr Lebensenergie", "Qigong &amp; TCM", "https://mehrlebensenergie-praxis.de", "illenseer")])
_a = s.h.index('<section class="sek laufband" id="gefunden">'); _e = s.h.index('</section>', _a)
_lb = s.h[_a:_e]
_teile = _lb.split('<div class="lb-zug">')
assert len(_teile) == 3, len(_teile)
def _vorne(zug, neu):
    # der Zug enthält die Karten zweimal (nahtlose Schleife): neue Karten vor beide Hälften
    # Kartenanfang als <a> (alte Vorlage) oder <div> (seit 19.11.2026 ohne Link, kunden_links.py) — nie nur eine Form suchen
    starts = [m.start() for m in re.finditer(r'<(?:a|div) class="lb-k"', zug)]
    assert len(starts) >= 2 and len(starts) % 2 == 0, len(starts)
    mitte = starts[len(starts) // 2]
    return neu + zug[:mitte] + neu + zug[mitte:]
_teile[1] = _vorne(_teile[1], LB_NEU_1); _teile[2] = _vorne(_teile[2], LB_NEU_2)
# Reihenfolge wie im Websites-Raster (Noah, 19.11.2026 abends: Wagenknecht „nicht ganz oben“, SD Hirsch, Schillinger, Koller,
# Dinkel, W&W Bau weiter nach vorn). Obere Leiste = erste Hälfte des Rasters, untere = zweite.
LB_FOLGE = [["Entenmann Haustechnik", "Irlbacher Gebäudetechnik", "SD Hirsch", "Björn Schillinger", "Zimmerei Koller", "Dinkel Metallbau", "W&amp;W Bau",
             "Zimmerei Knappich", "Küchenhaus Hirschvogel", "Baustoffe Kirchner", "Wohner Elektrotechnik", "Baureize", "Resch Bau"],
            ["Planung Hindelang", "Dachbau Kraus", "Schwaighofer", "Erwin Schmidt &amp; Sohn", "Vogel Holzbau", "Maser Tankschutz",
             "Schreinerei Kreitner", "Schuster Erisried", "Juwelier Wagenknecht", "Weber Metallbau", "Malermeister Müller"]]
# Senftleben raus (Noah, 21.11.2026: „bei websites brauchen wir die seite von senftleben eigentlich nicht mit reinnehmen“)
# Kategorie je Betrieb gegen die eigene Live-Seite geprüft (Noah, 21.11.2026: „sind nicht passend einkategorisiert“) —
# gilt für das Laufband hier und das Websites-Raster (RASTER weiter unten), damit beide gleich bleiben.
# Kurz, damit die Branche in JEDER Kachelbreite in eine Zeile passt (Noah, 21.11.2026: „branche kleine schrift, eine zeile“)
KATEGORIE = {
    "Entenmann Haustechnik": "SHK · Wärmepumpe", "Irlbacher Gebäudetechnik": "SHK · Lüftung",
    "SD Hirsch": "Rohrformteile", "Björn Schillinger": "Schreinerei · Möbel",
    "Zimmerei Koller": "Zimmerei · Holzhaus", "Dinkel Metallbau": "Metallbau · Treppen",
    "W&amp;W Bau": "Bau · Altbau", "Zimmerei Knappich": "Zimmerei · Dach",
    "Küchenhaus Hirschvogel": "Küchenstudio", "Baustoffe Kirchner": "Tiefbau · Baustoffe",
    "Wohner Elektrotechnik": "Elektro · Solar", "Baureize": "Maurer · Estrich",
    "Resch Bau": "Baugeschäft", "Planung Hindelang": "Planung · Holzbau",
    "Dachbau Kraus": "Dach · Fassade", "Schwaighofer": "Betonbau",
    "Erwin Schmidt &amp; Sohn": "SHK · Heizung &amp; Bad", "Vogel Holzbau": "Zimmerei · Hallen",
    "Maser Tankschutz": "Tankschutz", "Schreinerei Kreitner": "Schreinerei",
    "Schuster Erisried": "Landtechnik", "Juwelier Wagenknecht": "Uhren &amp; Schmuck",
    "Weber Metallbau": "Laserschneiden", "Malermeister Müller": "Maler · Fassade",
}


def _lb_karten(zug):
    starts = [m.start() for m in re.finditer(r'<(?:a|div) class="lb-k"', zug)]
    karten = {}
    for st in starts:
        fuss = zug.index('</small></div>', st) + len('</small></div>')
        ende = fuss + len(re.match(r'</(?:a|div)>', zug[fuss:]).group(0))
        karten.setdefault(re.search(r'<b>(.*?)</b>', zug[st:ende]).group(1), zug[st:ende])
    return karten, (starts[0], ende)


_alle = {}
_spannen = []
for _i in (1, 2):
    _k, _sp = _lb_karten(_teile[_i]); _alle.update(_k); _spannen.append(_sp)
_alle.pop("Mehr Lebensenergie")  # Inna Illenseer raus (Noah, 20.11.2026)
_alle.pop("Senftleben Haustechnik")
# Entenmann Haustechnik vorn (Noah, 20.11.2026: „als Referenz … kann auf jeden Fall gut präsent sein, auch bei den Projekten“)
_alle["Entenmann Haustechnik"] = _lb_karte("Entenmann Haustechnik", "SHK · Heizung &amp; Wärmepumpe", "https://entenmann-haustechnik.de", "entenmann")
_alle["Weber Metallbau"] = _lb_karte("Weber Metallbau", "Metallbau · Laser &amp; Blech", "https://weber-metalltechnik.com", "weber")
assert sorted(_alle) == sorted(LB_FOLGE[0] + LB_FOLGE[1]), set(_alle) ^ set(LB_FOLGE[0] + LB_FOLGE[1])
assert sorted(_alle) == sorted(KATEGORIE), set(_alle) ^ set(KATEGORIE)
for _n in _alle:
    assert _alle[_n].count("<small>") == 1, _n
    _alle[_n] = re.sub(r"<small>.*?</small>", f"<small>{KATEGORIE[_n]}</small>", _alle[_n])
for _i, (_st, _en) in zip((1, 2), _spannen):
    _zug = "".join(_alle[n] for n in LB_FOLGE[_i - 1])
    _teile[_i] = _teile[_i][:_st] + _zug + _zug + _teile[_i][_en:]
s.h = s.h[:_a] + '<div class="lb-zug">'.join(_teile) + s.h[_e:]
# Laufband „Bezugsfertig.“ läuft erst, wenn es ins Bild kommt, und die obere Bahn steht so, dass Entenmann und Irlbacher
# gerade rechts reinfahren (Noah, 21.11.2026: „so sind sie direkt weg“ — die CSS-Animation lief ab Seitenaufruf, beim
# Hinscrollen waren die ersten Karten schon links raus). Ohne JS läuft das Band wie bisher.
_e = s.h.index('</section>', s.h.index('<section class="sek laufband" id="gefunden">'))
s.h = s.h[:_e] + ('<script>(()=>{const sek=document.getElementById("gefunden");if(!sek||matchMedia("(prefers-reduced-motion: reduce)").matches)return;'
    'const zuege=[...sek.querySelectorAll(".lb-zug")];zuege.forEach(z=>z.style.animationPlayState="paused");'
    'const stellen=()=>{const z=sek.querySelector(".lb-bahn:not(.rueck) .lb-zug");if(!z)return;const halb=z.scrollWidth/2,breit=z.parentElement.clientWidth,'
    'dauer=parseFloat(getComputedStyle(z).animationDuration)||64,weg=Math.max(0,halb-breit+60);z.style.animationDelay=(-dauer*weg/halb)+"s"};stellen();'
    'let an=false;addEventListener("resize",()=>{if(!an)stellen()});'
    'new IntersectionObserver((es,o)=>{if(es.some(e=>e.isIntersecting)){an=true;zuege.forEach(z=>z.style.animationPlayState="running");o.disconnect()}},'
    '{rootMargin:"0px 0px -25% 0px"}).observe(sek.querySelector(".lb")||sek)})()</script>') + s.h[_e:]
# „Wie wir Seiten bauen“ fällt weg (Noah, 19.11.2026 abends: „brauchen nicht erklären – es geht drum was der Kunde hat“);
# der Knopf „Alle Arbeiten ansehen“ führt zu den fertigen Seiten.
s.ersetze('<a class="btn btn-rand" href="/websites/">Wie wir Seiten bauen</a>', '')

s.ersetze('<span class="kicker">Deine Website</span>', '<span class="kicker">Unsere Websites</span>')
# Kicker ohne Mittelpunkt, der wirkt maschinell (Noah, 15.11.2026)
s.ersetze('<span class="kicker">Kostenloses Beratungsgespräch · 30 Min.</span>', '<span class="kicker">Kostenloses Beratungsgespräch</span>')
# „Wer dahinter steht“: klare Überschrift, „Seit 2019 nur Handwerk“ als Kicker, Noahs Vorstellung als Text (Noah, 15.11.2026)
# Noah, 15.11.2026: die fünf Zeilen über die Familie waren zu lang, genau diese zwei Sätze (auch auf /ueber-uns/)
NOAH_TEXT = 'Servus, ich bin Noah, Inhaber der Handwerksmanufaktur. Dass wir nur fürs Handwerk arbeiten, kommt nicht von ungefähr.</p><p class="lead" style="margin-top:20px">Meine drei Brüder haben alle im Handwerk gelernt. Zwei davon sind Meister. Zusätzlich haben wir in der Familie mehrere Handwerksbetriebe. Dadurch habe ich schon von klein auf täglich mitgekriegt, wie es im Handwerk wirklich zugeht.</p><p class="lead" style="margin-top:20px">In den letzten 8 Jahren haben wir über 150 Firmen betreut und wissen mittlerweile ganz genau, was ein Handwerksbetrieb online braucht, damit Kunden und Bewerber bei ihm landen.'
s.ersetze('<span class="kicker">Wer dahinter steht</span><h2>Die Leute hinter deinem Auftritt.</h2><p class="lead">Dieselben Leute von Anfang bis Ende.</p>',
          f'<span class="kicker">Du bist auf der Baustelle daheim. Wir im Internet.</span><h2 style="max-width:none;font-size:clamp(23px,3.75vw,54px)">Wer hinter der<br><span style="white-space:nowrap">Handwerksmanufaktur steht.</span></h2>')
# Noah, 18.11.2026: „bei der Home-Seite … den ‚Über uns‘-Text rausnehmen … dass da einfach nur das Team mit dabei steht.
# Dann ist halt noch der Button ‚Mehr über uns‘“ — der Text steht nur noch auf /ueber-uns/.


# Je Karte zwei Zeilen (Noah, 20.11.2026: „wir wollen überall 2 Zeilen“); Sussmann mit dem ersten Auftrag über 10.000 €,
# Senftleben ohne „sechs Angebote“, dafür die Umkreis-Zeile
ERG_TEXTE = [
    ('Alles in zwei Monaten, der erste Auftrag kam nach 18 Tagen. Inzwischen warten Kunden fast drei Wochen auf einen Termin.',
     'Erster Auftrag über 10.000 € nach 18 Tagen. Kunden warten fast drei Wochen auf Termine.'),
    ('Sechs Angebote sind schon raus. Dieses Jahr ist voll, die nächsten Bäder plant Senftleben schon fürs neue Jahr.',
     'Qualifizierte Anfragen aus dem 30-km-Umkreis, dieses Jahr ist schon voll.'),
    ('Gesucht war ein Anlagenmechaniker. Aufkleber auf dem Wagen und die Stelle auf der eigenen Seite hatten vorher kaum etwas gebracht.',
     'Gesucht war ein Anlagenmechaniker. Aufkleber und Stellenseite hatten vorher nichts gebracht.'),
]


def ergebnisse_aktuell(seite):
    """Kundenfotos + Stimpfle-Zahlen wie auf der SHK-Seite abgenommen (Noah, 14.11.2026 nachts): Sussmann Foto 6, Stimpfle Foto 3."""
    h = seite.h
    h = re.sub(r"<img data-k='[^']*' src=\"/static/assets/img/_800/fall/sussmann-team\.webp\" alt=\"\"",
               '<img src="/start-neu/bilder/sussmann-wagen-duo.webp" alt="Patrick und Mirjana von Sussmann vor dem Firmenwagen" style="object-position:50% 30%"', h)
    h = h.replace('<img src="/static/assets/img/_800/fall/stimpfle-team.webp" alt="Drei Monteure von Stimpfle Sanitär und Heizung vor dem Firmenwagen" loading="lazy" decoding="async" style="object-position:50% 22%">',
                  '<img src="/start-neu/bilder/stimpfle-werkstatt.webp" alt="Das Team von Stimpfle Sanitär und Heizung in der Werkstatt" loading="lazy" decoding="async" style="object-position:50% 30%">')
    h = h.replace('<em>3 Bad-Anfragen</em><span>in den ersten 3 Tagen</span>', '<em>7 Bad-Anfragen</em><span>3 Vor-Ort-Termine in den ersten 3 Tagen</span>')
    h = h.replace('Die Werbung läuft seit dem 29. Oktober im Umkreis von Stadtbergen.', 'Die Anzeigen laufen seit dem 29. Oktober im Umkreis von Stadtbergen.')
    # Ob Anzeigen pausieren oder ein Kunde weitermacht, steht nie auf der Seite (Noah, 19.11.2026: „das NIE erwähnen“)
    h = h.replace(', die Werbung pausiert deshalb bis Februar.', '.').replace(', die Anzeigen pausieren deshalb bis Februar.', '.')
    assert not re.search(r'pausier|verlängert', re.sub(r'<script.*?</script>', '', h, flags=re.S)), 'Kundenstatus (pausiert/verlängert) auf der Seite'
    h = h.replace('<p class="lead">Werbung im Umkreis des Betriebs. Gezählt ist', '<p class="lead">Anzeigen im Umkreis des Betriebs. Gezählt ist')
    h = h.replace('<h2>Du kümmerst dich um nichts davon.</h2>', '<h2>Wir lassen unsere Kunden sprechen.</h2>')
    for alt, neu in ERG_TEXTE:
        h = h.replace(alt, neu)
    seite.h = h


# Einleitung darunter war Füllstoff, die Karten sprechen für sich (Noah, 15.11.2026)
s.ersetze('<span class="kicker">Facebook &amp; Instagram</span><h2>Echte Betriebe, echte Zahlen.</h2><p class="lead">Werbung im Umkreis des Betriebs. Gezählt ist jede Anfrage und jede Bewerbung, die angekommen ist.</p>',
          '<span class="kicker">Fallstudien</span><h2>Ergebnisse unserer Kunden.</h2>')
ergebnisse_aktuell(s)
# Team-Sektion ohne Bühnen-Signet (siehe LEISTUNGS_SEK)
_a, _e = s.bereich('<section class="sek stimmen">')
_sek = s.h[_a:_e]
_sek2, _n = re.subn(r'<div class="bahn" aria-hidden="false">.*</div>(?=</section>)', lambda m: stimmen_alle(), _sek, count=1, flags=re.S)
assert _n == 1 and _sek2.count('class="stimme ') == 92, _sek2.count('class="stimme ')  # 46 mit Logo, je Reihe doppelt
s.h = s.h[:_a] + _sek2 + s.h[_e:]
assert s.h.count('<h2>So sehen unsere Seiten aus.</h2>') == 1
s.h = s.h.replace('<h2>So sehen unsere Seiten aus.</h2>', '<h2>Bezugsfertig.</h2>')  # wie auf der Websites-Seite
# Satz unter „Über 150 Betriebe vertrauen uns.“ fällt weg (Noah, 21.11.2026: „Von der Zimmerei über den Heizungsbauer bis zum Autohaus.“ das weg)
s.ersetze(' Von der Zimmerei bis zum Autohaus.', '')
# Unter „Wer hinter der Handwerksmanufaktur steht“: Foto & Video. Noah, 20.11.2026: „einfach eine Art Bildergalerie … sehr
# strukturiert, mit Bildern, die … langsam durchläuft … ausschließlich Content, den wir gemacht haben … und auch nicht so quer …
# kann ein bisschen dezenter sein“ (ersetzt die schräge, laute Wand vom 19.11.): zwei gerade Reihen, alle Kacheln gleich groß
# (3 : 2), langsam gegenläufig, nur Querformat-Fotos unserer Drehtage und unsere Querformat-Filme, keine Zahl-Zeile.
def wand_sek():
    teile = []
    for d in GALERIE["fotos"]:
        if d["w"] > d["h"]:
            teile.append(("bild", f'{FV}/g/{d["k"]}-480.webp', _html.unescape(d["betrieb"] or "")))
    for _, _, _, betrieb, r, mp4, poster in GALERIE_FILME:
        if r > 1:
            teile.append(("film", mp4, _html.unescape(betrieb).split(",")[0], poster))
    for k in GALERIE["kontakt"]:
        teile.append(("bild", f"{FV}/k/{k}.webp", "Stimpfle Sanitär & Heizung"))
    filme = [x for x in teile if x[0] == "film"]; bilder = [x for x in teile if x[0] == "bild"]
    schritt = max(1, len(bilder) // (len(filme) + 1))
    folge = []
    for i, b in enumerate(bilder):
        folge.append(b)
        if (i + 1) % schritt == 0 and filme:
            folge.append(filme.pop(0))
    folge += filme
    bahnen = [folge[i::2] for i in range(2)]
    for bahn in bahnen:
        for i in range(1, len(bahn)):
            if bahn[i][2] and bahn[i][2] == bahn[i - 1][2]:
                j = next((x for x in range(i + 1, len(bahn)) if bahn[x][2] != bahn[i - 1][2]), None)
                if j: bahn[i], bahn[j] = bahn[j], bahn[i]

    def kachel(x):
        if x[0] == "film":
            return f'<span class="wd-k"><video muted loop playsinline preload="none" data-wand="{x[1]}" poster="{x[3]}"></video></span>'
        return f'<span class="wd-k"><img data-wand="{x[1]}" alt="" decoding="async"></span>'
    spuren = "".join(f'<div class="wd-bahn"><div class="wd-spur" style="--t:{t}s">{"".join(kachel(x) for x in bahn) * 2}</div></div>'
                     for bahn, t in zip(bahnen, (210, 250)))
    return ('<section class="sek wd-sek"><div class="wrap"><div class="kopfzeile mitte reveal"><span class="kicker">Foto &amp; Video</span>'
            '<h2>Bei unseren Kunden gedreht.</h2>'
            '<p class="lead"><a class="textlink" href="/foto-video/">Mehr zu Foto &amp; Video '
            '<svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a></p></div></div>'
            f'<div class="wd" aria-hidden="true">{spuren}</div></section>'
            '<style>.wd-sek{overflow:hidden}.wd-sek .kopfzeile>.lead{justify-self:center!important;text-align:center!important}'
            '.wd{position:relative;display:grid;gap:12px;margin-top:clamp(24px,3vw,40px);--wh:clamp(120px,13vw,200px)}'
            '.wd::before,.wd::after{content:"";position:absolute;top:0;bottom:0;width:8vw;z-index:2;pointer-events:none}'
            '.wd::before{left:0;background:linear-gradient(90deg,var(--papier),transparent)}.wd::after{right:0;background:linear-gradient(270deg,var(--papier),transparent)}'
            '.wd-spur{display:flex;gap:12px;width:max-content;animation:wd-lauf var(--t) linear infinite}'
            '.wd-bahn:nth-child(2) .wd-spur{animation-direction:reverse}'
            '.wd:hover .wd-spur{animation-play-state:paused}'
            '.wd-k{flex:none;height:var(--wh);aspect-ratio:3/2;border-radius:var(--radius);overflow:hidden;background:var(--papier-2,#efe9df)}'
            '.wd-k img,.wd-k video{width:100%;height:100%;object-fit:cover;display:block}'
            '@keyframes wd-lauf{to{transform:translateX(-50%)}}'
            '@media (prefers-reduced-motion:reduce){.wd-spur{animation:none}.wd-bahn{overflow-x:auto}}</style>'
            # Bilder laden, sobald die Galerie naht; jeder Film lädt und läuft nur, solange er selbst im Bild ist
            '<script>(()=>{const w=document.querySelector(".wd");if(!w)return;let an=false;'
            'new IntersectionObserver(es=>{if(es[0].isIntersecting&&!an){an=true;w.querySelectorAll("img[data-wand]").forEach(x=>{x.src=x.dataset.wand})}},{rootMargin:"800px 0px"}).observe(w);'
            'const vio=new IntersectionObserver(es=>{for(const e of es){const v=e.target;if(e.isIntersecting){if(!v.getAttribute("src"))v.src=v.dataset.wand;v.play().catch(()=>{})}else{v.pause()}}},{rootMargin:"200px"});'
            'w.querySelectorAll("video[data-wand]").forEach(v=>vio.observe(v))})()</script>')


# s.nach('<section class="sek team-sek" id="team">', wand_sek())  — raus (Noah, 20.11.2026: „mach die sektion bei startseite einfach raus“)

s.entwurf()
s.schreibe(ZIEL / "index.html")


def unterseite(slug):
    return Seite((QUELLE / f"{slug}.html").read_text())


# Ergebnisse auf Neukunden/Mitarbeiter = dieselben Karten wie auf der Startseite (Noah, 19.11.2026: „viel, viel zu kompliziert …
# bei der Home-Seite siehst du, welche Simpelheit wir brauchen“). Die lange Fallstudie mit Text, Zitat, Mail-Raster und Zeilen fällt weg.
_ea, _ee = s.bereich('<section class="sek erg-sek" id="ergebnisse">')
ERG_HOME = s.h[_ea:_ee]


# Die HWM-Seite ist für alle Gewerke, nicht nur SHK (Noah, 19.11.2026: „wir müssen ja auf der HWM seite nicht nur auf shk gehen“)
GEWERKE_MISCHEN = {
    "neukundengewinnung": [("<b>Wärmepumpe statt Ölheizung</b><small>Eigentümer · Start dieses Jahr · 14 km entfernt</small>",
                            "<b>Einbauküche nach Maß</b><small>Eigentümer · Start dieses Jahr · 14 km entfernt</small>")],
    "mitarbeitergewinnung": [("<b>Kundendienst-Monteur</b><small>Führerschein BE · wechselbereit in 3 Monaten</small>",
                              "<b>Zimmerer</b><small>Führerschein BE · wechselbereit in 3 Monaten</small>"),
                             ("<b>Geselle, 2 Jahre</b><small>Führerschein B · ab sofort · 7 km entfernt</small>",
                              "<b>Elektroniker, 2 Jahre Geselle</b><small>Führerschein B · ab sofort · 7 km entfernt</small>")],
}


def ablauf_animiert(slug, h2, texte):
    """„Was wir übernehmen“ als der ursprüngliche animierte Baustein (Handy-Anzeigen, Umkreis-Radar, Filterfragen „passt“) statt
    Kundenfoto-Karten (Noah, 19.11.2026: „das macht ja so kein sinn da die kundenbilder reinzumachen, da könnte diese ursprüngliche
    art animations ding hin“). Die Kachel mit dem Kundenfoto bleibt draußen, Texte so kurz wie auf der Startseite."""
    q = (QUELLE / f"{slug}.html").read_text()
    a = q.index('<section class="sek band auf-dunkel bento-sek">')
    sek = q[a:q.index("</section>", a) + len("</section>")]
    zellen = re.findall(r'<article class="zelle[^"]*">.*?</article>', sek, re.S)
    assert len(zellen) == 4 and "<img" in zellen[0] and "handys-k" in zellen[1] and "umkreis" in zellen[2] and "tickets" in zellen[3], slug
    neu = []
    for i, (z, (titel, text)) in enumerate(zip(zellen[1:], texte), 1):
        z = re.sub(r'<span class="nummer">\d+</span><h3>.*?</h3><p>.*?</p>', f'<span class="nummer">0{i}</span><h3>{titel}</h3><p>{text}</p>', z, count=1, flags=re.S)
        assert f"<h3>{titel}</h3>" in z, (slug, i)
        neu.append(z)
    html = "".join(neu)
    if slug == "neukundengewinnung":
        # Bettina (Fischer) mit „Du willst dein Bad schon sehen, bevor die erste Fliese fällt?“ statt Josef (Noah, 20.11.2026:
        # „ist n guter clip … auch bei Unterseite Neukundengewinnung“), ab knapp vor ihrer Zeigegeste
        alt_v = 'data-src="/static/assets/vid/josef.mp4" data-poster="/static/assets/vid/poster/josef.jpg"'
        assert html.count(alt_v) == 1, html.count(alt_v)
        html = html.replace(alt_v, 'data-src="/static/assets/vid/bettina-fliese.mp4?v=2" data-poster="/static/assets/vid/poster/bettina-fliese.jpg?v=2"')  # v2: Start bei der Armbewegung (33,03 s)
        # Mirjanas Handy-Film (Sussmann-Anzeige) gehört zur Auftragsgewinnung (Noah, 21.11.2026: „das video von mirjana kann eher noch bei
        # der auftragsgewinnung mit rein also dieses handyvideo da“) → dritter Film in der Handy-Kachel
        _ende = html.index('</div>', html.index('<div class="handys-k"'))
        html = html[:_ende] + '<video class="" muted loop playsinline preload="none" data-lazy data-src="/static/assets/vid/mirjana-hook.mp4" data-poster="/static/assets/vid/poster/mirjana-hook.jpg" ></video>' + html[_ende:]
    if slug == "mitarbeitergewinnung":
        # „bei mitarbeitergewinnung dann das video von irlbacher mit rein“ (Noah, 21.11.2026): Irlbachers Stellenanzeige statt Mirjana
        alt_m = 'data-src="/static/assets/vid/mirjana-hook.mp4" data-poster="/static/assets/vid/poster/mirjana-hook.jpg"'
        assert html.count(alt_m) == 1, html.count(alt_m)
        html = html.replace(alt_m, 'data-src="/static/assets/fv/v/ir-geselle.mp4" data-poster="/static/assets/fv/v/ir-geselle.jpg"')
    for alt, neu_t in GEWERKE_MISCHEN.get(slug, []):
        assert html.count(alt) == 1, (slug, alt)
        html = html.replace(alt, neu_t)
    neu = [html]
    return ('<section class="sek band auf-dunkel bento-sek ablauf-ani"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Was wir übernehmen</span>'
            f'<h2>{h2}</h2></div><div class="bento">{"".join(neu)}</div></div></section>'
            '<style>.handys-k:has(video:nth-child(3)) video{width:104px}.handys-k:has(video:nth-child(3)){gap:0}'
            '.handys-k video:nth-child(3){transform:rotate(4deg) translateY(4px)}.handys-k:has(video:nth-child(3)) video+video{margin-left:-14px}'
            '@media (max-width:900px){.handys-k:has(video:nth-child(3)) video{width:min(84px,21vw)}}'
            '@media (min-width:1001px){.ablauf-ani .bento{grid-template-columns:repeat(6,minmax(0,1fr))}'
            '.ablauf-ani .zelle.mit-handys{grid-column:1/span 2;grid-row:1/span 2;min-height:0}'
            '.ablauf-ani .zelle.mit-handys .handys-k{left:0;right:0;top:clamp(40px,4vw,64px);justify-content:center;gap:16px}'
            '.ablauf-ani .zelle.mit-handys .handys-k video{width:clamp(140px,11.5vw,172px)}'
            '.ablauf-ani .zelle.z-2{grid-column:3/span 4;grid-row:1;min-height:260px}.ablauf-ani .zelle.mit-tickets{grid-column:3/span 4;grid-row:2}}</style>')


def _tickets(zeilen, pfad):
    return '<div class="tickets" aria-hidden="true">' + "".join(
        f'<div class="ticket" style="--d:{i * 0.14:.2f}s"><span class="tic"><svg viewBox="0 0 24 24"><path d="{pfad}"/></svg></span>'
        f'<span><b>{b}</b><small>{s}</small></span><span class="ok">{ok}</span></div>' for i, (b, s, ok) in enumerate(zeilen)) + '</div>'


def seo_ablauf():
    """SEO „Was wir übernehmen“ im selben animierten Baustein wie Neukunden/Mitarbeiter: Seiten-Liste, Karten-Radar, Bewertungen."""
    seite = "M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9zM14 3v6h6"
    stern = "M12 3l2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9z"
    radar = ('<svg class="umkreis" viewBox="0 0 200 200" aria-hidden="true"><circle cx="100" cy="100" r="92"/><circle cx="100" cy="100" r="64"/>'
             '<circle cx="100" cy="100" r="36"/><circle class="puls" cx="100" cy="100" r="92"/><circle class="kern" cx="100" cy="100" r="7"/></svg>')
    zellen = [
        '<article class="zelle z-4 mit-tickets">' + _tickets([("Drehkranz Liebherr", "Drehkranz Josef Schwarz", "Seite 1"),
                                                              ("Abbruch Ammersee", "Kirchner Thaining", "Seite 1"),
                                                              ("Zimmerei Schongau", "Zimmerei Knappich", "Seite 1")], seite)
    # Noahs Wahl 19.11.2026: „abbruch ammersee … kirchner oben, drehkranz liebherr – er steht auf 1, ich habs gemessen – zimmerei schongau“.
    # Pille „Seite 1“ statt Platz: Knappich stand am 23.09. auf Platz 2, Abbruch Ammersee ist von uns nicht nachgemessen.  # echte Messung 19.10.2026 aus der Rangliste (Noah, 19.11.2026: „sachen nehmen wo auch kunden von uns kommen“)
        + '<span class="nummer">01</span><h3>Eine Seite je Leistung</h3><p>Jede Leistung bekommt eine eigene Seite, mit deinem Ort drin.</p></article>',
        f'<article class="zelle z-2">{radar}<span class="nummer">02</span><h3>Dein Google-Profil</h3><p>Mit Leistungen und Fotos, damit dich die Karte zeigt.</p></article>',
    ]
    # Bewertungs-Kachel raus (Noah, 21.11.2026: „die sektion macht kein sinn bei seo“): bleiben Seiten je Leistung + Google-Profil

    return ('<section class="sek band auf-dunkel bento-sek ablauf-ani ablauf-seo"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Was wir übernehmen</span>'
            f'<h2>Den Weg nach vorn übernehmen wir.</h2></div><div class="bento">{"".join(zellen)}</div></div></section>'
            '<style>@media (min-width:1001px){.ablauf-seo .zelle.z-4{grid-column:1/span 4;grid-row:1}.ablauf-seo .zelle.z-2{grid-column:5/span 2;grid-row:1}'
            '}'
            '.ablauf-seo .ticket .ok{white-space:nowrap}@media (min-width:1001px){.ablauf-seo .zelle p{min-height:3em}}</style>')  # Titel beider Karten auf einer Linie (Design-Tor A)


def erg_karten(art, ohne=()):
    karten = [k for k in re.findall(r'<article class="erg reveal">.*?</article>', ERG_HOME, re.S)
              if f"<br><b>{art}</b>" in k and not any(o in k for o in ohne)]
    assert 1 <= len(karten) <= 3, (art, len(karten))
    karten = [re.sub(r'<a class="textlink"[^>]*>.*?</a>', "", k, flags=re.S) for k in karten]
    raster = {3: '', 2: ' style="grid-template-columns:repeat(2,minmax(0,1fr))"', 1: ' data-einzel style="grid-template-columns:minmax(0,1fr)"'}[len(karten)]
    # Eine Karte allein steht quer über die ganze Breite (Bild links, Zahlen rechts), sonst bleibt die halbe Sektion leer
    einzel = ('<style>@media (min-width:901px){.erg-sek .ergebnisse[data-einzel] .erg{grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);grid-template-rows:none}'
              '.erg-sek .ergebnisse[data-einzel] .erg-film{aspect-ratio:16/10;height:100%}.erg-sek .ergebnisse[data-einzel] .erg-in{align-self:center;padding:clamp(28px,3vw,48px)}'
              '.erg-sek .ergebnisse[data-einzel] .erg-zeile em{font-size:clamp(30px,2.6vw,40px)}}</style>') if len(karten) == 1 else ''
    return ('<section class="sek erg-sek" id="ergebnisse"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Die Ergebnisse</span>'
            f'<h2>Ergebnisse unserer Kunden.</h2></div><div class="ergebnisse"{raster}>{"".join(karten)}</div>'
            + (f'<p class="erg-wisch" aria-hidden="true">Wischen für {("beide", "alle drei")[len(karten) - 2]} Betriebe</p>' if len(karten) > 1 else '')
            + '</div></section>' + einzel)


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
                 ('<h2>So sehen unsere Seiten aus.</h2>', '<h2>Bezugsfertig.</h2>')],
    "suchmaschinenoptimierung": [('<h1>Dein nächster Kunde googelt gerade.</h1>', '<h1>Ganz oben ist dein Platz.</h1>'),
                 ('<h2>Den Weg nach vorn übernehmen wir.</h2>', '<h2>Vom ersten Suchwort bis Seite 1.</h2>'),
                 ('<h2>{SEITE1} Kundenseiten stehen auf Seite 1.</h2>', '<h2>{SEITE1}-mal Richtfest.</h2>'),
                 # Noah, 21.11.2026: „zu viel erklärung“ → Satz „Stand 19. Oktober …“ raus, die Zahlen-Kacheln darunter sagen es
                 ('<p class="lead">Stand 19. Oktober 2026: Wir haben jede Kundenseite mit dem Wort gesucht, das ein Kunde im Umkreis eintippt. Ohne Anmeldung, Anzeigen zählen nicht mit.</p>', '')],
    "foto-video": [('<h1>Fotos, auf denen man deinen Betrieb wiedererkennt.</h1>', '<h1>Wir setzen dein Handwerk ins Licht.</h1>'),
                 ('<h2>Den Drehtag übernehmen wir.</h2>', '<h2>Vom ersten Bild bis zum fertigen Film.</h2>')],
    "neukundengewinnung": [('<h1>Die Aufträge, die du willst. Nur für deinen Betrieb.</h1>', '<h1>Du fährst hin.<br> Den Rest machen wir.</h1>'),
                 ('<h2>Die Anzeigen übernehmen wir.</h2>', '<h2>Von der Anzeige bis zum Aufmaß.</h2>'),
                 ],
    "mitarbeitergewinnung": [('<h1>Leute, die bei dir anfangen wollen. Aus deinem Umkreis.</h1>', '<h1>Wir suchen.<br> Du stellst ein.</h1>'),
                 ('<h2>Die Suche übernehmen wir.</h2>', '<h2>Von der Anzeige bis zum Handschlag.</h2>'),
                 ],
}


def fertig(seite, slug, hero=None):
    ergebnisse_aktuell(seite)
    # „Erst selbst durchrechnen … kommt überall raus“ und „die Galerie genauso groß wie die Sektion rechts“ (Noah, 20.11.2026)
    seite.h = re.sub(r'\n?<(button|a)[^>]*class="uk-rechner"[^>]*>.*?</\1>', "", seite.h, flags=re.S)
    seite.h = re.sub(r'<dialog class="rd" id="rechner-dialog".*?</dialog>', "", seite.h, flags=re.S)
    seite.h = seite.h.replace('<a class="btn btn-bronze" href="#rechner-auf">Potenzial durchrechnen ', '<a class="btn btn-bronze" href="/kontakt/">Erstgespräch vereinbaren ')
    assert "uk-rechner" not in seite.h and "durchrechnen" not in seite.h, (slug, re.findall(r'.{60}durchrechnen.{20}', seite.h)[:2])
    if "uk-karte{align-items:stretch" not in seite.h:
        seite.h = seite.h.replace("</head>", f"<style>{KONTAKT_STIL}</style></head>", 1)
    if hero:  # Noah, 18.11.2026 abends: Leistungsseiten wieder mit den drei Säulen („davor fand ich es cleaner“), nur Foto & Video behält den Film-Hero
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
einfach(w, 'Wir bauen deine Website mit Fotos aus deinem Betrieb und einer eigenen Seite je Leistung, damit der Kunde bei dir anruft.', ('Unsere Seiten', 'Aufbau einer Seite'),
        fragen_lead='Preis, Dauer und was mit der alten Seite passiert.')
w.ersetze('<span class="kicker">Unsere Seiten</span><h2>Jedes Gewerk bekommt seine eigene Seite.</h2>', '<span class="kicker">Die Ergebnisse</span><h2>So sehen unsere Seiten aus.</h2>')
# Füll-Einleitungen auf einen schlichten Satz (Noah, 15.11.2026)
# Neueste Seiten nach vorn: Irlbacher als große erste Kachel, dann Wagenknecht und Schillinger (Noah, 19.11.2026:
# „die ganzen neuen seiten schillinger, irlbacher, juwelier … irlbacher ruhig bisschen präsent … vor allem auch bei den website konzepten“).
# Die Größe hängt an der Position im Raster (gross / gross rechts), deshalb Klassen nach dem Umsortieren neu vergeben.
_a, _e = w.bereich('<section class="sek" id="arbeiten">')
_sek = w.h[_a:_e]
_arts = re.findall(r'<article class="projekt[^"]*">.*?</article>(?=<article|</div>)', _sek, re.S)
_klassen = re.findall(r'<article class="(projekt[^"]*)">', _sek)
assert len(_arts) == len(_klassen) == 24, (len(_arts), len(_klassen))
# Reihenfolge und Größen nach Noah, 19.11.2026 abends: „Wagenknecht … nicht ganz oben … rechts oben … SD Hirsch, Schillinger
# einigermaßen, Zimmerei Koller kann ziemlich weit hoch, Dinkel Metallbau auch … anstatt Resch Bau größer darzustellen, weil bei
# Resch Bau dann irgendwie so ein ewiger Absatz unten drunter ist … genauso wie bei Planung Hindelang … Irlbacher haben wir
# doppelt drin … W&W Bau kann ein bisschen weiter hoch … Wohner kannst du gerne groß machen“.
# Groß wird nur, wer ein ganzes Seitenbild hat (Film + Seitenbild in der großen Kachel lässt unten einen leeren Streifen).
# 3 Spalten: eine große Kachel belegt 2 × 2, die zwei kleinen danach füllen die freie Spalte.
# ── Raster neu (Noah, 21.11.2026): „bei den seiten … will ich immer überall noch son vorher button - und die logos größer - und dann
# ne ein-satz beschreibung, was wir gemacht haben - und da können die seiten schon auch durchscrollen“ · „die seiten da schauen richtig
# unscharf aus“ · „nicht passend einkategorisiert“ · „die seite von senftleben eigentlich nicht mit reinnehmen“.
# Jede Kachel: Hero-Film der Live-Seite (1280×800), beim Drüberfahren läuft die ganze Seite durch (1440 px breit, am Handy beim
# Ins-Bild-Kommen bzw. per Antippen), „Vorher“-Knopf zeigt die alte Website in derselben Kachel (nur wo eine belegte Aufnahme
# existiert, raster_aufnahmen.vorher_quellen()). Aufnahmen: start-neu/raster_aufnahmen.py → static/assets/vid/raster/.
# Kategorien gegen die Live-Seiten geprüft (21.11.2026), dieselben stehen im Laufband der Startseite (KATEGORIE oben).
# Raster ohne Lücke: 23 Kacheln unter Entenmann. Eine große Kachel belegt 4 Plätze, also ginge es im Dreierraster nie auf —
# Kreitner liegt deshalb als „zwei“ (2 Spalten × 1 Reihe) neben Schuster Erisried; im Zweierraster sind zwei/groß/breit volle Reihen.
_V = "/static/assets/vid/raster"
_LG = "/static/assets/img/logos/"
RASTER = [  # (Name, k, Form, Logo, Satz) — nur Querformate (Noah, 21.11.2026: „die seiten bei website unterseite eher waagrecht, irlbacher
            # ist schon fast senkrecht und die seite ist abgeschnitten“): breit = ganze Reihe 2:1, Wohner/ESS/Kreitner seit 21.11. auch ganze Reihe (Noah: „die queren projekte wie wohner … sind alle erstaunlich klein“)
    ("Entenmann Haustechnik", "entenmann", "breit", "logo-entenmann-haustechnik.png", "Eine Seite je Leistung, dazu Notdienst."),
    ("SD Hirsch", "sdhirsch", "", "logo-sd-hirsch-weiss.png", "Eine Seite je Produkt, auch auf Englisch."),
    ("Björn Schillinger", "schillinger", "", "logo-bjoern-schillinger.png", "Eigene Seiten für Schränke und Küchen."),
    ("Dinkel Metallbau", "dinkel", "", "logo-dinkel-metallbau-weiss.png", "Von Treppen bis Zäune, für Tübingen."),
    ("Irlbacher Gebäudetechnik", "irlbacher", "breit", "logo-irlbacher.png", "Fotos vom Shooting und eine eigene Jobseite."),
    ("W&amp;W Bau", "ww", "", "logo-ww-bau.png", "Sieben Leistungsseiten, dazu Jobs."),
    ("Zimmerei Knappich", "knappich", "", "logo-zimmerei-knappich.png", "Projekte vom Holzhaus bis zum Carport."),
    ("Küchenhaus Hirschvogel", "hirschvogel", "", "logo-kuechenhaus-hirschvogel.png", "Eine Seite je Küchenlinie."),
    ("Zimmerei Koller", "koller", "breit", "logo-zimmerei-koller.png", "Eigene Seiten für Holzhaus und Aufstockung."),
    ("Baustoffe Kirchner", "kirchner", "", "logo-baustoffe-thaining-kirchner.png", "Vom Tiefbau bis zum Containerdienst."),
    ("Baureize", "baureize", "", "logo-baureize.png", "Maurer- und Estricharbeiten mit Galerie."),
    ("Resch Bau", "resch", "", "logo-resch-bau.png", "Massivhausbau, dazu der AwSV-Fachbetrieb."),
    ("Wohner Elektrotechnik", "wohner", "breit", "wohner_elektrotechnik_weiss_cropped.png", "PV, Speicher und Wallbox mit Projekten."),
    ("Planung Hindelang", "hindelang", "", "logo-planung-hindelang.png", "Vom Laserscan bis zum Energieausweis."),
    ("Dachbau Kraus", "kraus", "", "logo-dachbau-kraus-gmbh.png", "Dach und Fassade für Gewerbe."),
    ("Schwaighofer", "schwaighofer", "", "logo-schwaighofer-betontechnik-logo.png", "Hallenbau für die Landwirtschaft."),
    ("Erwin Schmidt &amp; Sohn", "ess", "breit", "logo-erwin-schmidt-sohn-weiss.png", "Sanitär, Heizung und Erneuerbare."),
    ("Vogel Holzbau", "vogel", "", "logo-thomas-vogel-holzbau.png", "Holzrahmenbau, Hallen und Sanierung."),
    ("Maser Tankschutz", "maser", "", "logo-maser-tankschutz-logo.png", "Jede Tankarbeit mit eigener Seite."),
    ("Schuster Erisried", "erisried", "", "logo-schuster-landmaschinen-agrartechnik.png", "Werkstatt, Landtechnik und Unimog-Teile."),
    ("Schreinerei Kreitner", "kreitner", "breit", "logo-schreinerei-kreitner.png", "Schwerpunkt barrierefreies Wohnen."),
    ("Juwelier Wagenknecht", "wagenknecht", "", "logo-juwelier-wagenknecht-farbe.png", "Werkstatt, Ankauf und Geschichte seit 1908."),
    ("Weber Metallbau", "weber", "", "w/logo-weber-metallbau.webp", "Vom Blech zum fertigen Teil."),
    ("Malermeister Müller", "mueller", "", "logo-malermeister-mueller.png", "Von Fassade bis Beschriftung."),
]
_FILM = {"": (1280, 800), "breit": (1920, 960), "zwei": (1640, 560)}


def _logo_mass(datei):
    # Gleiche optische Größe: gleiche Fläche je Logo, Höhe 32–68 px, Breite höchstens 190 px (aus dem echten Bildinhalt gerechnet)
    from PIL import Image
    im = Image.open(WURZEL / ("static/assets/img/logos/" + datei)).convert("RGBA")
    bb = im.getchannel("A").getbbox() or (0, 0, *im.size)
    r = (bb[2] - bb[0]) / max(1, bb[3] - bb[1])
    h = max(22, min(34, (2200 / r) ** .5)); b = h * r
    if b > 88:
        b = 88; h = b / r
    return round(b), round(h)


def _vq(datei):
    # Versionsnummer aus der Dateizeit, damit der Browser nach einer Neuaufnahme nie das alte Video zeigt (21.11.2026)
    return f"?v={int((WURZEL / 'static/assets/vid/raster' / datei).stat().st_mtime)}"


def _raster_karte(name, k, form, logo, satz):
    # Farblogo ohne schwarzen Kasten (Noah, 21.11.2026: „logo da noch bisschen größer der firmen - und in farbe, ohne schwarzen hintergrund“)
    logo = f"farbe/{k}.png"
    assert len(satz) <= 45 and "·" not in satz, (name, len(satz))  # kurz, sonst drückt der Satz die Kachel hoch (Noah, 21.11.2026)
    fw, fh = _FILM[form]
    film = " film" if form in ("gross", "gross rechts", "breit", "zwei") else ""
    vorher = (WURZEL / f"static/assets/vid/raster/v{k}.webp").exists()
    # große Kachel: fast quadratischer Film am Desktop, der 16:10-Film fürs Handy (main.js nimmt data-src-mobil unter 760 px)
    q = "-q" if form.startswith("gross") else ""
    for x in ("webm", "jpg"):
        assert (WURZEL / f"static/assets/vid/raster/h{k}{q}.{x}").exists() and (WURZEL / f"static/assets/vid/raster/h{k}.{x}").exists(), (k, x)
    assert (WURZEL / f"static/assets/vid/raster/s{k}.webp").exists(), k
    from PIL import Image as _Im
    _w, _h = _Im.open(WURZEL / ("static/assets/img/logos/" + logo)).size
    _r = _w / _h
    # Optisch gleich groß (Apple-Logoreihe): gleiche Fläche je Logo in einem festen Rahmen 112 × 48, unabhängig vom Namen
    # (Noah, 21.11.2026: „in welcher vergleichbaren größe du das logo da reinmachen musst? IMMER APPLE DESIGN REGELN“)
    _RB, _RH, _FL = 112, 48, 4600
    _rh = 62 if _r < 1.3 else _RH  # fast quadratische Marken (W&W, Baureize) dürfen höher, sonst wirken sie winzig (Probe H)
    lb = min((_FL * _r) ** .5, _RB); lh = lb / _r
    if lh > _rh:
        lh = _rh; lb = lh * _r
    lb, lh = round(lb), round(lh)
    lc = round(lb / _RB * 24, 2)  # schrumpft mit der Kachel im selben Verhältnis (24cqi = voller Rahmen)
    return (f'<article class="projekt{" " + form if form else ""} reveal" data-k="{k}"><div class="schirm ra{film}">'
            f'<video class="hero-lauf" muted loop playsinline preload="none" data-src="{_V}/h{k}{q}.webm{_vq(f'h{k}{q}.webm')}" data-poster="{_V}/h{k}{q}.jpg{_vq(f'h{k}{q}.jpg')}" '
            + (f'data-src-mobil="{_V}/h{k}.webm{_vq(f"h{k}.webm")}" ' if q else "")
            + f'width="{fw}" height="{fh}" aria-label="{name} — Startseite, wie sie live läuft"></video>'
            f'<img class="ra-seite" data-src="{_V}/s{k}.webp{_vq(f's{k}.webp')}" alt="" aria-hidden="true" decoding="async">'
            + (f'<img class="ra-alt" data-src="{_V}/v{k}.webp{_vq(f'v{k}.webp')}" alt="Die alte Website von {name}" decoding="async">'
               f'<button class="ra-vorher" type="button" aria-pressed="false" aria-label="Alte Website von {name} zeigen">Vorher</button>' if vorher else "")
            # Logo rechts neben dem ganzen Text (Noah, 21.11.2026: „das logo kann doch einfach da rechts neben den text da jeweils“)
            + f'</div><div class="unten" style="--lb:{lb}px;--lc:{lc}cqi"><div class="ra-text"><small>{KATEGORIE[name]}</small><b>{name}</b><p class="ra-satz">{satz}</p></div>'
            f'<span class="ra-logo"><img loading="lazy" src="{_LG}{logo}" alt="Logo {name}" width="{lb}" height="{lh}"></span></div></article>')


_namen_quelle = {re.search(r"<b>(.*?)</b>", x).group(1) for x in _arts}
assert "Senftleben Haustechnik" in _namen_quelle  # steht noch in der Vorlage, fällt hier raus (Noah, 21.11.2026)
_neu = [_raster_karte(*r) for r in RASTER]
assert len(_neu) == 24 and len({r[0] for r in RASTER}) == 24 and not any("Senftleben" in x for x in _neu)
# Plätze im Dreierraster: breit 3, groß 4, zwei 2, normal 1 → muss aufgehen (sonst Lücke in der letzten Reihe)
assert sum({"breit": 3, "zwei": 2, "": 1}[r[2]] for r in RASTER) % 3 == 0 and not any(r[2].startswith("gross") for r in RASTER)
# Zweierraster: breit/groß/zwei je eine volle Reihe, die normalen paarweise
assert sum(1 for r in RASTER if not r[2]) % 2 == 0
RASTER_STIL = (
    '<style>/* Websites-Raster (start-neu/bauen.py, 21.11.2026) */'
    '#arbeiten .schirm.ra img{animation:none!important}'
    '#arbeiten .schirm.ra .ra-seite,#arbeiten .schirm.ra .ra-alt{position:absolute;left:0;top:0;width:100%;height:auto;max-width:none;opacity:0;'
    'transition:opacity .3s var(--ease);pointer-events:none;will-change:transform;z-index:1}'
    '#arbeiten .schirm.ra .ra-alt{z-index:2;min-height:100%;object-fit:cover;object-position:top center;background:var(--papier-2)}'
    '#arbeiten .schirm.ra.zeigt .ra-seite,#arbeiten .schirm.ra.alt .ra-alt{opacity:1}'
    '#arbeiten .ra-vorher{position:absolute;top:12px;right:12px;z-index:3;min-height:36px;padding:0 15px;border:0;border-radius:var(--pille,999px);'
    'background:rgba(22,19,14,.82);color:#faf7f1;font:600 14px/1 inherit;letter-spacing:.02em;cursor:pointer;'
    'box-shadow:0 6px 18px -8px rgba(22,19,14,.6);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);transition:background var(--schnell),transform var(--schnell)}'
    '#arbeiten .ra-vorher:hover{transform:translateY(-1px);background:rgba(22,19,14,.95)}'
    '#arbeiten .ra-vorher:focus-visible{outline:2px solid var(--bronze);outline-offset:2px}'
    '#arbeiten .schirm.ra.alt .ra-vorher{background:var(--bronze);color:var(--tinte)}'
    '#arbeiten .ra-vorher::before{content:"";position:absolute;inset:-4px}'
    # Kachel nie breiter als ihre Spalte: ohne feste Spalte rechnete die 16:10-Fläche ihre Breite aus der Reihenhöhe (736 statt 399 px)
    '#arbeiten .projekt{grid-template-columns:minmax(0,1fr)}#arbeiten .projekt .schirm{width:100%;min-width:0}'
    '#arbeiten .projekt .unten{display:flex;flex-direction:column;gap:6px;min-width:0}'
    '#arbeiten .ra-satz{margin:2px 0 0;font-size:16px;line-height:1.45;color:var(--tinte-2);max-width:44ch}'
    '#arbeiten .projekt .unten{display:grid;grid-template-columns:minmax(0,1fr) auto;column-gap:clamp(12px,1.4vw,20px);align-items:start}''#arbeiten .ra-text{display:flex;flex-direction:column;gap:6px;min-width:0}''#arbeiten .ra-logo{align-self:center}''#arbeiten .ra-text b,#arbeiten .ra-text small{line-height:1.3}''#arbeiten .projekt .unten .ra-logo{height:clamp(44px,4vw,56px);min-width:0;padding:0 clamp(8px,0.9vw,12px)}''#arbeiten .projekt .unten .ra-logo img{width:auto!important;height:auto!important;max-width:clamp(56px,6vw,88px);max-height:clamp(22px,2.4vw,34px)}''#arbeiten .projekte{container-type:inline-size}''#arbeiten .projekte{grid-auto-flow:row dense}'
    # Noah, 21.11.2026: „branche kleine schrift, eine zeile dann name max 1 zeile und drunter 2 - und dann das logo rechts daneben“
    # Schrift wächst mit der Kachel (cqi), damit Branche und Name in JEDER Breite in eine Zeile passen; Design-Tor G misst 340–1920 px
    '#arbeiten .projekt{container-type:inline-size}''#arbeiten .projekt .unten .ra-text small{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:13px;letter-spacing:.07em;line-height:1.35;min-height:0}''#arbeiten .projekt .unten .ra-text b{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:clamp(15px,5.4cqi,21px);line-height:1.3;min-height:0}''#arbeiten .projekt .unten .ra-satz{display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:2;overflow:hidden;min-height:2.9em;max-width:none;font-size:clamp(14px,4.4cqi,17px)}''#arbeiten .projekt .unten .ra-logo{align-self:center;height:clamp(40px,11cqi,56px);padding:0 clamp(6px,2.2cqi,12px)}''@container (max-width:400px){#arbeiten .projekt .unten .ra-text small{letter-spacing:.03em}#arbeiten .projekt .unten{column-gap:10px}}''@container (max-width:340px){#arbeiten .projekt .unten .ra-text b{font-size:15px}#arbeiten .projekt .unten .ra-logo img{max-width:38px!important}}''@container (max-width:290px){#arbeiten .projekt .unten .ra-text b{font-size:14px}#arbeiten .projekt .unten .ra-logo{padding:0 5px}#arbeiten .projekt .unten{padding-left:16px;padding-right:16px;column-gap:8px}#arbeiten .projekt .unten .ra-logo img{max-width:32px!important}}''#arbeiten .projekt .unten .ra-logo img{max-width:clamp(40px,15cqi,88px)!important;max-height:clamp(20px,6cqi,34px)!important}'
    '#arbeiten .ra-logo{flex:none;display:inline-flex;align-items:center;justify-content:center;height:56px;min-width:72px;padding:0 12px;border-radius:10px;background:var(--tinte)}'
    '#arbeiten .projekt .unten .zeile .ra-logo img{display:block;max-width:100%;max-height:100%;object-fit:contain;background:none;padding:0;border-radius:0}'
    '#arbeiten .projekt.zwei{grid-column:span 2;display:flex;flex-direction:column}'
    '#arbeiten .projekt.zwei .schirm.film{flex:1;aspect-ratio:auto;min-height:220px}'
    '#arbeiten .schirm.film video.hero-lauf{object-fit:cover;object-position:left top}'
    '@media (max-width:1000px){#arbeiten .projekt.zwei{grid-column:1 / -1}#arbeiten .projekt.zwei .schirm.film{flex:none;aspect-ratio:2/1;min-height:0}}'
    '@media (max-width:700px){#arbeiten .projekt.zwei .schirm.film,#arbeiten .projekt.breit .schirm.film{aspect-ratio:16/10}'
    '#arbeiten .ra-logo{height:48px}#arbeiten .ra-satz{font-size:15px}}'
    # doppelt breite Kachel: Film genau so hoch wie der Film der Nachbarkachel (16:10 einer Spalte), sonst steht ihr Name tiefer (Design-Tor A)
    '@media (min-width:1001px){#arbeiten .projekte .projekt.zwei .schirm.film{flex:none;aspect-ratio:auto;min-height:0;height:calc((100cqw - 2 * var(--gap)) / 3 * 10 / 16)}}'
    # Farblogo frei auf der Karte, kein schwarzer Kasten; Breite schrumpft mit schmaler Kachel (30cqi), Design-Tor G hält Name und Branche einzeilig
    '#arbeiten .projekt .unten .ra-logo{background:none!important;padding:0!important;height:auto!important;min-width:0!important;border-radius:0!important;box-shadow:none!important}'
    # Fußzeile: Branche und Name links, Logo rechts in festem Rahmen (alle Logos optisch gleich groß), Satz darunter
    '#arbeiten .projekt .unten{display:grid!important;grid-template-columns:minmax(0,1fr) auto!important;grid-template-areas:"k l" "n l" "s l";column-gap:clamp(12px,3cqi,22px);row-gap:6px;align-items:start}'
    '#arbeiten .projekt .unten .ra-text{display:contents}'
    '#arbeiten .projekt .unten .ra-text small{grid-area:k}#arbeiten .projekt .unten .ra-text b{grid-area:n;font-size:clamp(14px,4.4cqi,20px)!important}#arbeiten .projekt .unten .ra-satz{grid-area:s}'
    '#arbeiten .projekt .unten .ra-logo{grid-area:l;align-self:center;justify-self:end;display:flex;justify-content:flex-end;min-width:0!important}'
    '#arbeiten .projekt .unten .ra-logo img{width:calc(var(--lb) * var(--ls,.85))!important;max-width:none!important;height:auto!important;max-height:none!important}'
    # Logo nimmt keine Zeilenhöhe ein (Höhe 0, mittig über Branche/Name), sonst schiebt ein hohes Logo den Namen tiefer als in der Nachbarkachel (Probe A)
    '#arbeiten .projekt .unten .ra-logo{height:0!important;overflow:visible;position:relative}'
    '#arbeiten .projekt .unten .ra-logo img{transform:translateY(-50%)}'
    # Logo-Maßstab je Bildschirmbreite statt Container-Einheiten (cqi wurde im Testbrowser je nach Ladezeitpunkt anders aufgelöst, 21.11.2026)
    '@media (min-width:1201px){#arbeiten .projekt.breit .unten{--ls:1}}'
    '@media (max-width:1200px){#arbeiten .projekt .unten{--ls:.7}}'
    '@media (max-width:1000px){#arbeiten .projekt .unten{--ls:.66}}'
    '@media (max-width:760px){#arbeiten .projekt .unten{--ls:.6}}'
    '@media (max-width:400px){#arbeiten .projekt .unten{--ls:.48}}''@media (max-width:360px){#arbeiten .projekt .unten{--ls:.42}}'
    '@container (max-width:460px){#arbeiten .projekt .unten{grid-template-areas:"k l" "n l" "s s"}}'
    '@container (max-width:310px){#arbeiten .projekt .unten .ra-text b{font-size:13.5px!important}}'
    
    '</style>')
RASTER_JS = (
    '<script>(()=>{const sek=document.getElementById("arbeiten");if(!sek)return;'
    'const ruhig=matchMedia("(prefers-reduced-motion: reduce)").matches,maus=matchMedia("(hover:hover) and (pointer:fine)").matches,TEMPO=120;'
    'sek.querySelectorAll(".schirm.ra").forEach(schirm=>{'
    'const seite=schirm.querySelector(".ra-seite"),alt=schirm.querySelector(".ra-alt"),knopf=schirm.querySelector(".ra-vorher"),karte=schirm.closest(".projekt");'
    'let lauf=null,an=false,uhr=0;'
    'const aktiv=()=>schirm.classList.contains("alt")?alt:seite;'
    'const laden=(b,f)=>{if(!b)return;if(!b.getAttribute("src"))b.src=b.dataset.src;if(!f)return;if(b.complete&&b.naturalHeight)f();else b.addEventListener("load",f,{once:true})};'
    'const stand=b=>new DOMMatrix(getComputedStyle(b).transform).m42||0;'
    'const fahr=(b,ziel,dauer,kurve)=>{const von=stand(b);lauf&&lauf.cancel();'
    'lauf=b.animate([{transform:`translateY(${von}px)`},{transform:`translateY(${ziel}px)`}],{duration:dauer(von),easing:kurve,fill:"forwards"});lauf.b=b};'
    'const start=()=>{an=true;const b=aktiv();if(b===seite)schirm.classList.add("zeigt");'
    'laden(b,()=>{if(!an||aktiv()!==b||ruhig)return;const weg=b.offsetHeight-schirm.clientHeight;if(weg<=8)return;'
    'fahr(b,-weg,von=>Math.max(1500,(weg+von)/TEMPO*1000),"cubic-bezier(.35,0,.3,1)")})};'
    'const stop=()=>{an=false;clearTimeout(uhr);if(lauf)fahr(lauf.b,0,()=>450,"cubic-bezier(.2,.7,.2,1)");schirm.classList.remove("zeigt")};'
    'if(knopf)knopf.addEventListener("click",e=>{e.stopPropagation();const neu=!schirm.classList.contains("alt");'
    'lauf&&lauf.cancel();lauf=null;[seite,alt].filter(Boolean).forEach(b=>b.getAnimations().forEach(a=>a.cancel()));'
    'schirm.classList.toggle("alt",neu);knopf.setAttribute("aria-pressed",String(neu));knopf.textContent=neu?"Nachher":"Vorher";'
    'knopf.setAttribute("aria-label",(neu?"Neue":"Alte")+" Website zeigen");laden(alt);if(an)start()});'
    'if(maus){karte.addEventListener("pointerenter",e=>{if(e.pointerType==="mouse")start()});karte.addEventListener("pointerleave",e=>{if(e.pointerType==="mouse")stop()});'
    'new IntersectionObserver((es,o)=>{if(es[0].isIntersecting){o.disconnect();(window.requestIdleCallback||setTimeout)(()=>laden(seite))}},{rootMargin:"300px 0px"}).observe(schirm)}'
    'else{schirm.addEventListener("click",()=>an?stop():start());'
    'new IntersectionObserver(es=>es.forEach(e=>{clearTimeout(uhr);if(e.isIntersecting)uhr=setTimeout(start,1400);else if(an)stop()}),{threshold:.6}).observe(schirm)}'
    '})})()</script>')
_ra = _sek.index(_arts[0][:60])
_re = _sek.rindex("</article>") + len("</article>")
_sek2 = _sek[:_ra] + "".join(_neu) + _sek[_re:]
assert _sek2.count('<article class="projekt') == 24 and _sek2.count('class="ra-vorher"') == sum(
    (WURZEL / f"static/assets/vid/raster/v{r[1]}.webp").exists() for r in RASTER)
_sek2 = _sek2[:-len("</section>")] + RASTER_STIL + RASTER_JS + "</section>"
w.h = w.h[:_a] + _sek2 + w.h[_e:]
assert 'Wischen für alle 24 Seiten' in w.h
w.ersetze('<p class="lead">Jede mit Fotos aus dem eigenen Betrieb, jede auf ihr Gewerk und ihren Umkreis gebaut. Fahr über eine Seite, dann scrollt sie durch.</p>',
          '<p class="lead">Alle live. Tipp eine an.</p>')
# Durchgezogen (Noah, 19.11.2026: „jo und des ziehst du jetzt durch“): keine Problem-Kästen, keine Kundenfoto-Karten im Ablauf,
# stattdessen der ursprüngliche animierte Baustein „Aufbau einer Seite“ (Browser mit fünf Stellen, die nacheinander aufleuchten)
# Raus (Noah, 19.11.2026 abends: „die sektion raus - brauchen nicht erklären - es geht drum was der kunde hat“): kein Bauplan einer
# Seite. Stattdessen, was der Kunde bekommt (Noah, gleich danach: „so eine Sektion … was wir übernehmen … und wofür sie da ist …
# was wir alles machen, zack, zack, zack“): ein Satz, wofür die Seite da ist, dann sechs Karten, jede ein Ding, das er nicht selbst macht.
w.heraus('<section class="sek grund aufbau-sek">')
assert "aufbau-sek" not in w.h and "Aufbau einer Seite" not in w.h
_IC = {
    "foto": '<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
    "seiten": '<rect x="4" y="3" width="12" height="15" rx="1.5"/><path d="M8 21h11a1 1 0 0 0 1-1V7M7.5 8h5M7.5 11.5h5"/>',
    "text": '<path d="M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16z"/><path d="M13.5 6.5l4 4"/>',
    "google": '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5 5"/>',
    "anfrage": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1A16 16 0 0 1 4 5a1 1 0 0 1 1-1z"/>',
    "danach": '<path d="M12 3l7 3v5c0 4.5-3 8.5-7 10-4-1.5-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/>',
}
_WU = [("foto", "Fotos aus deinem Betrieb", "Wir kommen vorbei und fotografieren dein Team, deine Fahrzeuge und deine Arbeit."),
       ("seiten", "Eine Seite je Leistung", "Bad, Dach, Treppe: Jede Leistung bekommt ihre eigene Seite, damit Google sie findet."),
       ("text", "Alle Texte", "Wir schreiben alles. Du liest nur drüber."),
       ("google", "Bei Google", "Schnell am Handy, alte Adressen leiten weiter."),  # einzeilig wie die Nachbarkarten (Noah, 21.11.2026)
       ("anfrage", "Anfragen direkt zu dir", "Anruf-Knopf und Formular. Jede Anfrage landet sofort bei dir."),
       ("danach", "Nach dem Start", "Updates und kleine Änderungen. Ein Satz genügt.")]
# Gleicher Baustein wie „Was wir übernehmen“ auf Neukunden/Mitarbeiter/SEO (Noah, 19.11.2026: „ähnlich wie die Sektion bei
# Neukundengewinnung, Mitarbeitergewinnung … dass sich das Design halt mehr durch die Seite generell noch durchzieht“):
# dunkles Band, Kacheln mit Nummer, bewegtem Bild, Titel, einem Satz.
_ic = lambda k: f'<span class="web-ic" aria-hidden="true"><svg viewBox="0 0 24 24">{_IC[k]}</svg></span>'
_seite = "M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9zM14 3v6h6"
_post = "M4 6h16v12H4zM4 7l8 6 8-6"
_web_zellen = [
    '<article class="zelle z-3 hoch mit-handys web-fotos"><div class="handys-k" aria-hidden="true">'
    f'<img src="{FV}/g/kl-flex-900.webp" alt="" loading="lazy" decoding="async"><img src="{FV}/g/cs-schweissen-900.webp" alt="" loading="lazy" decoding="async"></div>'
    f'<span class="nummer">01</span><h3>{_WU[0][1]}</h3><p>{_WU[0][2]}</p></article>',
    # 02 + 03 in einer Kachel (Noah, 21.11.2026: „sektion 02 und 03 lassen sich verknüpfen … sodass die sektion kleiner ist und
    # dann darunter einfach die … anderen sachen kommen“): Seiten links, Anfragen rechts, eine Überschrift; die drei kleinen
    # Kacheln stehen darunter rechts neben 01 (Raster 9 Spalten: 01 = 3, rechts 6 = Doppelkachel bzw. 3 × 2).
    '<article class="zelle mit-tickets web-seiten"><div class="web-zwei">' + _tickets([("Badsanierung", "Eigene Seite · mit deinem Ort", "online"),
                                                                       ("Dachstuhl neu", "Eigene Seite · mit deinem Ort", "online"),
                                                                       ("Treppen aus Holz", "Eigene Seite · mit deinem Ort", "online")], _seite)
    + _tickets([("Neue Anfrage: Badsanierung", "Formular · mit Fotos und Nummer", "neu"),
                ("Rückruf gewünscht", "Anruf-Knopf am Handy", "neu"),
                ("Neue Anfrage: Carport", "Formular · mit Fotos und Nummer", "neu")], _post)
    + '</div><span class="nummer">02</span><h3>Eine Seite je Leistung. Jede Anfrage direkt zu dir.</h3>'
      '<p>Bad, Dach, Treppe: Jede Leistung bekommt ihre eigene Seite, damit Google sie findet. Anruf-Knopf und Formular bringen jede Anfrage sofort zu dir.</p></article>',
] + [f'<article class="zelle z-klein">{_ic(i)}<span class="nummer">0{n}</span><h3>{titel}</h3><p>{text}</p></article>'
     for n, (i, titel, text) in enumerate([_WU[2], _WU[3], _WU[5]], 3)]
WU_SEK = ('<section class="sek band auf-dunkel bento-sek ablauf-web"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Was wir übernehmen</span>'
          '<h2>Du lieferst den Betrieb. Wir den Rest.</h2>'
          '<p class="lead">Deine Website ist dein Schaufenster: Wer dich sucht, sieht deine Arbeit und ruft dich an statt den Nächsten.</p></div>'
          f'<div class="bento">{"".join(_web_zellen)}</div></div></section>'
          '<style>@media (min-width:901px){.ablauf-web .bento{grid-template-columns:repeat(9,minmax(0,1fr))}'
          '.ablauf-web .web-fotos{grid-column:1/span 3;grid-row:1/span 2;min-height:0}'
          '.ablauf-web .web-fotos .handys-k{left:0;right:0;top:clamp(40px,4vw,64px);justify-content:center;gap:0}''.ablauf-web .web-fotos .handys-k img{width:clamp(170px,calc(10.5vw + 72px),228px)}.ablauf-web .web-fotos .handys-k img+img{margin-left:-96px;transform:rotate(-3deg) translateY(90px)}.ablauf-web .web-fotos .handys-k img:first-child{position:relative;z-index:2}'  # Monteur vorn, sein Kopf bleibt frei
          '.ablauf-web .web-seiten{grid-column:4/span 6;grid-row:1}'
          '.ablauf-web .z-klein{grid-column:span 2;grid-row:2;min-height:260px}'
          '.ablauf-web .web-zwei{display:grid;grid-template-columns:1fr 1fr;gap:12px}.ablauf-web .web-zwei .tickets{margin:8px 0 22px}'
          '.ablauf-web .web-zwei .ticket b{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.ablauf-web .web-zwei .ticket>span:nth-child(2){min-width:0}}'
          '@media (max-width:900px){.ablauf-web .web-zwei .tickets+.tickets{margin-top:-14px}.ablauf-web .web-zwei .ticket:nth-child(3){display:none}}'
          '.ablauf-web .handys-k img{width:clamp(150px,13vw,196px);aspect-ratio:9/16;border-radius:16px;object-fit:cover;border:2px solid rgba(250,247,241,.28);'
          'transform:rotate(3deg);box-shadow:0 20px 40px -20px rgba(0,0,0,.7);transition:transform .5s var(--ease)}'
          '.ablauf-web .handys-k img:nth-child(2){transform:rotate(-3deg) translateY(14px)}'
          '.ablauf-web .web-fotos:hover .handys-k img{transform:rotate(5deg) translateY(-6px)}.ablauf-web .web-fotos:hover .handys-k img:nth-child(2){transform:rotate(-5deg) translateY(84px)}'
          '.ablauf-web .web-ic{width:56px;height:56px;border-radius:16px;background:rgba(250,247,241,.08);box-shadow:inset 0 0 0 1px rgba(250,247,241,.12);display:grid;place-items:center;'
          'margin:18px 0 auto;transition:transform var(--schnell),background var(--schnell)}'
          '.ablauf-web .web-ic svg{width:26px;height:26px;fill:none;stroke:var(--bronze-hell);stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}'
          '.ablauf-web .z-klein:hover .web-ic{transform:rotate(-6deg) scale(1.08);background:rgba(250,247,241,.14)}'
          '.ablauf-web .z-klein{justify-content:flex-start}.ablauf-web .z-klein .web-ic{margin:18px 0 0}.ablauf-web .z-klein h3{margin-top:28px}'  # Kacheln oben bündig: Icon, Titel, Text stehen in allen drei auf derselben Linie (Noah, 21.11.2026: „wieso muss ich es jedes mal wieder dazusagen mit den design regeln“)
          ''
          '.ablauf-web .ticket .ok{white-space:nowrap}'
          '@media (max-width:900px){.ablauf-web .zelle.web-fotos .handys-k{display:flex;position:relative;right:auto;top:auto;justify-content:center;margin:6px 0 22px}'
          '.ablauf-web .handys-k img{width:min(132px,34vw)}.ablauf-web .z-klein{min-height:0}}</style>')
w.nach('<section class="hero-klein">', WU_SEK)
assert w.h.count('<article class="zelle') == 5 and "ablauf-web" in w.h
w.vor('<section class="sek faq">', STIMMEN)
fertig(w, "websites", hero_unter("websites"))

# ── 3 · Suchmaschinenoptimierung
g = unterseite("suchmaschinenoptimierung")
SEITE1 = nur_website_kunden(g)
einfach(g, 'Dein nächster Kunde tippt dein Gewerk und deinen Ort ein und ruft den an, der oben steht.', ('Nachgemessen, nicht behauptet',),
        fragen_lead='Wie lange es dauert und ob es auch in der Großstadt geht.')
hero_knopf(g, "/websites/#arbeiten", "#ergebnisse")
g.ersetze('<section class="sek grund rangliste-sek"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Nachgemessen, nicht behauptet</span><h2>Wo unsere Kunden bei Google wirklich stehen.</h2>',
          f'<section class="sek grund rangliste-sek" id="ergebnisse"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Die Ergebnisse</span><h2>{SEITE1} Kundenseiten stehen auf Seite 1.</h2>')
g.nach('<section class="hero-klein">', seo_ablauf())
g.vor('<section class="sek faq">', STIMMEN)
fertig(g, "suchmaschinenoptimierung", hero_unter("suchmaschinenoptimierung"))

# ── 4 · Foto & Video (zwei Ergebnis-Sektionen wie die Startseite: Filme + Fotos; dafür ohne Kundenstimmen)
f = unterseite("foto-video")
einfach(f, 'Wir kommen einen Tag mit Kamera und Drohne zu dir, danach hast du Bilder und Filme für deine Website und deine Anzeigen.',
        ('Am Drehtag entstanden', 'Aus unseren Shootings', 'So läuft der Drehtag'))
hero_knopf(f, "/websites/#arbeiten", "#ergebnisse", "Arbeiten ansehen")
f.ersetze('<section class="sek band auf-dunkel"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Am Drehtag entstanden</span><h2>Ein Drehtag, daraus der Film für deine Startseite und die Clips für deine Anzeigen.</h2>',
          '<section class="sek band auf-dunkel" id="ergebnisse"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Die Filme</span><h2>Diese Filme sind am Drehtag entstanden.</h2>')
f.ersetze('<span class="kicker">Aus unseren Shootings</span>', '<span class="kicker">Die Fotos</span>')
f.ersetze('<p class="lead">Der Chef erzählt, die Drohne zeigt den Hof, die Kamera steht an der Maschine. Diese sechs Filme sind so bei unseren Kunden entstanden, gedreht im laufenden Betrieb. Die Fragen schreiben wir vorher, du musst nichts auswendig lernen.</p>',
          '<p class="lead">Entstanden im laufenden Betrieb unserer Kunden.</p>')
f.ersetze('<p class="lead">Hallen, Baustellen, Bäder und Werkstätten, von der Zimmerei bis zur Haustechnik. Jedes Bild ist an einem Drehtag bei einem Kunden entstanden, mit den Leuten, die dort arbeiten.</p>',
          '<p class="lead">Jedes Bild ist an einem Drehtag bei einem Kunden entstanden.</p>')
# Ablauf ohne Kundenfotos: die ursprüngliche Treppe „So läuft der Drehtag“ (vier Schritte mit Symbol) statt drei Fotokarten
f.h, _n = re.subn(r'<span class="kicker">So läuft der Drehtag</span><h2>Ein Tag bei dir, und dein Betrieb läuft dabei weiter\.</h2><p class="lead">.*?</p>',
                  '<span class="kicker">Was wir übernehmen</span><h2>Den Drehtag übernehmen wir.</h2>', f.h, count=1, flags=re.S)
assert _n == 1
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
fertig(f, "foto-video", (hero_foto_video(), 3500))  # Takt je Lage steht in data-dauer

# ── 5 · Neukundengewinnung
n = unterseite("neukundengewinnung")
einfach(n, 'Anzeigen mit deinen Leuten, nur in deinem Umkreis, und jede Anfrage gehört dir allein.', ('Fallstudie · Badsanierung',))
hero_knopf(n, "/websites/#arbeiten", "#ergebnisse")
n.ersetze('<section class="sek grund"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Fallstudie · Badsanierung</span>',
          '<section class="sek grund" id="ergebnisse"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Die Ergebnisse</span>')
n.ersetze('<span class="nr" data-zahl="14">14</span><span class="fz-einheit">Bad-Anfragen</span></div><p>Daraus sieben Termine vor Ort und nach 18 Tagen der erste Auftrag.</p>',
          '<span class="nr" data-zahl="37">37</span><span class="fz-einheit">Bad-Anfragen</span></div><p>Daraus zwölf Termine vor Ort, der erste Auftrag über 10.000 € war nach 18 Tagen unterschrieben.</p>')  # Stand wie Startseite (37 / 12)
# Noah, 22.11.2026: „nicht Vorarbeiter, sonst einfach andere Möglichkeiten“ + „dass sich mehr Leute eintragen, wenn es persönlich ist“
n.ersetze('Es hilft, weil ein Kunde vor einem großen Auftrag wissen will, wen er sich ins Haus holt. Pflicht ist es nicht — es geht auch mit deinem Vorarbeiter.',
          'Es hilft, weil sich mehr Leute eintragen, wenn es persönlich ist. Pflicht ist es nicht: Es geht auch mit deinem Team oder nur mit Bildern und Filmen von eurer Arbeit.', 2)
n.ersetze('Sein Argument: Werbung macht man nicht erst, wenn es schlechter läuft, sondern damit man dann schon bekannt ist.',
          'Sein Argument: Wer erst wirbt, wenn es schlechter läuft, ist dann noch nicht bekannt.', 2)
# Schlicht wie die Startseite (Noah, 19.11.2026): Hero → Was wir übernehmen → Ergebnis-Karten → Stimmen → Fragen → Kontakt
n.heraus('<section class="sek grund" id="ergebnisse">')
n.nach('<section class="hero-klein">',
       ablauf_animiert("neukundengewinnung", 'Die Anzeigen übernehmen wir.', [
           ("Die Anzeige mit deinen Leuten", "Man erkennt den Betrieb aus dem Nachbarort, deshalb bleibt sie im Feed hängen."),
           ("Nur 25 Kilometer um deinen Betrieb", "Wer 60 Kilometer weiter ein Projekt plant, sieht sie nicht."),
           ("Vier Filterfragen vor jeder Anfrage", "Bei dir kommt an, wer sein Projekt ernst meint, mit Name und Nummer.")])
       + erg_karten("Bad-Anfragen"))
n.vor('<section class="sek faq">', STIMMEN)
fertig(n, "neukundengewinnung", hero_unter("neukundengewinnung"))

# ── 6 · Mitarbeitergewinnung
m = unterseite("mitarbeitergewinnung")
einfach(m, 'Die Guten suchen nicht, also bringen wir deine Stelle dorthin, wo sie jeden Abend sind.', ('Fallstudie · Anlagenmechaniker SHK',),
        fragen_lead='Was es kostet, wie lange es dauert und was du selbst dafür tun musst.')
hero_knopf(m, "/websites/#arbeiten", "#ergebnisse")
m.ersetze('<section class="sek grund"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Fallstudie · Anlagenmechaniker SHK</span>',
          '<section class="sek grund" id="ergebnisse"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Die Ergebnisse</span>')
m.heraus('<section class="sek grund" id="ergebnisse">')
m.nach('<section class="hero-klein">',
       ablauf_animiert("mitarbeitergewinnung", 'Die Suche übernehmen wir.', [
           ("Deine Mannschaft in der Anzeige", "Sie läuft abends auf Instagram und Facebook, wo die Fachkräfte ohnehin sind."),
           ("Nur 30 Kilometer um deinen Betrieb", "Wer 90 Kilometer weg wohnt, sieht sie nicht."),
           ("Bewerbung in zwei Minuten", "Vier Filterfragen statt Anschreiben und Lebenslauf, du rufst nur noch an.")]))

# Die Reihe geht im selben Muster weiter (Noah, 21.11.2026: „die oben sollst du genauso lassen … dass wir das einfach so weiterspielen,
# Kirchner, Planung Hindelang, Autohaus Ressle, HAWE Engineering“): Klaß als dritter Block, dann abwechselnd gespiegelt.
# Zahlen nur mit Beleg (Chat-Doku hwm-website-ueberarbeitung.md „Zahlen mit Quelle“): Klaß 35/16, Kirchner 25/16, Ressle 14 selbst
# nachgezählt, HAWE „über 100 in 4 Wochen“ (Recherche Drive); Hindelang 12 (Pool-D1 hwm-pool, funnel 69e117fde66be169b9109746, 27.04.–07.06.2026; Noah, 23.11.2026: „wieso sind bei hindelang nicht die bewerbung mit großer zahl aufgelistet“).
# Logo zu jedem Ergebnis (Noah, 21.11.2026 abends: „überall die logos dazu“, dann „logos kleiner … und unter den normalen namen“):
# Farblogo ohne Kasten UNTER dem Betriebsnamen, optisch gleich groß (gleiche Fläche im Rahmen 112 × 44, flache 140 breit).
# Klaß und HAWE gibt es nur weiß → in Tinte eingefärbt (logos/farbe/klass.png, hawe.png).
def senft_marke(k):
    from PIL import Image as _Im
    _w, _h = _Im.open(WURZEL / f"static/assets/img/logos/farbe/{k}.png").size
    _r = _w / _h
    _RB, _RH, _FL = 112, 44, 3000
    if _r > 4: _RB = 140   # sehr flache Schriftzüge (Klaß) breiter, sonst winzig
    lb = min((_FL * _r) ** .5, _RB); lh = lb / _r
    if lh > _RH:
        lh = _RH; lb = lh * _r
    return (f'<span class="senft-marke"><img loading="lazy" src="/static/assets/img/logos/farbe/{k}.png" alt="" '
            f'width="{round(lb)}" height="{round(lh)}" decoding="async"></span>')


def _folge(nr, kicker, h2, bild, alt, zahl=None, einheit="", lead="", pos="50% 45%", logo=None, dunkel=False, marke=None):
    gespiegelt = " gespiegelt" if nr % 2 == 0 else ""
    if logo:
        fig = (f'<figure class="senft-bild senft-logo{" dunkel" if dunkel else ""} reveal"><img src="{logo}" alt="{alt}" loading="lazy" decoding="async"></figure>')
    else:
        fig = (f'<figure class="senft-bild reveal"><img src="{bild}" alt="{alt}" loading="lazy" decoding="async" style="object-position:{pos}"></figure>')
    z = f'<p class="senft-zahl"><b>{zahl}</b><span>{einheit}</span></p>' if zahl else ''
    return (f'<div class="wrap senft-raster folge{gespiegelt}">{fig}<div class="senft-text reveal"><span class="kicker">{kicker}</span>'
            f'{z}<h2>{h2}</h2>' + (f'<p class="lead">{lead}</p>' if lead else '') + (senft_marke(marke) if marke else '') + '</div></div>')


FOLGE_BLOECKE = "".join([
    _folge(3, "Heizung-Sanitär Klaß in Türkenfeld", "Für den Obermonteur.", "/static/assets/img/_h1280/fall/klass-team.webp",
           "Zwei Monteure von Heizung-Sanitär Klaß vor dem Firmenwagen", "35", "Bewerbungen", "16 davon mit Erfahrung im Fach.", pos="70% 40%", marke="klass"),
    _folge(4, "Kirchner in Thaining am Ammersee", "Für die offene Stelle.", "/static/assets/fv/g/ki-team-1800.webp",
           "Das Team von Kirchner Thaining vor einem Container", "25", "Bewerbungen", "16 davon mit passendem Führerschein.", pos="50% 40%", marke="kirchner"),
    # Fotos statt Logo (Noah, 21.11.2026: „bei planung hindelang nimmst einfach das bild von ihm … ohne creative“,
    # „autohaus ressle hatten wir ja auch die bilder und hawe auch“) – Originale aus dem Drive des Kunden
    # Noah, 21.11.2026 abends: „bei hindelang das bild von der baustelle“, „bei ressle nehmen wir das bild vom servicetechniker“
    _folge(5, "Planung Hindelang", "Für die Stelle als Planer.", "/static/assets/img/_h1280/fall/hindelang-baustelle.webp",
           "Alexander Hindelang mit dem 3D-Laserscanner im Dachstuhl einer Baustelle", zahl="12", einheit="Bewerbungen", lead="Die Anzeige lief auf Facebook und Instagram, mit eigener Bewerbungsseite.", pos="55% 40%", marke="hindelang"),
    _folge(6, "Autohaus Ressle", "Für die offene Stelle.", "/static/assets/img/_h1280/fall/ressle-servicetechniker.webp",
           "Servicetechniker von Autohaus Ressle unter einem Fahrzeug auf der Hebebühne", zahl="14", einheit="Bewerbungen", pos="40% 45%", marke="autohaus-ressle"),
    _folge(7, "HAWE Engineering", "Für die offene Stelle.", "/static/assets/img/_h1280/fall/hawe-inhaber.webp",
           "Der Inhaber von HAWE Engineering am Arbeitsplatz", zahl="100+", einheit="Bewerbungen", lead="In nur vier Wochen.", pos="50% 45%", marke="hawe"),
])
# Senftleben groß (Noah, 18.11.2026: „in 18 [Tagen] Stelle besetzt … die kannst du auch groß machen … mit der Buchhaltung“), Zahlen wie SHK-Seite
SENFT_SEK = ('<section class="sek senft-sek" id="ergebnisse"><div class="wrap senft-raster"><figure class="senft-bild reveal"><img src="/static/assets/img/_h1280/fall/senftleben-team.webp" '
             'alt="Das Team von Senftleben Haustechnik vor den Firmenwagen in Ehingen" loading="lazy" decoding="async"></figure>'
             '<div class="senft-text reveal"><span class="kicker">Senftleben Haustechnik in Ehingen</span>'
             '<p class="senft-zahl"><b>18</b><span>Tage</span></p><h2>Bis die Stelle besetzt war.</h2>'
             '<p class="lead">21 qualifizierte Bewerbungen sind gekommen.</p>' + senft_marke("senftleben") +
             '</div></div>'
             # Erwin Schmidt darunter (Noah, 21.11.2026: „dann darunter noch erwin schmidt - da hats ja auch nicht soo lange gedauert“);
             # Zahlen wie auf der SHK-Seite (25 Bewerbungen, Stelle in 4 Wochen besetzt), Foto ohne Meike (Noah, 20.11.2026)
             '<div class="wrap senft-raster gespiegelt"><figure class="senft-bild reveal"><img src="/static/assets/img/_h1280/fall/ess-zwei-monteure.webp" '
             'alt="Zwei Monteure von Erwin Schmidt &amp; Sohn in der Ausstellung in Sindelfingen" loading="lazy" decoding="async" style="object-position:50% 25%"></figure>'
             '<div class="senft-text reveal"><span class="kicker">Erwin Schmidt &amp; Sohn in Sindelfingen</span>'
             '<p class="senft-zahl"><b>4</b><span>Wochen</span></p><h2>Bis die Stelle besetzt war.</h2>'
             '<p class="lead">25 Bewerbungen sind gekommen.</p>' + senft_marke("ess") +
             '</div></div>'
             + FOLGE_BLOECKE + '</section>'
             '<style>.senft-raster.gespiegelt,.senft-raster.folge{margin-top:clamp(56px,7vw,110px)}.senft-logo{display:flex;align-items:center;justify-content:center;background:var(--papier);border:1px solid rgba(22,19,14,.1);padding:clamp(28px,5vw,72px)}.senft-bild.senft-logo img[src*=hindelang]{width:min(38%,190px)}.senft-logo.dunkel{background:var(--tinte);border-color:transparent}.senft-bild.senft-logo img{width:min(70%,360px);height:auto;object-fit:contain}@media (min-width:901px){.senft-raster.gespiegelt{grid-template-columns:minmax(0,.85fr) minmax(0,1.15fr)}.senft-raster.gespiegelt .senft-bild{order:2}}'
             '.senft-raster{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:clamp(28px,4vw,72px);align-items:center}'
             '.senft-bild{margin:0;border-radius:var(--radius);overflow:hidden;aspect-ratio:4/3}.senft-bild img{width:100%;height:100%;object-fit:cover;object-position:50% 45%;display:block}'
             '.senft-text{min-width:0}.senft-marke{display:flex;align-items:center;height:44px;margin:26px 0 0}.senft-marke img{display:block;max-width:140px;max-height:44px}.senft-zahl{display:flex;flex-wrap:wrap;align-items:baseline;gap:0 .25em;margin:14px 0 6px;line-height:.9}.senft-zahl b{font-size:clamp(96px,13vw,200px);font-weight:800;letter-spacing:-.05em;color:var(--bronze-tief,#8F5B1D)}'
             '.senft-zahl span{font-size:clamp(28px,3vw,44px);font-weight:700;letter-spacing:-.02em}.senft-text h2{margin:0 0 12px;max-width:24ch;font-size:clamp(28px,2.8vw,42px);line-height:1.12}.senft-text h2::before{display:none}'
                          '@media (max-width:900px){.senft-raster{grid-template-columns:1fr}}</style>')
# Noah, 20.11.2026: „da wollen wir nicht unbedingt Meike drin haben … Klaß und Senftleben“ → Erwin Schmidt raus
m.nach('<section class="sek band auf-dunkel bento-sek ablauf-ani">', SENFT_SEK)
m.vor('<section class="sek faq">', STIMMEN)
# „Fragen, die fast jeder Betrieb vorher stellt … kannst du erst mal ausmachen“ (Noah, 20.11.2026)
m.heraus('<section class="sek faq">')
fertig(m, "mitarbeitergewinnung", hero_unter("mitarbeitergewinnung"))

# Design-Tor am Ende jedes Live-Baus (Noah, 21.11.2026: „schau dir wirklich an, was im code falsch ist, dass er es nicht checkt“):
# misst die gerenderten Seiten (Kartenreihen bündig, kein Leerraum in Karten, Handy ohne Überlauf, h2 ≤ 2 Zeilen). Rot = Exit 1.
# Der pre-commit-Hook in firma/website sperrt zusätzlich jeden Commit mit rotem Tor.
if LIVE and "--ohne-tor" not in sys.argv:
    import subprocess as _sp
    _r = _sp.run(["node", "hwm_live_tor.mjs"], cwd="/Users/noahs/CEO-GPT/system/apps/audit")
    if _r.returncode != 0:
        sys.exit("❌ Design-Tor rot — Seiten gebaut, aber so nicht committen (Befunde oben).")

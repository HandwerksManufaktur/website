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
        self.h = self.h.replace('</head>', '<style>/* Entwurf: Tap-Ziele im Fuß mindestens 44 px breit */.fuss ul a,.fuss .unten a{min-width:44px}.lg-buehne li span b,.pb-marke,.ab-leiste span,.lang-marke,.pb-karte b,.fsz-legende span,.kal-fuss span,.kal-fuss b,.rg-lese,.pb-adr span,.pb-menue span,.pb-ruf,.pb-ok{letter-spacing:.01em!important}.ab-zoom{transition-duration:.4s!important}'
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
                                    '@media (max-width:900px){.dsk-br{display:none}}' + KONTAKT_STIL + KARTEN_STIL + '</style></head>', 1)

    def schreibe(self, pfad):
        # Sperren (Noah, 15.11.2026): kein Kicker mit Mittelpunkt, keine alte Kundenzahl, keine Bewertungszeile unter den Stimmen
        assert not re.findall(r'<span class="kicker">[^<]*·[^<]*</span>', self.h), (pfad, re.findall(r'<span class="kicker">[^<]*·[^<]*</span>', self.h))
        assert "130 Betriebe" not in self.h and 'class="zusammen' not in self.h, pfad
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


# ── 1 · Startseite ────────────────────────────────────────────────────────────────────────────────
s = Seite(LIVE_START)
s.ersetze('<h1><span class="w">Mehr Aufträge.</span> <span class="w">Mehr Bewerber.</span> <span class="w">Aus deinem Umkreis.</span></h1>',
          '<h1><span class="w">Dein Handwerk.</span> <span class="w">Unsere Baustelle.</span></h1>')  # Noah, 15.11.2026: „genau passend, ist perfekt“
s.ersetze('<p class="lead">Website, Fotos und Social-Media-Werbung für Handwerksbetriebe.</p>',
          '<p class="lead">Über 150 Betriebe arbeiten mit uns. Wir bauen deine Website und bringen dir Kunden und Mitarbeiter aus deinem Umkreis.</p>')
# Aufbau wie shk…/start-neu/: Firma → drei Leistungen (einfache Karten) → Ergebnisse → Stimmen → Team → Kontakt.
# Die drei Säulen in Logo-Form stehen schon im Hero und kommen hier nicht noch einmal (Noah, 14.11.2026);
# Problem-Szenen, Google-Mechanik und Foto-Band stehen auf den Unterseiten.
s.heraus('<section class="sek system-sek" id="system"')
s.heraus('<section class="sek grund lagen-sek probleme pb-sek">')
s.heraus('<section class="sek google grund">')
s.heraus('<section class="sek band auf-dunkel" id="videos">')
PFEIL = '<svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'


def karte(bild, alt, pos, titel, zeile, text, ziel, knopf):
    return (f'<article class="erg reveal"><div class="erg-film"><img src="/start-neu/bilder/{bild}.webp" alt="{alt}" loading="lazy" decoding="async" style="object-position:{pos}"></div>'
            f'<div class="erg-in"><div class="erg-zeile"><em>{titel}</em><span>{zeile}</span></div><p>{text}</p>'
            f'<a class="textlink" href="/{ziel}/">{knopf} {PFEIL}</a></div></article>')


LEISTUNGS_SEK = ('<section class="sek leistungen-sek" id="system"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Unsere Leistungen</span>'
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
NOAH_TEXT = "Servus, ich bin Noah, Gründer der Handwerksmanufaktur. Dass wir nur fürs Handwerk arbeiten, kommt nicht von ungefähr. Meine drei Brüder haben alle im Handwerk gelernt. Zwei davon sind Meister. Zusätzlich haben wir in der Familie gleich mehrere Handwerksbetriebe. So habe ich schon von klein auf mitgekriegt, wie es im Handwerk zugeht. In den letzten 8 Jahren haben wir über 150 Firmen betreut und kennen ganz genau, wie ein Handwerksbetrieb an Aufträge und gute Mitarbeiter kommt."
s.ersetze('<span class="kicker">Wer dahinter steht</span><h2>Die Leute hinter deinem Auftritt.</h2><p class="lead">Dieselben Leute von Anfang bis Ende.</p>',
          f'<span class="kicker">Über uns</span><h2>Seit 2019 nur fürs Handwerk.</h2><p class="lead">{NOAH_TEXT}</p>')


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
                 ('<h2>77 Kundenseiten stehen auf Seite 1.</h2>', '<h2>77-mal Richtfest.</h2><p class="lead">77 Kundenseiten stehen bei Google auf Seite 1.</p>')],
    "foto-video": [('<h1>Fotos, auf denen man deinen Betrieb wiedererkennt.</h1>', '<h1>Wir setzen dein Handwerk ins Licht.</h1>'),
                 ('<h2>Den Drehtag übernehmen wir.</h2>', '<h2>Vom ersten Bild bis zum fertigen Film.</h2>'),
                 ('<h2>Diese Filme sind am Drehtag entstanden.</h2>', '<h2>Abgedreht.</h2>')],
    "neukundengewinnung": [('<h1>Die Aufträge, die du willst. Nur für deinen Betrieb.</h1>', '<h1>Wir füllen dein Auftragsbuch.</h1>'),
                 ('<h2>Die Anzeigen übernehmen wir.</h2>', '<h2>Von der Anzeige bis zum Aufmaß.</h2>'),
                 ('<h2>„Dass so schnell so viele Anfragen kommen, hätte ich nicht gedacht.“</h2>', '<h2>Schwarz auf weiß.</h2><p class="lead">„Dass so schnell so viele Anfragen kommen, hätte ich nicht gedacht.“</p>')],
    "mitarbeitergewinnung": [('<h1>Leute, die bei dir anfangen wollen. Aus deinem Umkreis.</h1>', '<h1>Verstärkung ist unterwegs.</h1>'),
                 ('<h2>Die Suche übernehmen wir.</h2>', '<h2>Von der Anzeige bis zum Handschlag.</h2>'),
                 ('<h2>„Wir haben nur nicht gedacht, dass es so viele sind.“</h2>', '<h2>25 Bewerbungen. 4 Wochen. 1 Neuer.</h2><p class="lead">„Wir haben nur nicht gedacht, dass es so viele sind.“</p>')],
}


def fertig(seite, slug):
    ergebnisse_aktuell(seite)
    for alt, neu in FASSUNG.get(slug, []):
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
fertig(w, "websites")

# ── 3 · Suchmaschinenoptimierung
g = unterseite("suchmaschinenoptimierung")
einfach(g, 'Dein nächster Kunde tippt dein Gewerk und deinen Ort ein und ruft den an, der oben steht.', ('Nachgemessen, nicht behauptet',),
        fragen_lead='Wie lange es dauert und ob es auch in der Großstadt geht.')
hero_knopf(g, "/websites/#arbeiten", "#ergebnisse")
g.ersetze('<section class="sek grund rangliste-sek"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Nachgemessen, nicht behauptet</span><h2>Wo unsere Kunden bei Google wirklich stehen.</h2>',
          '<section class="sek grund rangliste-sek" id="ergebnisse"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Die Ergebnisse</span><h2>77 Kundenseiten stehen auf Seite 1.</h2>')
g.nach('<section class="hero-klein">',
       problem('Der Wettbewerber steht vor dir.',
               ['Heizung, Bad und Wartung stehen auf einer Seite. Gefunden wird davon nichts.', 'Das Google-Profil ist nicht gepflegt.', 'Die Seite lädt am Handy vier Sekunden und rutscht ab.'],
               ['Jede Leistung hat ihre eigene Seite mit Ort.', 'Dein Google-Profil ist aufgebaut und gepflegt.', 'Die Seite lädt schnell, auch am Handy.'])
       + uebernehmen('Den Weg nach vorn übernehmen wir.', [
           ('u-leistung-ort', 'Haus mit Photovoltaik-Anlage von Wohner Elektrotechnik aus der Luft', '50% 50%', 'Die Seiten', 'Eine je Leistung, mit Ort.', '„Badsanierung Landsberg“ bekommt eine eigene Seite.'),
           ('u-profil', 'Dach mit Blecheindeckung von Dachbau Kraus', '50% 50%', 'Das Google-Profil', 'Aufgebaut und gepflegt.', 'Mit Leistungen und Fotos, damit dich die Karte zeigt.'),
           ('u-bewertung', 'Handschlag auf dem Hof von Kirchner in Thaining', '50% 30%', 'Die Bewertungen', 'Sie kommen von selbst.', 'Ein Link nach jedem Auftrag, der Rest läuft.')]))
g.vor('<section class="sek faq">', STIMMEN)
fertig(g, "suchmaschinenoptimierung")

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
       problem('Stockfotos wie überall. Der Anruf geht zum Nächsten.',
               ['„Aktuelle Fotos haben wir keine“, hören wir fast in jedem Erstgespräch.', 'Auf der Seite stehen Katalogbilder.', 'Wer vergleicht, erkennt deinen Betrieb nicht wieder.'],
               ['Auf den Bildern stehen deine Leute vor deinen Fahrzeugen.', 'Fotografiert wird im laufenden Betrieb.', 'Alle Fotos und Filme gehören dir, in voller Auflösung.'])
       + uebernehmen('Den Drehtag übernehmen wir.', [
           ('u-motivliste', 'Zwei Männer im Büro von HAWE Engineering', '50% 30%', 'Die Motivliste', 'Vorher am Telefon.', 'Wir klären, was Website und Anzeigen brauchen, und haken die Liste am Drehtag ab.'),
           ('u-drehtag', 'Zwei Männer an der Laseranlage bei Allplast', '50% 30%', 'Der Drehtag', 'Ein Tag bei dir.', 'Wir fotografieren und filmen, was bei dir ohnehin passiert, und dein Betrieb läuft weiter.'),
           ('u-uebergabe', 'Zwei Mitarbeiter in der Fertigung von SD Hirsch', '50% 30%', 'Die Übergabe', 'Alles gehört dir.', 'Du bekommst alle Fotos und Filme in voller Auflösung.')]))
fertig(f, "foto-video")

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
fertig(n, "neukundengewinnung")

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
fertig(m, "mitarbeitergewinnung")

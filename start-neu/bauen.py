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
LIVE_START = (WURZEL / "index.html").read_text()


class Seite:
    def __init__(self, quelle):
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

    def entwurf(self):
        """noindex + alle Links auf Start und die fünf Leistungen in den Entwurf."""
        self.ersetze('<meta name="robots" content="index,follow">', '<meta name="robots" content="noindex, nofollow, noarchive">')
        self.h = re.sub(r'href="/(#[^"]*)?"', lambda m: f'href="/start-neu/{m.group(1) or ""}"', self.h)
        self.h = re.sub(r'href="/(%s)/' % "|".join(LEISTUNGEN), r'href="/start-neu/\1/', self.h)

    def schreibe(self, pfad):
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
          '<h1><span class="w">Der Partner für</span> <span class="w">Handwerksbetriebe.</span></h1>')
s.ersetze('<p class="lead">Website, Fotos und Social-Media-Werbung für Handwerksbetriebe.</p>',
          '<p class="lead">Über 130 Betriebe arbeiten mit uns. Wir bauen deine Website, machen Fotos und Videos bei dir im Betrieb und schalten Anzeigen für Kunden und Mitarbeiter.</p>')
# Aufbau: Leistungen direkt nach den Logos, Problem-Szenen raus (stehen jetzt auf den Unterseiten)
leistungen = s.heraus('<section class="sek system-sek" id="system"')
s.vor('<section class="sek grund lagen-sek probleme pb-sek">', leistungen)
s.heraus('<section class="sek grund lagen-sek probleme pb-sek">')
s.entwurf()
s.schreibe(HIER / "index.html")


def unterseite(slug):
    return Seite((WURZEL / slug / "index.html").read_text())


def hero_knopf(seite, alt_href, neu_href, text="Ergebnisse ansehen"):
    seite.ersetze(f'<a class="btn btn-umriss" href="{alt_href}">Arbeiten ansehen</a>',
                  f'<a class="btn btn-umriss" href="{neu_href}">{text}</a>')


# ── 2 · Websites: Problem (Google, Seite 3) → Aufbau → Ablauf → Seiten → Gewerke → Stimmen → Fragen → Kontakt
w = unterseite("websites")
w.nach('<section class="hero-klein">', szene(0, "Kennst du das?", "Gute Arbeit, aber keiner findet dich."))
w.ersetze('<section class="sek grund aufbau-sek">', '<section class="sek aufbau-sek">')
w.ersetze('<span class="kicker">Aufbau einer Seite</span>', '<span class="kicker">Was die Seite dagegen tut</span>')
ablauf = w.heraus('<section class="sek"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">So läuft es ab</span>')
w.nach('<section class="sek aufbau-sek">', ablauf.replace('<section class="sek">', '<section class="sek grund">', 1))
w.vor('<section class="sek faq">', STIMMEN)
w.ersetze('<span class="kicker">Bevor du weiterliest</span>', '<span class="kicker">Wenn deine Seite mehr bringen soll</span>')
w.entwurf()
w.schreibe(HIER / "websites" / "index.html")

# ── 3 · Suchmaschinenoptimierung: Aufbau trägt den Faden schon (Problem → Was wir machen → Plätze → Fragen)
g = unterseite("suchmaschinenoptimierung")
hero_knopf(g, "/websites/#arbeiten", "#ergebnisse")
g.ersetze('<section class="sek grund rangliste-sek">', '<section class="sek grund rangliste-sek" id="ergebnisse">')
g.entwurf()
g.schreibe(HIER / "suchmaschinenoptimierung" / "index.html")

# ── 4 · Foto & Video: Problem (Vergleich, Stockfoto) → Drehtag → Filme → Fotos → Betriebe → Fragen → Kontakt
f = unterseite("foto-video")
hero_knopf(f, "/websites/#arbeiten", "#ergebnisse", "Arbeiten ansehen")
f.ersetze('<section class="sek band auf-dunkel">', '<section class="sek band auf-dunkel" id="ergebnisse">')
drehtag = f.heraus('<section class="sek"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">So läuft der Drehtag</span>')
f.nach('<section class="hero-klein">', szene(1, "Der Kunde vergleicht", "Stockfotos wie überall. Der Anruf geht zum Nächsten.") + drehtag)
f.entwurf()
f.schreibe(HIER / "foto-video" / "index.html")

# ── 5 · Neukundengewinnung: Faden steht (Problem → Mechanik → Ablauf → Fallstudie → Werktage → Fragen)
n = unterseite("neukundengewinnung")
hero_knopf(n, "/websites/#arbeiten", "#ergebnisse")
n.ersetze('<section class="sek grund"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Fallstudie',
          '<section class="sek grund" id="ergebnisse"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Fallstudie')
n.entwurf()
n.schreibe(HIER / "neukundengewinnung" / "index.html")

# ── 6 · Mitarbeitergewinnung: Problem (vier Wege) + Szene Bewerber → Mechanik → Ablauf → Fallstudie → …
m = unterseite("mitarbeitergewinnung")
hero_knopf(m, "/websites/#arbeiten", "#ergebnisse")
m.ersetze('<section class="sek grund"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Fallstudie',
          '<section class="sek grund" id="ergebnisse"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Fallstudie')
m.nach('<section class="sek leiter-sek">', szene(3, "Und wenn doch einer nachschaut", "Kein Team, keine Stelle, kein Weg zur Bewerbung."))
m.entwurf()
m.schreibe(HIER / "mitarbeitergewinnung" / "index.html")

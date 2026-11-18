"""Pilot „roter Faden“ für /neukundengewinnung/ (Noah, 19.11.2026: „Die Unterseiten, die sind noch nicht geil. Da zieht sich
noch kein roter Faden durch, keine rote Linie.“).

Befund: Jede Unterseite stapelt dieselben losen Blöcke (Hero → Problem → drei Karten → Ergebnisse → Stimmen → Fragen →
Kontakt), jeder mit eigenem Kicker, eigener Bauform und eigener Hintergrundfarbe, ohne Bezug zum Block davor.
Pilot: EINE Geschichte entlang des Wegs, den eine Anfrage nimmt (Anzeige → Filterfragen → Anfrage → Termin vor Ort →
Auftrag, danach „Der Name bleibt“ und das Ziel Kontakt). Die vorhandenen Inhalte werden in diese Kapitel einsortiert:
Problem-Zeilen zeigen auf das Kapitel, das sie löst; jede Frage aus dem FAQ steht in dem Kapitel, in dem sie sich stellt;
die Zahlen der Betriebe stehen an der Station, an der sie entstanden sind. Eine Bronze-Linie (static: start-neu/roter-faden/
faden.css + faden.js) verbindet die Kapitelmarken und zeichnet sich beim Scrollen bis zur Bildmitte.

Sicherheit: bauen.py wird NICHT verändert. Dieses Skript führt bauen.py (Entwurfsmodus) im Speicher aus, fängt alle
Schreibzugriffe ab (nichts landet auf der Platte), nimmt die fertige Entwurfsseite Neukundengewinnung und baut daraus
start-neu/roter-faden/neukundengewinnung/index.html (noindex). Live-Dateien bleiben unberührt.
Zahlen: nur, was schon auf der Website steht (Neukundengewinnung + Fallstudien-Karten der Startseite).
Aufruf: /Users/noahs/CEO-GPT/.venv/bin/python start-neu/roter_faden.py
"""
import contextlib
import io
import re
import runpy
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
ZIEL = HIER / "roter-faden" / "neukundengewinnung" / "index.html"
V = "1"


def entwurf_erfassen():
    """bauen.py im Entwurfsmodus ausführen, ohne dass eine Datei geschrieben wird; liefert {Pfad: HTML}."""
    erfasst = {}
    alt_schreiben, alt_mkdir, alt_argv = Path.write_text, Path.mkdir, sys.argv
    Path.write_text = lambda self, d, *a, **k: erfasst.__setitem__(str(self), d) or len(d)
    Path.mkdir = lambda self, *a, **k: None
    sys.argv = [str(HIER / "bauen.py")]
    sys.path.insert(0, str(HIER))
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(str(HIER / "bauen.py"), run_name="roter_faden_erfassen")
    finally:
        Path.write_text, Path.mkdir, sys.argv = alt_schreiben, alt_mkdir, alt_argv
    return erfasst


def bereich(h, anfang):
    """(start, ende) der <section>, die mit `anfang` beginnt, verschachtelte <section> mitgezählt."""
    assert h.count(anfang) == 1, (anfang, h.count(anfang))
    a = h.index(anfang)
    tiefe = 0
    for m in re.compile(r"<section\b|</section>").finditer(h, a):
        tiefe += 1 if m.group() == "<section" else -1
        if tiefe == 0:
            return a, m.end()
    raise AssertionError(anfang)


def frage(h, text):
    """Antwort einer FAQ-Frage im Wortlaut der Seite."""
    m = re.search(r'<summary>%s<span class="plus">.*?</summary><p>(.*?)</p>' % re.escape(text), h, re.S)
    assert m, text
    return m.group(1)


PFEIL = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
BRIEF = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>'
SIGNET = ('<svg viewBox="0 0 83 91" aria-hidden="true"><path d="M0,39.667 L22,25 L22,91 L0,91 Z"/>'
          '<path d="M34,14.667 L56,0 L56,91 L34,91 L34,64.67 L27,68 L27,53.667 L34,49 Z"/><path d="M61,14.667 L83,0 L83,91 L61,91 Z"/></svg>')
LOGO = {"senftleben": ('/static/assets/img/logos/logo-senftleben-haustechnik.png', True),
        "sussmann": ('/static/assets/img/logos/logo-sussmann-gmbh.png', False),
        "goldacker": ('/static/assets/img/logos/logo-goldacker.png', True),
        "stimpfle": ('/static/assets/img/logos/logo-yannick-stimpfle-logo.png', True)}


def logo(wer, alt):
    src, dunkel = LOGO[wer]
    return f'<span class="fz-logo{" dunkel" if dunkel else ""}"><img src="{src}" alt="{alt}" loading="lazy" decoding="async"></span>'


def marke(inhalt, art=""):
    return f'<span class="rf-marke{(" " + art) if art else ""}" aria-hidden="true">{inhalt}</span>'


def kopf(nr, kicker, h2, lead=""):
    m = marke(f"<b>{nr}</b>" if nr else "", "" if nr else "rf-ring")
    lead = f'<p class="lead">{lead}</p>' if lead else ""
    return f'<div class="rf-kopf">{m}<div class="rf-kopf-text reveal"><span class="kicker">{kicker}</span><h2>{h2}</h2>{lead}</div></div>'


def notiz(f, antwort):
    return f'<div class="rf-frage reveal"><span class="rf-frage-m">Das fragen fast alle</span><b>{f}</b><p>{antwort}</p></div>'


def station(klasse, sid, inhalt):
    i = f' id="{sid}"' if sid else ""
    return f'<section class="sek rf-station {klasse}"{i}><div class="wrap rf-wrap">{inhalt}</div></section>'


def baue(h):
    a_hero, e_hero = bereich(h, '<section class="hero-klein">')
    a_kontakt, e_kontakt = bereich(h, '<section class="sek umkreis-kontakt" id="kontakt">')
    mitte = h[e_hero:a_kontakt]
    # Bausteine aus der fertigen Seite (Wortlaut bleibt, nichts erfunden)
    a, e = bereich(mitte, '<section class="sek stimmen">')
    stimmen = mitte[a:e]
    bahnen = stimmen[stimmen.index('<div class="bahn"'):stimmen.rindex('</section>')]
    a, e = bereich(mitte, '<section class="sek grund" id="ergebnisse">')
    fall = mitte[a:e]
    absaetze = re.search(r'<div class="text"><div>(.*?)</div><blockquote>(.*?)<cite>(.*?)</cite></blockquote>', fall, re.S)
    p_fall, zitat, zitat_wer = absaetze.groups()
    p_fall = re.findall(r'<p>(.*?)</p>', p_fall, re.S)
    assert len(p_fall) == 2, p_fall
    video = re.search(r'<video controls[^>]*></video>', fall).group()
    video = video.replace('data-poster="', 'poster="', 1)
    for zahl in ('data-zahl="125000"', 'data-zahl="21"', 'data-zahl="10" data-nach="+"', 'data-zahl="37"', 'data-zahl="17"'):
        assert zahl in fall, zahl  # die Zahlen, die der Pilot zeigt, stehen auf der Seite
    f_kamera = frage(mitte, "Muss ich selbst vor die Kamera?")
    f_schnaeppchen = frage(mitte, "Kommen darüber nur Schnäppchenjäger?")
    f_erste = frage(mitte, "Wann kommt die erste Anfrage?")
    f_genug = frage(mitte, "Wir haben gerade genug zu tun. Lohnt sich das trotzdem?")
    f_kosten = frage(mitte, "Was kostet das?")
    zitat_filter = re.search(r'(„Mir kam es bis jetzt bei den Kunden vor Ort nicht so vor\.“)', f_schnaeppchen).group(1)
    f_schnaeppchen_kurz = f_schnaeppchen.split(" Benjamin Senftleben dazu")[0]
    assert "Aufmaß" in mitte and "Jede Anfrage gehört dir allein." in mitte

    # ── Vorher: die drei Probleme der Seite, jedes zeigt auf das Kapitel, das es löst ──
    zeilen = [("Empfehlungen kannst du nicht bestellen, wenn ein großes Projekt wegbricht.", "k1", "01", "Die Anzeige läuft nur 25 Kilometer um deinen Betrieb."),
              ("Auf der Vergabeplattform bekommt den Auftrag, wer am billigsten ist.", "k2", "02", "Vier Filterfragen stehen vor jeder Anfrage."),
              ("Im Lead-Portal geht dieselbe Anfrage an vier Betriebe gleichzeitig.", "k3", "03", "Jede Anfrage gehört dir allein.")]
    for heute, _, _, mit in zeilen:
        assert heute in mitte and mit in mitte, (heute, mit)
    vorher = station("rf-vorher", "", kopf("", "Vorher", "Drei Wochen voll, dann wieder Zufall.")
                     + '<div class="rf-tausch reveal"><div class="rf-tausch-kopf" aria-hidden="true"><span>Heute</span><span>Mit uns</span></div>'
                     + "".join(f'<div class="rf-tausch-zeile"><p class="rf-heute">{h_}</p><a class="rf-mit" href="#{sid}"><span class="rf-mit-nr">{nr}</span><span>{m_}</span></a></div>'
                               for h_, sid, nr, m_ in zeilen) + '</div>')

    # ── Fahrplan: der Weg einer Anfrage ──
    halte = [("k1", "01", "Die Anzeige"), ("k2", "02", "Die Filterfragen"), ("k3", "03", "Die Anfrage"), ("k4", "04", "Der Termin vor&nbsp;Ort"), ("k5", "05", "Der Auftrag")]
    fahrplan = station("rf-plan", "", '<div class="rf-kopf rf-kopf-plan"><div class="rf-kopf-text reveal"><span class="kicker">So läuft es</span>'
                       '<h2>Von der Anzeige bis zum Aufmaß.</h2><p class="lead">Fünf Stationen, und an jeder ein Betrieb, bei dem es genau so gelaufen ist.</p></div></div>'
                       '<ol class="rf-fahrplan reveal">' + "".join(f'<li><a href="#{sid}"><span>{nr}</span><b>{t}</b></a></li>' for sid, nr, t in halte) + '</ol>')

    # ── 01 Die Anzeige ──
    k1 = station("rf-k1", "k1", kopf("01", "Die Anzeige", "Deine Leute.<br> Im Feed von nebenan.")
                 + '<div class="rf-zwei"><div class="rf-text reveal"><p>Auf der Anzeige stehen deine Leute. Man erkennt den Betrieb aus dem Nachbarort, deshalb bleibt sie im Feed hängen.</p>'
                 '<p>Sie läuft nur 25 Kilometer um deinen Betrieb. Wer 60 Kilometer weiter ein Projekt plant, sieht sie nicht.</p>'
                 + notiz("Muss ich selbst vor die Kamera?", f_kamera) + '</div>'
                 '<figure class="rf-bild rf-bild-umkreis reveal"><img src="/start-neu/bilder/u-umkreis.webp" alt="Senftleben Haustechnik mit Team und Firmenwagen aus der Luft" width="1000" height="749" loading="lazy" decoding="async">'
                 '<figcaption class="rf-beleg"><span class="nr" data-zahl="125000" data-nach="">125000</span><span>Aufrufe im 25-km-Umkreis</span>'
                 '<small>Senftleben Haustechnik, Ehingen</small></figcaption></figure></div>')

    # ── 02 Die Filterfragen ──
    k2 = station("rf-k2", "k2", kopf("02", "Die Filterfragen", "Vier Fragen.<br> Dann erst die Anfrage.")
                 + '<div class="rf-zwei rf-zwei-text"><div class="rf-text reveal"><p>Vor jeder Anfrage stehen vier Filterfragen. Bei dir kommt an, wer sein Projekt ernst meint, mit Name und Nummer.</p></div>'
                 + notiz("Kommen darüber nur Schnäppchenjäger?", f_schnaeppchen_kurz) + '</div>'
                 f'<figure class="rf-zitat reveal"><blockquote>{zitat_filter}</blockquote><figcaption>{logo("senftleben", "Senftleben Haustechnik")}'
                 '<span><b>Benjamin Senftleben</b>Senftleben Haustechnik, Ehingen, nach zwei Monaten</span></figcaption></figure>')

    # ── 03 Die Anfrage ──  37 Briefe von Sussmann, 12 davon führen weiter in Kapitel 04
    briefe = "".join(f'<i class="{"hervor" if i < 12 else ""}" style="--i:{i}">{BRIEF}</i>' for i in range(37))
    k3 = station("rf-k3", "ergebnisse", kopf("03", "Die Anfrage", "Name, Nummer, Projekt.<br> Nur bei dir.")
                 + '<div class="rf-zwei rf-zwei-anfrage"><div class="rf-postfach reveal"><div class="rf-postfach-kopf">' + logo("sussmann", "Erich Sussmann GmbH")
                 + '<span><b>Erich Sussmann GmbH</b>Kirchheim, Badsanierung, in zwei Monaten</span></div>'
                 f'<p class="rf-gross"><span class="nr" data-zahl="37">37</span><span>Bad-Anfragen</span></p><div class="rf-briefe" aria-hidden="true">{briefe}</div>'
                 '<p class="rf-legende"><span><i></i>37 Bad-Anfragen</span><span><i class="hervor"></i>12 davon mit Termin vor Ort</span></p></div>'
                 '<div class="rf-text"><p class="reveal">Im Lead-Portal geht dieselbe Anfrage an vier Betriebe gleichzeitig. Bei uns gehört jede Anfrage dir allein.</p>'
                 '<div class="rf-betriebe reveal">'
                 f'<div class="rf-betrieb">{logo("goldacker", "Goldacker Gebäudetechnik")}<div><p class="rf-mittel"><span class="nr" data-zahl="17">17</span> Wärmepumpen-Anfragen</p>'
                 '<small>Goldacker Gebäudetechnik, Schöngeising. Jede mit Name, Nummer und Angaben zum Haus, direkt im Postfach des Betriebs.</small></div></div>'
                 f'<div class="rf-betrieb">{logo("stimpfle", "Stimpfle Sanitär und Heizung")}<div><p class="rf-mittel"><span class="nr" data-zahl="7">7</span> Bad-Anfragen</p>'
                 '<small>Stimpfle Sanitär &amp; Heizung, Stadtbergen. In den ersten drei Tagen, die Anzeigen laufen seit dem 29. Oktober.</small></div></div></div>'
                 + notiz("Wann kommt die erste Anfrage?", f_erste) + '</div></div>')

    # ── 04 Der Termin vor Ort ──
    termine = [("sussmann", "Erich Sussmann GmbH", "12", "", "Termine vor Ort", "Erich Sussmann GmbH, aus 37 Bad-Anfragen in zwei Monaten."),
               ("senftleben", "Senftleben Haustechnik", "10", "+", "Vor-Ort-Termine", "Senftleben Haustechnik, aus 21 Bad-Anfragen in zwei Monaten."),
               ("stimpfle", "Stimpfle Sanitär und Heizung", "3", "", "Vor-Ort-Termine", "Stimpfle Sanitär &amp; Heizung, in den ersten drei Tagen.")]
    k4 = station("rf-k4", "k4", kopf("04", "Der Termin vor Ort", "Du fährst hin.<br> Du misst auf.")
                 + '<div class="rf-zwei rf-zwei-termin"><figure class="rf-bild reveal"><img src="/start-neu/bilder/stimpfle-werkstatt.webp" alt="Das Team von Stimpfle Sanitär und Heizung in der Werkstatt" width="1000" height="667" loading="lazy" decoding="async">'
                 '<figcaption>Stimpfle Sanitär &amp; Heizung in Stadtbergen</figcaption></figure>'
                 '<div class="rf-text"><p class="reveal">Aus der Anfrage wird ein Termin beim Kunden. Ab hier bist du dran: hinfahren, anschauen, aufmessen.</p><ul class="rf-termine reveal">'
                 + "".join(f'<li>{logo(w, alt)}<p class="rf-mittel"><span class="nr" data-zahl="{z}" data-nach="{n}">{z}{n}</span> {e}</p><small>{t}</small></li>'
                           for w, alt, z, n, e, t in termine) + '</ul></div></div>')

    # ── 05 Der Auftrag ──  Sussmann-Verlauf, jede Zeile steht so auf der Website
    verlauf = [("Start", "Die Anzeigen laufen im Umkreis von Kirchheim."), ("Tag 18", "Der erste Auftrag."),
               ("Zwei Monate", "37 Bad-Anfragen, 12 Termine vor Ort."), ("Heute", "Kunden warten fast drei Wochen auf einen Termin. Die Anzeigen pausieren bis Februar.")]
    k5 = station("rf-k5", "k5", kopf("05", "Der Auftrag", "Tag 18.<br> Der erste Auftrag.")
                 + '<div class="rf-auftrag reveal"><p class="rf-riesig"><span class="nr" data-zahl="18">18</span><span>Tage</span></p>'
                 f'<div class="rf-auftrag-wer">{logo("sussmann", "Erich Sussmann GmbH")}<p>bis zum ersten Auftrag bei der Erich Sussmann GmbH in Kirchheim.</p></div></div>'
                 '<ol class="rf-verlauf reveal">' + "".join(f'<li class="{"an" if i == 1 else ""}"><b>{w}</b><span>{t}</span></li>' for i, (w, t) in enumerate(verlauf)) + '</ol>')

    # ── Danach: Senftleben verlängert, obwohl er voll ist ──
    danach = station("rf-danach", "k6", kopf("", "Danach", "Der Name bleibt.")
                     + f'<div class="rf-zwei rf-zwei-film"><div class="rf-film reveal">{video}<span class="rf-film-m">Originalfilm, 2:14</span></div>'
                     f'<div class="rf-text"><p class="reveal">{p_fall[0]}</p><blockquote class="rf-stimme reveal">{zitat}<cite>{zitat_wer}</cite></blockquote>'
                     + notiz("Wir haben gerade genug zu tun. Lohnt sich das trotzdem?", f_genug) + '</div></div>')

    # ── Stimmen: dieselbe Bahn, aber innerhalb der Strecke ──
    stimmen_neu = ('<section class="sek stimmen rf-station rf-stimmen"><div class="wrap rf-wrap"><div class="rf-kopf"><div class="rf-kopf-text reveal">'
                   '<span class="kicker">Kundenstimmen</span><h2>Wir lassen unsere Kunden sprechen.</h2></div></div>'
                   f'<div class="rf-bahnen">{bahnen}</div></div></section>')

    # ── Ziel: der Kontakt, die Linie endet am Signet ──
    kontakt = h[a_kontakt:e_kontakt]
    kontakt = kontakt.replace('<section class="sek umkreis-kontakt" id="kontakt"><div class="wrap">',
                              '<section class="sek umkreis-kontakt rf-station rf-ziel" id="kontakt"><div class="wrap rf-wrap"><div class="rf-kopf rf-kopf-ziel">'
                              + marke(SIGNET, "rf-signet") + '<div class="rf-kopf-text reveal">'
                              + notiz("Was kostet das?", f_kosten).replace(' reveal"', '"') + '</div></div>', 1)
    assert 'rf-ziel' in kontakt

    strecke = ('<div class="rf-strecke"><div class="rf-spur" aria-hidden="true"><i class="rf-zug"></i><i class="rf-spitze"></i></div>'
               + vorher + fahrplan + k1 + k2 + k3 + k4 + k5 + danach + stimmen_neu + kontakt + '</div>')
    h = h[:e_hero] + strecke + h[e_kontakt:]
    h = h.replace('</head>', f'<link rel="stylesheet" href="/start-neu/roter-faden/faden.css?v={V}"></head>', 1)
    h = h.replace('</body>', f'<script src="/start-neu/roter-faden/faden.js?v={V}" defer></script></body>', 1)
    h = h.replace('<title>', '<title>Entwurf roter Faden: ', 1)
    # Prüfungen
    assert 'noindex' in h and '<section class="sek faq"' not in h and '<section class="sek grund problem-sek"' not in h and '<section class="sek uebernehmen-sek"' not in h
    assert 'Werbung' not in "".join(re.findall(r'<h[123][^>]*>.*?</h[123]>', h, re.S))
    assert 'u-anzeige' not in h.split('class="rf-strecke"')[1], "gesperrtes Empfangsfoto (Umarmung)"
    for gesperrt in ("ess-team-lachen", "st-tragen", "senftleben-team-tragen", "senftleben-team-2026"):
        assert gesperrt not in h, gesperrt
    assert not re.findall(r'<span class="kicker">[^<]*·[^<]*</span>', h)
    return h


if __name__ == "__main__":
    seiten = entwurf_erfassen()
    quelle = seiten[str(HIER / "neukundengewinnung" / "index.html")]
    neu = baue(quelle)
    ZIEL.parent.mkdir(parents=True, exist_ok=True)
    ZIEL.write_text(neu)
    print("✓", ZIEL.relative_to(HIER.parent), len(neu))

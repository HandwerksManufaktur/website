"""Testfassung der Startseite: roter Faden entlang der Drei Säulen.

Baut test-startseite/index.html aus der Live-Startseite (index.html), damit beide nie
auseinanderlaufen. Live bleibt unberührt. Aufruf: python3 test-startseite/bauen.py
"""
import re
from html.parser import HTMLParser
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
h = (WURZEL / "index.html").read_text()


def ende_div(text, start):
    """Index hinter dem schließenden Tag des Elements, das bei start beginnt."""
    class P(HTMLParser):
        def __init__(s):
            super().__init__(convert_charrefs=False); s.tiefe = 0; s.ende = None
        def handle_starttag(s, tag, a):
            if tag == "div": s.tiefe += 1
        def handle_endtag(s, tag):
            if tag == "div" and s.ende is None:
                s.tiefe -= 1
                if s.tiefe == 0: s.ende = s.getpos()
    p = P(); p.feed(text[start:start + 60000])
    zeile, spalte = p.ende
    rest = text[start:].split("\n")
    return start + sum(len(z) + 1 for z in rest[:zeile - 1]) + spalte + len("</div>")


def ersetze(alt, neu, menge=1):
    global h
    assert h.count(alt) == menge, (alt, h.count(alt))
    h = h.replace(alt, neu)


# 1 · Nicht in Google, Startseite bleibt die echte Adresse
ersetze('<meta name="robots" content="index,follow">', '<meta name="robots" content="noindex, nofollow, noarchive">')

# 2 · Problem-Block: 5 → 3 Momente, je einer pro Säule (Google · Stockfotos · Bewerber)
for nr in (4, 2):  # von hinten, damit die Positionen stimmen
    a = h.index(f'<div class="lg-panel pb-panel" role="tabpanel" id="lg-p{nr}"')
    h = h[:a] + h[ende_div(h, a):]
    a = h.index(f'<button type="button" class="lg-tab" role="tab" id="lg-t{nr}"')
    h = h[:a] + h[h.index("</button>", a) + len("</button>"):]
ersetze("Fünf Momente, in denen deine Website entscheidet, ob sich jemand meldet.",
        "Drei Momente, in denen sich entscheidet, ob sich jemand meldet.")
ersetze('aria-label="Fünf Momente"', 'aria-label="Drei Momente"')

# 3 · Säulen am Handy ohne gepinnte Bühne (main.js liest das Attribut, eigener Cache-Schlüssel)
h = re.sub(r'main\.js\?v=[\w]+', 'main.js?v=faden1', h)
ersetze('<section class="sek system-sek" id="system">', '<section class="sek system-sek" id="system" data-ohne-buehne>')

# 4 · Beweise der Reihe nach den Säulen zuordnen
ersetze('<span class="kicker">Aus unseren Arbeiten</span>', '<span class="kicker">01 · Gefunden</span>')
ersetze('<span class="kicker">Aus der Praxis</span>', '<span class="kicker">02 · Gesehen</span>')
ersetze('<span class="kicker">Ergebnisse, nicht Versprechen</span>', '<span class="kicker">03 · Gebucht</span>')

# 5 · Reihenfolge: Problem → Säulen → 01 Gefunden → 02 Gesehen → 03 Gebucht → Team → Stimmen → Kontakt
def block(anfang):
    a = h.index(anfang)
    e = min(x for x in (h.find("\n<section", a + 1), h.find("\n</main", a + 1)) if x > 0)
    return a, e

namen = {
    "system": '<section class="sek system-sek"',
    "videos": '<section class="sek band auf-dunkel" id="videos"',
    "erg": '<section class="sek erg-sek"',
    "laufband": '<section class="sek laufband"',
    "google": '<section class="sek google grund"',
}
teile = {k: h[slice(*block(v))] for k, v in namen.items()}
a = block(namen["system"])[0]
e = block(namen["google"])[1]
assert h[a:e].count("<section class=\"sek") == 5, "unerwartete Abschnitte zwischen Säulen und Google"
neu = "".join(teile[k].rstrip("\n") + "\n\n" for k in ("system", "laufband", "google", "videos", "erg"))
h = h[:a] + neu.rstrip("\n") + h[e:]

(WURZEL / "test-startseite" / "index.html").write_text(h)
print("test-startseite/index.html gebaut")

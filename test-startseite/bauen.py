"""Testfassung der Startseite: roter Faden entlang der Drei Säulen.

Baut test-startseite/index.html aus der Live-Startseite (index.html), damit beide nie
auseinanderlaufen. Live bleibt unberührt. Aufruf: python3 test-startseite/bauen.py
"""
import re
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
h = (WURZEL / "index.html").read_text()


def ersetze(alt, neu, menge=1):
    global h
    assert h.count(alt) == menge, (alt, h.count(alt))
    h = h.replace(alt, neu)


# 1 · Nicht in Google, Startseite bleibt die echte Adresse
ersetze('<meta name="robots" content="index,follow">', '<meta name="robots" content="noindex, nofollow, noarchive">')

# 2 · Problem-Block: statt 5 Reitern mit abstrakten Platzhalter-Bildschirmen 3 Reiter (einer je Säule)
#     mit echten Namen und einem Schalter „Heute / Mit uns“, der von selbst umschaltet.
#     Die alten Reiter waren laut Zähler die meistgeklickte Stelle der Startseite → klickbar bleibt es.
#     (Noah, 15.10.2026: „so, dass die leute trotzdem klicken und checken was abgeht“)
a = h.index('<section class="sek grund lagen-sek probleme pb-sek">')
e = h.index("\n<section", a + 1)
h = h[:a] + (WURZEL / "test-startseite" / "problem_block.html").read_text().strip() + h[e:]
ersetze('<section class="sek laufband">', '<section class="sek laufband" id="gefunden">')

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

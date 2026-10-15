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

# 2 · Problem-Block: statt 5 Klick-Reitern mit nachgebauten Bildschirmen drei Karten,
#     die man ohne Klick versteht. Je Karte ein Moment, eine Säule, ein Sprung zum Beweis.
#     (Noah, 15.10.2026: „der normale Handwerksinhaber muss das safe checken“)
KARTEN = [
    ("01 · Gefunden", "#gefunden", "Ein Kunde googelt „Zimmerei“ und deinen Ort.",
     "Du stehst auf Seite 3. Er ruft den Nachbarn an.", "Du stehst ganz oben. Er ruft dich an."),
    ("02 · Gesehen", "#videos", "Er vergleicht drei Betriebe im Netz.",
     "Überall dieselben Stockfotos. Er nimmt den Günstigsten.", "Er sieht deine Leute und deine Baustellen. Er nimmt dich."),
    ("03 · Gebucht", "#ergebnisse", "Du suchst Aufträge oder einen neuen Monteur.",
     "Du wartest auf Empfehlungen. Es kommt zu wenig.", "Anzeigen im Umkreis. Anfragen und Bewerbungen landen bei dir."),
]
karten = "".join(
    f'<a class="pf-karte" href="{ziel}"><span class="kicker">{saeule}</span><b class="pf-moment">{moment}</b>'
    f'<p class="pf-heute"><i aria-hidden="true">✕</i><span><small>Heute</small>{heute}</span></p>'
    f'<p class="pf-mit"><i aria-hidden="true">✓</i><span><small>Mit uns</small>{mit}</span></p>'
    f'<span class="pf-los">So sieht das aus <span aria-hidden="true">↓</span></span></a>'
    for saeule, ziel, moment, heute, mit in KARTEN)
STIL = """<style>
.pf-raster{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}
.pf-karte{display:flex;flex-direction:column;gap:18px;padding:30px 28px;background:var(--papier);border-radius:var(--radius);color:var(--tinte);text-decoration:none;border:1px solid var(--papier-3);transition:transform .3s,box-shadow .3s,border-color .3s}
.pf-karte:hover{transform:translateY(-4px);box-shadow:0 18px 40px -22px rgba(22,19,14,.35);border-color:var(--bronze)}
.pf-moment{font-size:clamp(21px,1.6vw,24px);line-height:1.25;letter-spacing:-.01em}
.pf-karte p{display:grid;grid-template-columns:28px 1fr;gap:12px;margin:0;font-size:17px;line-height:1.45}
.pf-karte p i{display:grid;place-items:center;width:28px;height:28px;border-radius:50%;font-style:normal;font-size:14px;font-weight:700}
.pf-karte small{display:block;font-size:13px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;margin-bottom:2px}
.pf-heute{color:var(--tinte-3)}.pf-heute i{background:var(--papier-3);color:var(--tinte-3)}
.pf-mit{color:var(--tinte)}.pf-mit i{background:var(--tinte);color:var(--bronze-hell)}.pf-mit small{color:var(--bronze-tief)}
.pf-los{margin-top:auto;font-weight:600;color:var(--tinte);border-bottom:2px solid var(--bronze);align-self:flex-start;padding-bottom:2px}
@media (max-width:900px){.pf-raster{grid-template-columns:1fr}}
</style>"""
a = h.index('<section class="sek grund lagen-sek probleme pb-sek">')
e = h.index("\n<section", a + 1)
h = h[:a] + (
    '<section class="sek grund pf-sek"><div class="wrap"><div class="kopfzeile reveal">'
    '<span class="kicker">Woran es meistens hängt</span><h2>Gute Arbeit reicht nicht mehr, um gefunden zu werden.</h2>'
    '<p class="lead">Drei Momente, in denen sich ein Kunde oder Bewerber für dich entscheidet. Oder für den Nachbarn.</p></div>'
    f'<div class="pf-raster reveal">{karten}</div></div></section>{STIL}'
) + h[e:]
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

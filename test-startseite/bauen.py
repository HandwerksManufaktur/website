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

# 2 · Problem-Block: die bebilderten Szenen von vorher (Noah: „dass da davor bilder drin waren, das ist gut so“),
#     aber nur noch 3 Momente, einer je Säule, als 01 · Gefunden / 02 · Gesehen / 03 · Gebucht.
#     Die alten Reiter waren laut Zähler die meistgeklickte Stelle der Startseite → klickbar bleibt es.
def ende_div(text, start):
    """Index hinter dem </div>, das das bei start öffnende <div> schließt."""
    tiefe, i = 0, start
    for m in re.finditer(r"<div\b|</div>", text[start:]):
        tiefe += 1 if m.group(0) == "<div" else -1
        if tiefe == 0:
            return start + m.end()
    raise ValueError("kein Ende")

for nr in (4, 2):  # „Abends um zehn“ und „Die alte Homepage“ raus (abstrakte Platzhalter)
    a = h.index(f'<div class="lg-panel pb-panel" role="tabpanel" id="lg-p{nr}"')
    h = h[:a] + h[ende_div(h, a):]
    a = h.index(f'<button type="button" class="lg-tab" role="tab" id="lg-t{nr}"')
    h = h[:a] + h[h.index("</button>", a) + len("</button>"):]
for alt, nr, saeule in (("Bei Google unsichtbar", "01", "Gefunden"), ("Der Kunde vergleicht", "02", "Gesehen"),
                        ("Der Bewerber schaut nach", "03", "Gebucht")):
    ersetze(f"<b>{alt}</b>", f'<span class="lg-txt"><small>{nr} · {saeule}</small><b>{alt}</b></span>')
ersetze("Fünf Momente, in denen deine Website entscheidet, ob sich jemand meldet. Tipp auf einen.",
        "Drei Momente, in denen sich ein Kunde oder Bewerber für dich entscheidet. Oder für den Nachbarn. Tipp auf einen.")
ersetze('aria-label="Fünf Momente"', 'aria-label="Drei Momente"')
a = h.index('<section class="sek grund lagen-sek probleme pb-sek">')
e = h.index("</section>", a) + len("</section>")
h = h[:e] + (WURZEL / "test-startseite" / "problem_stil.html").read_text().strip() + h[e:]
ersetze('<section class="sek laufband">', '<section class="sek laufband" id="gefunden">')

# 3 · Säulen am Handy ohne gepinnte Bühne (main.js liest das Attribut, eigener Cache-Schlüssel)
h = re.sub(r'main\.js\?v=[\w]+', 'main.js?v=faden1', h)
ersetze('<section class="sek system-sek" id="system">', '<section class="sek system-sek" id="system" data-ohne-buehne>')

# 4 · Beweise der Reihe nach den Säulen zuordnen
ersetze('<span class="kicker">Aus unseren Arbeiten</span>', '<span class="kicker">01 · Gefunden</span>')
ersetze('<span class="kicker">Aus der Praxis</span>', '<span class="kicker">02 · Gesehen</span>')
ersetze('<span class="kicker">Ergebnisse, nicht Versprechen</span>', '<span class="kicker">03 · Gebucht</span>')

# 5 · Reihenfolge (Angriff 15.10.: erst Google, dann was man nach dem Klick sieht; Stimmen vor Team):
#     Problem → Säulen → 01 Google → 01 Website → 02 Videos → 03 Ergebnisse → Stimmen → Team → Kontakt
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
neu = "".join(teile[k].rstrip("\n") + "\n\n" for k in ("system", "google", "laufband", "videos", "erg"))
h = h[:a] + neu.rstrip("\n") + h[e:]

a, e = block('<section class="sek team-sek"')
team = h[a:e]; h = h[:a] + h[e:].lstrip("\n")
a, e = block('<section class="sek stimmen"')
h = h[:e] + "\n\n" + team.rstrip("\n") + h[e:]

# 6 · Copy: alles knüpft an „Gute Arbeit reicht nicht mehr, um gefunden zu werden“ an (Angriff 15.10.2026)
ersetze("Drei Momente, in denen sich ein Kunde oder Bewerber für dich entscheidet. Oder für den Nachbarn. Tipp auf einen.",
        "Drei Momente, in denen sich Kunden und Bewerber für dich entscheiden. Oder für den Nachbarn. Tipp auf den, wo es bei dir hakt.")
ersetze('<span class="pb-marke gut">Platz 1 in deinem Ort</span>', '<span class="pb-marke gut">Ganz vorne in deinem Ort</span>')
ersetze('<span class="kicker">Das Drei-Säulen-System</span>', '<span class="kicker">Die Lösung in drei Schritten</span>')
ersetze("<h2>Drei Säulen, die aufeinander aufbauen.</h2>", "<h2>Damit man dich findet, sieht und bucht.</h2>")
ersetze("Kein Baukasten aus sechs Angeboten, sondern ein Auftritt, der in drei Schritten aufeinander aufbaut. Wo wir bei dir anfangen, klären wir im Erstgespräch: bei den meisten ist es die Website, bei manchen die Stelle, die seit Monaten offen ist.",
        "Ein Kunde findet dich bei Google, sieht deine Arbeit und deine Leute und ruft dann an. Bei Bewerbern läuft es genauso. Für jeden dieser drei Schritte bauen wir dir das Passende, und womit du anfängst, klären wir im Erstgespräch.")
ersetze("Anzeigen im Umkreis, vier Filterfragen davor.", "Anzeigen im Umkreis. Wer sich meldet, beantwortet vorher ein paar kurze Fragen.")
ersetze('<span class="kicker">Probier es aus</span>', '<span class="kicker">01 · Gefunden bei Google</span>')
ersetze('<span class="kicker">01 · Gefunden</span>', '<span class="kicker">01 · Gefunden über die Website</span>')
ersetze("<h2>Frag Google einfach selbst.</h2>", "<h2>So stehen unsere Kunden bei Google da.</h2>")
ersetze("Tipp einen Suchbegriff an. So suchen Kunden, und so stehen unsere Betriebe da.",
        "Tipp einen Suchbegriff an, so wie ihn ein Kunde eintippt. Du siehst, auf welchem Platz der Betrieb steht.")
ersetze("<h2>Das läuft gerade live.</h2>", "<h2>Das sehen Kunden nach dem Klick.</h2>")
ersetze("Bildschirmaufnahmen der fertigen Websites, so wie sie heute online sind. Klick auf eine, dann bist du drauf.",
        "Fertige Websites unserer Betriebe, so wie sie heute online sind. Klick auf eine, dann bist du drauf.")
ersetze("<h2>Bei unseren Kunden gedreht.</h2>", "<h2>Zeig, wie bei dir gearbeitet wird.</h2>")
ersetze("Drohne, Kamera, Baustellenstaub. Skript, Dreh und Schnitt von uns, vor der Kamera steht der Chef. Alle Aufnahmen gehören danach dem Betrieb.",
        "So sehen Kunden deine Arbeit und Bewerber dein Team, bevor sie anrufen. Dreh und Schnitt machen wir, die Aufnahmen gehören danach dir.")
ersetze("<h2>Was dabei rauskommt.</h2>", "<h2>Das bringen Anzeigen im Umkreis.</h2>")
ersetze("Drei Betriebe, drei Kampagnen, alle Zahlen aus den laufenden Konten. Klick auf ein Video, dann erzählt es der Chef selbst.",
        "Drei Handwerksbetriebe, echte Zahlen aus den laufenden Anzeigen. Klick auf ein Video, dann erzählt es der Chef selbst.")
ersetze("<h2>Wir können viel erzählen. Unsere Kunden erzählen es besser.</h2>", "<h2>Und du musst dich um nichts davon selbst kümmern.</h2>")

(WURZEL / "test-startseite" / "index.html").write_text(h)
print("test-startseite/index.html gebaut")

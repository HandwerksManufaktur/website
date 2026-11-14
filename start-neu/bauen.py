"""Entwurf der Startseite: Firma → Leistungen → Ergebnisse (Noah, 14.11.2026, wie shk…/start-neu/).

Die Startseite positioniert uns als Partner für Handwerksbetriebe, zeigt die drei Leistungen
gleichrangig und danach die Ergebnisse; Problem-Szenen und Mechanik gehören auf die Unterseiten.
Baut start-neu/index.html aus der Live-Startseite (index.html), damit beide nie auseinanderlaufen.
Live bleibt unberührt. Aufruf: python3 start-neu/bauen.py
"""
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
h = (WURZEL / "index.html").read_text()


def ersetze(alt, neu, menge=1):
    global h
    assert h.count(alt) == menge, (alt[:70], h.count(alt))
    h = h.replace(alt, neu)


def sektion(anfang):
    """(start, ende) der <section>, die mit `anfang` beginnt."""
    assert h.count(anfang) == 1, (anfang, h.count(anfang))
    a = h.index(anfang)
    return a, h.index("</section>", a) + len("</section>")


# 1 · Nicht in Google, die echte Startseite bleibt die Adresse
ersetze('<meta name="robots" content="index,follow">', '<meta name="robots" content="noindex, nofollow, noarchive">')

# 2 · Erster Satz: wer wir sind und für wen, keine Einzelleistung als Lösung
ersetze('<h1><span class="w">Mehr Aufträge.</span> <span class="w">Mehr Bewerber.</span> <span class="w">Aus deinem Umkreis.</span></h1>',
        '<h1><span class="w">Der Partner für</span> <span class="w">Handwerksbetriebe.</span></h1>')
ersetze('<p class="lead">Website, Fotos und Social-Media-Werbung für Handwerksbetriebe.</p>',
        '<p class="lead">Über 130 Betriebe arbeiten mit uns. Wir bauen deine Website, machen Fotos und Videos bei dir im Betrieb und schalten Anzeigen für Kunden und Mitarbeiter.</p>')

# 3 · Aufbau: Leistungen direkt nach den Logos, Problem-Szenen raus (stehen auf den Unterseiten)
a, e = sektion('<section class="sek system-sek" id="system"')
leistungen = h[a:e]
h = h[:a] + h[e:]
a, e = sektion('<section class="sek grund lagen-sek probleme pb-sek">')
h = h[:a] + leistungen + h[e:]

(Path(__file__).resolve().parent / "index.html").write_text(h)
print("✓ start-neu/index.html", len(h))

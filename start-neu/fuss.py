"""Fuß der HWM-Seite angleichen (Noah, 18.11.2026): „Websites für dein Gewerk“ und „Mitarbeiter finden je Gewerk“ unten
nicht mehr anzeigen, Einsatzgebiet raus, Telefon/Mail/Zeiten mittig zum Icon (vorher Emoji auf der Grundlinie neben 44-px-Links).
Dieselbe Fassung erzeugt kunden/handwerksmanufaktur/konzept/build_pages.fuss() (FUSS_KONTAKT).

Aufruf über alle live gepflegten Seiten:  .venv/bin/python firma/website/start-neu/fuss.py
"""
import re
from pathlib import Path

FUSS_KONTAKT = ('<ul class="kontakt-f"><li><svg class="kf-ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/></svg><a href="tel:+4981947174990">+49 8194 7174990</a></li>'
                '<li><svg class="kf-ic" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg><a href="mailto:info@handwerksmanufaktur.digital">info@handwerksmanufaktur.digital</a></li>'
                '<li><svg class="kf-ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg><span>Mo–Fr, 8:00–18:00 Uhr</span></li></ul>')


def fuss_neu(h):
    h, n = re.subn(r'<ul class="kontakt-f">.*?</ul>', FUSS_KONTAKT, h, count=1, flags=re.S)
    assert n == 1, "kontakt-f fehlt"
    h = re.sub(r'<div class="fuss-gewerke">.*?</ul></div>', '', h, flags=re.S)
    assert 'fuss-gewerke' not in h.split('<footer', 1)[-1] and 'Einsatzgebiet' not in h.split('<footer', 1)[-1]
    # Karriereseite (Noah, 21.11.2026): Link im Fuß unter „Unternehmen“, und die „Wir suchen dich“-Karte im Team zeigt auf
    # /karriere/ statt auf den alten Opener-Funnel
    if '<a href="/karriere/">Karriere</a>' not in h:
        h = h.replace('<li><a href="/ueber-uns/">Über uns</a></li>', '<li><a href="/ueber-uns/">Über uns</a></li><li><a href="/karriere/">Karriere</a></li>', 1)
    h = h.replace('href="https://jobs.die-handwerksmanufaktur.de/" rel="noopener"', 'href="/karriere/"')
    return h




AUSLASSEN = ("alt/", "archiv-2026-09/", "neu/", "neu-neu/", "test/", "test-startseite/", "start-neu/", "praesentation/",
             "onboarding/", "einwilligung/", "github-vorbereitung/", "cf-worker/", "konzept/")

if __name__ == "__main__":
    wurzel = Path(__file__).resolve().parent.parent
    n = 0
    for f in sorted(wurzel.glob("**/index.html")):
        rel = str(f.relative_to(wurzel))
        if rel.startswith(AUSLASSEN): continue
        h = f.read_text(encoding="utf-8")
        if 'class="kontakt-f"' not in h: continue
        neu = fuss_neu(h)
        if neu != h:
            f.write_text(neu, encoding="utf-8"); n += 1
    print(f"Fuß angeglichen: {n} Seiten")

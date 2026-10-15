"""Vergleich Szene 3 (03 · Gebucht): live (fehlende Karriereseite) neben Vorschlag (Stellenanzeige im Feed).

Noah, 16.10.2026: „du kannst mir mal testmäßig es nebeneinander machen“. Erzeugt aus der Live-Startseite:
  test-startseite/szene3/alt.html   Startseite wie live, öffnet Moment 3
  test-startseite/szene3/neu.html   Startseite mit neuer Szene 3, öffnet Moment 3
  test-startseite/szene3/index.html beide nebeneinander (noindex)
Aufruf: python3 test-startseite/szene3_bauen.py
"""
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
ZIEL = WURZEL / "test-startseite" / "szene3"
h = (WURZEL / "index.html").read_text()
h = h.replace('<meta name="robots" content="index,follow">', '<meta name="robots" content="noindex, nofollow, noarchive">')
assert "noindex" in h

# Moment 3 öffnen und hinscrollen; Klick hält die automatische Rotation an
OEFFNEN = """<script>
addEventListener('load', () => setTimeout(() => {
  const t = document.querySelectorAll('.pb-sek .lg-tab')[2]; if (!t) return;
  document.querySelector('.pb-sek .lg-buehne').scrollIntoView({ block: 'center' });
  let n = 0; const tippen = () => { if (t.classList.contains('an') || n++ > 8) return; t.click(); setTimeout(tippen, 700); };
  setTimeout(tippen, 400);
}, 600));
</script>"""

a = h.index('<div class="lg-panel pb-panel" role="tabpanel" id="lg-p3"')
heute_a = h.index('<div class="lg-seite heute">', a)
vs = h.index('<span class="pb-vs"', a)

NEU = """<div class="lg-seite heute"><span class="lg-etikett"><i>✕</i>Heute</span><div class="pb-g ps-heute"><div class="ps-wagen"><img src="/static/assets/img/fall/erwin-schmidt-team.jpg" alt="" loading="lazy" decoding="async" width="1100" height="733"><span class="ps-kleber"><small>Wir suchen</small><b>Monteur (m/w/d)</b><i aria-hidden="true">▦ QR</i></span></div><div class="ps-zahl"><small>Bewerbungen in 3 Monaten</small><b>0</b></div><span class="pb-marke schlecht">↩︎ Gesehen hat sie keiner</span></div><p>Die Stelle hängt am Wagen und auf der Website. Ein Monteur im Umkreis bekommt sie nie zu sehen.</p></div>
<div class="lg-seite mit"><span class="lg-etikett"><i>✓</i>Mit uns</span><div class="pb-g pb-bew gut"><div class="pb-handy ps-feed"><div class="ps-kopf"><span class="ps-ava">DB</span><span><b>Dein Betrieb</b><small>Gesponsert · 25 km</small></span></div><img class="ps-bild" src="/static/assets/img/fall/ess-zwei-monteure.jpg" alt="" loading="lazy" decoding="async" width="1600" height="1067"><div class="ps-text"><b>Anlagenmechaniker gesucht</b><small>Festes Team, eigener Wagen, 4-Tage-Woche möglich.</small></div><span class="pb-ruf">In 60 Sekunden bewerben</span><span class="pb-finger" aria-hidden="true"></span><span class="pb-ok">✓ Bewerbung gesendet</span></div><span class="pb-marke gut">✓ Bewerbung eingegangen</span></div><p>Er sieht die Stelle abends am Handy, im Umkreis. Und bewirbt sich in einer Minute.</p></div>
"""
STIL = """<style>
.ps-heute{gap:14px}
.ps-wagen{position:relative;width:min(300px,100%);aspect-ratio:4/3;border-radius:18px;overflow:hidden;box-shadow:0 0 0 1px rgba(22,19,14,.12)}
.ps-wagen img{width:100%;height:100%;object-fit:cover;object-position:88% 55%;filter:saturate(.75)}
.ps-kleber{position:absolute;right:10px;bottom:10px;display:grid;gap:1px;padding:8px 10px;border-radius:10px;background:#fff;box-shadow:0 6px 16px -8px rgba(0,0,0,.5);font-size:13px;line-height:1.2;color:var(--tinte)}
.ps-kleber small{font-size:13px;color:var(--tinte-3)}.ps-kleber i{font-style:normal;font-size:13px;color:var(--tinte-3)}
.ps-zahl{display:flex;align-items:baseline;gap:10px;padding:8px 16px;border-radius:var(--pille);background:var(--papier-2)}
.ps-zahl small{font-size:14px;color:var(--tinte-3)}.ps-zahl b{font-size:22px}
.ps-feed{gap:7px}
.ps-kopf{display:flex;align-items:center;gap:8px;font-size:13px;line-height:1.15;text-align:left}
.ps-kopf b{color:var(--tinte)}
.ps-kopf small{display:block;font-size:13px;color:var(--tinte-3)}
.ps-ava{display:grid;place-items:center;width:28px;height:28px;border-radius:50%;background:var(--tinte);color:var(--bronze-hell);font-size:13px;font-weight:700;flex:none}
.ps-bild{width:100%;height:96px;object-fit:cover;object-position:50% 30%;border-radius:10px}
.ps-text{display:grid;gap:2px;text-align:left;font-size:13px;line-height:1.25;color:var(--tinte)}
.ps-text small{font-size:13px;color:var(--tinte-3)}
</style>"""
neu = h[:heute_a] + NEU + h[vs:]
neu = neu.replace("<b>Der Bewerber schaut nach</b>", "<b>Deine Stelle sieht keiner</b>")
neu = neu.replace("</body>", STIL + OEFFNEN + "</body>")
alt = h.replace("</body>", OEFFNEN + "</body>")

VERGLEICH = """<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive"><title>Szene 3 im Vergleich</title>
<style>
:root{--papier:#FAF7F1;--tinte:#16130E;--bronze:#C8873A}
body{margin:0;background:var(--papier);color:var(--tinte);font:16px/1.4 system-ui,-apple-system,sans-serif}
header{padding:24px 24px 8px}h1{margin:0 0 4px;font-size:24px}p{margin:0;color:#6B6355}
.zwei{display:grid;grid-template-columns:1fr 1fr;gap:20px;padding:16px 24px 32px}
.spalte h2{margin:0 0 10px;font-size:17px}.spalte h2 span{color:var(--bronze)}
.rahmen{position:relative;width:100%;aspect-ratio:1440/900;overflow:hidden;border-radius:16px;box-shadow:0 0 0 1px rgba(22,19,14,.12);background:#fff}
.rahmen iframe{position:absolute;top:0;left:0;width:1440px;height:900px;border:0;transform-origin:0 0}
a{color:inherit}
@media (max-width:900px){.zwei{grid-template-columns:1fr}}
</style></head><body>
<header><h1>Szene 3 · „03 · Gebucht“ im Vergleich</h1><p>Links wie jetzt live, rechts der Vorschlag. Beide öffnen Moment 3 von selbst. Klick in den Rahmen, um zu wechseln.</p></header>
<div class="zwei">
<div class="spalte"><h2>Jetzt live · <span>Keine Karriereseite</span></h2><div class="rahmen"><iframe src="alt.html" title="Szene 3 live"></iframe></div><p style="margin-top:8px"><a href="alt.html" target="_blank">groß öffnen ↗</a></p></div>
<div class="spalte"><h2>Vorschlag · <span>Stellenanzeige im Umkreis</span></h2><div class="rahmen"><iframe src="neu.html" title="Szene 3 Vorschlag"></iframe></div><p style="margin-top:8px"><a href="neu.html" target="_blank">groß öffnen ↗</a></p></div>
</div>
<script>
const passen = () => document.querySelectorAll('.rahmen').forEach(r => { const f = r.querySelector('iframe'); f.style.transform = `scale(${r.clientWidth / 1440})`; });
addEventListener('resize', passen); passen();
</script></body></html>"""

ZIEL.mkdir(parents=True, exist_ok=True)
(ZIEL / "alt.html").write_text(alt)
(ZIEL / "neu.html").write_text(neu)
(ZIEL / "index.html").write_text(VERGLEICH)
print("szene3 gebaut")

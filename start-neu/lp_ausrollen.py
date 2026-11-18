"""Stadt- und Gewerkseiten aus einer Konzept-Probe gezielt live übernehmen (18.11.2026).

hwm_konzept_live.py würde live gepflegte Seiten (ueber-uns, Rechner-Entfernung vom 15.11.) mit der Konzept-Fassung
überschreiben. Deshalb: Probe bauen (`hwm_konzept_live.py --probe DIR`), dann nur die 17 Landingpages + neue Dateien
unter static/ übernehmen; Rechner raus wie live (Seite.ohne_rechner), Fuß und Stimmen wie start-neu/fuss.py.
Aufruf: .venv/bin/python firma/website/start-neu/lp_ausrollen.py <probe-ordner>
"""
import re, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fuss import fuss_neu

PROBE = Path(sys.argv[1]); WURZEL = Path(__file__).resolve().parent.parent
SEITEN = [p.parent.name for p in PROBE.glob("website-*/index.html") if not p.parent.name.startswith(("website-fuer-", "website-aufwand"))] + \
         [p.parent.name for p in PROBE.glob("webdesign-*/index.html")]
assert len(SEITEN) == 17, SEITEN


def ohne_rechner(h, name):
    h, n1 = re.subn(r'\n?<button type="button" class="uk-rechner" data-rechner>.*?</button>', "", h, flags=re.S)
    h, n2 = re.subn(r'<dialog class="rd" id="rechner-dialog".*?</dialog>', "", h, flags=re.S)
    h = re.sub(r'href="#rechner-auf"', 'href="/kontakt/"', h)
    rest = re.findall(r'.{60}(?:rechner|Rechner|durchrechnen).{40}', h)
    assert not rest, (name, n1, n2, rest[:2])
    return h


for s in SEITEN:
    h = (PROBE / s / "index.html").read_text(encoding="utf-8")
    h = fuss_neu(ohne_rechner(h, s))
    assert "Entwurf" not in re.sub(r"<[^>]+>", " ", h), (s, "Entwurf")
    (WURZEL / s / "index.html").write_text(h, encoding="utf-8")

neu = 0
for f in (PROBE / "static").rglob("*"):
    if f.is_dir(): continue
    rel = f.relative_to(PROBE)
    ziel = WURZEL / rel
    if str(rel) in ("static/main.js", "static/styles.css"): continue
    if not ziel.exists() or (str(rel).startswith(("static/assets/lp/", "static/assets/img/lp/")) and ziel.read_bytes() != f.read_bytes()):
        ziel.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(f, ziel); neu += 1
print(f"{len(SEITEN)} Seiten übernommen, {neu} Dateien unter static/ neu oder geändert")

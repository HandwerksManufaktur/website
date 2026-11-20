"""Noah ist auf allen Seiten „Inhaber“, nie „Gründer“ (Noah, 20.11.2026: „bei mir schreibst du nicht hin Gründer sondern Inhaber“).

Läuft über jede HTML-Seite der HWM-Website (auch start-neu/quelle, aus der bauen.py baut) und meldet, was übrig bleibt.
Aufruf:  .venv/bin/python firma/website/start-neu/inhaber.py [--pruefen]   (--pruefen: Exit 1, wenn „Gründer“ noch irgendwo bei Noah steht)
"""
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
ERSATZ = [("Gründer &amp; Geschäftsführer", "Inhaber"), ("Gründer & Geschäftsführer", "Inhaber"),
          ("Gründer &amp; Inhaber", "Inhaber"), ("Gründer & Inhaber", "Inhaber"),
          ('"jobTitle": "Gründer"', '"jobTitle": "Inhaber"'), ("<span>Gründer</span>", "<span>Inhaber</span>"),
          ("Noah Seelau</b> · Gründer,", "Noah Seelau</b> · Inhaber,"), ("Noah Seelau · Gründer", "Noah Seelau · Inhaber"),
          ("ich bin Noah, Gründer der", "ich bin Noah, Inhaber der")]


def seiten():
    return [p for p in WURZEL.rglob("*.html") if "node_modules" not in p.parts and ".git" not in p.parts]


if __name__ == "__main__":
    pruefen = "--pruefen" in sys.argv
    rest, geaendert = [], 0
    for p in seiten():
        t = p.read_text(encoding="utf-8", errors="ignore")
        n = t
        if not pruefen:
            for a, b in ERSATZ:
                n = n.replace(a, b)
            if n != t:
                p.write_text(n, encoding="utf-8"); geaendert += 1
        if "Gründer" in n:
            rest.append(str(p.relative_to(WURZEL)))
    print(f"{geaendert} Seiten geändert, „Gründer“ noch in {len(rest)}: {rest[:6]}")
    sys.exit(1 if rest else 0)

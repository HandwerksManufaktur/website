"""Kundenseiten werden auf handwerksmanufaktur.digital gezeigt, aber nie verlinkt (Noah, 19.11.2026:
„Die ganzen Websites will ich eigentlich nicht verlinkt haben bei Handwerksmanufaktur … mach einfach alle live und mach die
nicht zum Anklicken, nicht zum Antippen“).

entlinken(html) macht aus jedem Link auf eine Kundendomain reinen Inhalt: Laufband-Karten werden <div>, „Live ansehen“-Links
fallen weg, jeder andere Link wird <span> mit derselben Klasse. Quellen-Links (Bitkom, IW, Statistiken) bleiben.

Aufruf:  .venv/bin/python firma/website/start-neu/kunden_links.py            → alle Live-Seiten der HWM-Website
         .venv/bin/python firma/website/start-neu/kunden_links.py --pruefen  → zählt verbliebene Kundenlinks (Exit 1, wenn > 0)
"""
import re, sys
from pathlib import Path

import yaml

WURZEL = Path(__file__).resolve().parent.parent
RANKINGS = WURZEL.parent.parent / "system/config/rankings.yaml"
EXTRA = {"aeditec.de", "ammer-lech-bau.de", "ausbau-jirka.de", "axelkaiser-metallbau.de", "azemi-hausrenovierung.de", "baumring.de",
         "bib-bau-eichenau.de", "eibl-bau.de", "elektro-langmajer.de", "elektrotechnik-wohner.de", "energie-fischer.de",
         "entenmann-haustechnik.de", "erwin-schmidt-sohn.de", "es-m.de", "fconstruct.de", "federspiel.info", "fensterreinigung-esapovic.de",
         "gallenberger-shk.de", "gutachter-hilbenz.de", "haustechnik-buchschmid.de", "hofmann-zimmerei.de", "hohenester.de",
         "hs-irlbacher.de", "juwelier-wagenknecht.de", "kfz-greif.de", "klooster-transporte.de", "kohler-bau-meisterbetrieb.de",
         "lanzinger-gmbh.de", "larosaholzbau.de", "lueders-fliesen.de", "maler-abenthum.de", "maler-dp.de", "malerböck.de",
         "max-gleiser-bau.de", "mehrlebensenergie-praxis.de", "meisterschillinger.de", "mh-maschinenbau.de", "mueller-maler-meister.de",
         "oswald-bau-weil.de", "planung-hindelang.de", "proebstl-holz.de", "richard-senftleben.de", "rupp-rott.de", "satis-factory.de",
         "schreinerei-damnig.de", "schreinerei-volmerg.de", "schuster-holzbau.de", "schustererisried.de", "sdhirsch.de",
         "allplast-laser.de", "steuerberater-rieger.com", "stimpfle-sanitaer.de", "taro-design.de", "textilreinigung-berger.de",
         "tore-musch.de", "volkamer-leichtmetallbau.de", "w-w-bau.com", "weber-metalltechnik.com", "wegelebau.de", "wmrt.de",
         "zimmerei-fagner.de", "zimmerei-koller.com", "zimmerei-pfoederl.de", "zimmerei-spenglerei-tous.de", "dinkel-metallbau.de",
         "baureize.de", "kirchner-thaining.de", "cs-metalldesign.de"}


def domains():
    d = set(EXTRA)
    for r in yaml.safe_load(RANKINGS.read_text(encoding="utf-8"))["eintraege"]:
        if r.get("domain"):
            d.add(r["domain"].lower().removeprefix("www."))
    return d


def _muster():
    alt = "|".join(re.escape(x) for x in sorted(domains(), key=len, reverse=True))
    return rf'https?://(?:[a-z0-9-]+\.)?(?:{alt})(?:[/?#][^"]*)?'


def entlinken(html):
    m = _muster()
    # 1) Laufband-Karten: <a class="lb-k" …> … </a> → <div class="lb-k"> … </div>
    html = re.sub(rf'<a class="lb-k" href="{m}"[^>]*>(.*?)</a>', r'<div class="lb-k">\1</div>', html, flags=re.S)
    # 2) „Live ansehen ↗“ / „Website ansehen“: der Link fällt ganz weg
    html = re.sub(rf'<a [^>]*href="{m}"[^>]*>\s*(?:Live|Website|Seite) ansehen.*?</a>', '', html, flags=re.S)
    # 3) jeder andere Kundenlink → <span> mit derselben Klasse
    def span(t):
        kl = re.search(r'class="([^"]*)"', t.group(1))
        return f'<span{f" class={chr(34)}{kl.group(1)}{chr(34)}" if kl else ""}>{t.group(2)}</span>'
    html = re.sub(rf'<a ((?:(?!>).)*?href="{m}"[^>]*)>(.*?)</a>', span, html, flags=re.S)
    html = html.replace("Alle live. Tipp eine an.", "Alle live.")
    return html


def rest(html):
    return re.findall(rf'<a [^>]*href="({_muster()})"', html)


def seiten():
    return [p for p in WURZEL.rglob("*.html") if "node_modules" not in p.parts and ".git" not in p.parts]


if __name__ == "__main__":
    pruefen = "--pruefen" in sys.argv
    gesamt, geaendert = 0, 0
    for p in seiten():
        t = p.read_text(encoding="utf-8", errors="ignore")
        if not pruefen:
            n = entlinken(t)
            if n != t:
                p.write_text(n, encoding="utf-8"); geaendert += 1
                t = n
        r = rest(t)
        if r:
            gesamt += len(r); print(len(r), p.relative_to(WURZEL), r[:2])
        if "Tipp eine an" in t:
            gesamt += 1; print("Tipp eine an:", p.relative_to(WURZEL))
    print(f"{geaendert} Seiten geändert, {gesamt} Kundenlinks übrig")
    sys.exit(1 if gesamt else 0)

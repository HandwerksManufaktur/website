"""Karriereseite /karriere/ (Noah, 21.11.2026: „wir suchen einmal opener, dann einmal fullfilment jemanden und backoffice …
bau das einfach mal auf ne richtig geile karriere seite“).

Aufbau nach der Kurslektion „Recruiting Seite / Karriere Seite Aufbau“ (Agency Elite → Team Aufbau & Management):
offene Stellen → Werte → Benefits → Stimme → Team, dazu Schnellbewerbung ohne langes Formular und mobil zuerst.
Inhalte der Opener-Stelle aus dem eigenen Bewerber-Funnel (firma/sales-funnel/adapted/home.md) und der JOIN-Anzeige
(firma/sales-funnel/join-anzeige.md): Zeiten, Provision pro ERSCHIENENEM Termin, über 30 Termine in einer Woche.
Kopf, Menü und Fuß kommen aus ueber-uns/index.html, damit sie nie auseinanderlaufen. Bewerbungen gehen wie das
Kontaktformular über Web3Forms an info@ (Betreff „Neue Bewerbung: <Stelle>“).

Aufruf: /Users/noahs/CEO-GPT/.venv/bin/python firma/website/start-neu/karriere.py
"""
import json
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
WURZEL = HIER.parent
sys.path.insert(0, str(HIER))
from fuss import fuss_neu

ZURUECK = '<svg viewBox="0 0 24 24"><path d="M19 12H5M11 6l-6 6 6 6"/></svg>'
PFEIL = '<svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
HAKEN = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 4 4L19 7"/></svg>'
PLUS = '<span class="plus"><svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg></span>'
TEL = '<svg viewBox="0 0 24 24"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/></svg>'
MAIL = '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>'

TITEL = "Karriere – Jobs bei der HandwerksManufaktur, 100 % remote"
BESCHR = ("Wir suchen Verstärkung: Opener im Vertrieb, Account Manager / Media Buyer und Backoffice. "
          "100 % remote, Bewerbung in zwei Minuten ohne Lebenslauf.")

# ── Die drei Stellen ───────────────────────────────────────────────────────────────────────────────
STELLEN = [
    {
        "id": "opener", "bereich": "Vertrieb", "titel": "Opener (m/w/d)", "kurz": "Opener",
        "fakten": ["Remote", "Vollzeit", "ab sofort"],
        "satz": "Du rufst Handwerksbetriebe an und legst Termine für unser Sales-Team.",
        "aufgaben": ["Du telefonierst mit Inhabern von Handwerksbetrieben.",
                     "Du weckst Interesse und legst qualifizierte Termine in den Kalender unseres Sales-Teams.",
                     "Du hältst jeden Anruf sauber im CRM fest.",
                     "Läuft es gut, wirst du schnell Setter und später auch Closer."],
        "mitbringen": ["Lust aufs Telefonieren und ein dickes Fell.",
                       "Ruhiger Arbeitsplatz, Headset und stabiles Internet.",
                       "Erfahrung im Vertrieb ist schön, aber kein Muss."],
        "bekommen": ["Fixum, dazu Provision pro erschienenem Termin und pro Abschluss.",
                     "Skripte, einen klaren Ablauf und Einarbeitung direkt durch Noah.",
                     "Ein Angebot, bei dem Termine leicht kommen."],
        "jp_typ": "FULL_TIME",
    },
    {
        "id": "account", "bereich": "Fulfillment", "titel": "Account Manager / Media Buyer (m/w/d)", "kurz": "Account Manager",
        "fakten": ["Remote", "Vollzeit", "ab sofort"],
        "satz": "Du betreust unsere Kunden und sorgst dafür, dass ihre Anzeigen Anfragen und Bewerber bringen.",
        "aufgaben": ["Du betreust Handwerksbetriebe, deren Anzeigen bei uns laufen, für neue Kunden oder neue Mitarbeiter.",
                     "Du setzt Kampagnen im Meta-Werbeanzeigenmanager auf, testest Anzeigen und hältst die Kosten je Anfrage im Blick.",
                     "Du pflegst die Anfrage- und Bewerbungsseiten und planst mit, was am Drehtag gefilmt wird.",
                     "Du führst Kick-off und Kampagnen-Review und bist der feste Ansprechpartner des Kunden."],
        "mitbringen": ["Erfahrung mit Meta-Ads oder in der Kundenbetreuung einer Agentur.",
                       "Du denkst in Zahlen und erklärst sie so, dass ein Handwerksmeister sie versteht.",
                       "Sehr gutes Deutsch, am Telefon und schriftlich.",
                       "Du arbeitest selbstständig und hältst, was du zusagst."],
        "bekommen": ["Feste Vergütung, die Höhe klären wir im Gespräch.",
                     "Kampagnen mit belegten Ergebnissen, etwa 37 Bad-Anfragen für einen Betrieb oder eine Stelle in 18 Tagen besetzt.",
                     "Reports, Lead-Mails und Auswertungen laufen automatisch. Du kümmerst dich um das, was zählt."],
        "jp_typ": "FULL_TIME",
    },
    {
        "id": "backoffice", "bereich": "Backoffice", "titel": "Backoffice & Administration (m/w/d)", "kurz": "Backoffice",
        "fakten": ["Remote", "Teilzeit möglich", "ab sofort"],
        "satz": "Du hältst uns den Rücken frei: Kundenakten, Termine, Rechnungen und Postfach.",
        "aufgaben": ["Du nimmst neue Kunden auf: Unterlagen, Zugänge und Termine für Drehtag und Kick-off.",
                     "Du pflegst Kundenakten und CRM und behältst Termine und Fristen im Blick.",
                     "Du bereitest Rechnungen vor, ordnest Belege und gleichst Zahlungen ab.",
                     "Du sortierst das Postfach und beantwortest einfache Anfragen selbst."],
        "mitbringen": ["Du arbeitest gern ordentlich und vergisst nichts.",
                       "Erfahrung im Büro oder in der Assistenz ist ein Plus.",
                       "Du kommst mit Google Workspace, Tabellen und neuen Programmen schnell klar.",
                       "Sehr gutes Deutsch."],
        "bekommen": ["Feste Vergütung, die Höhe klären wir im Gespräch.",
                     "Klare Abläufe, viele Routinen laufen schon automatisch.",
                     "Freie Zeiteinteilung, solange die Aufgaben sitzen."],
        "jp_typ": "PART_TIME",
    },
]


def liste(punkte):
    return "<ul>" + "".join(f"<li>{HAKEN}<span>{p}</span></li>" for p in punkte) + "</ul>"


def stelle(i, s):
    fakten = "".join(f"<span>{f}</span>" for f in s["fakten"])
    return (f'<details class="kr-stelle reveal" id="stelle-{s["id"]}"{" open" if i == 0 else ""}>'
            f'<summary><span class="kr-nr">0{i + 1}</span><span class="kr-kopf"><span class="kr-bereich">{s["bereich"]}</span>'
            f'<h3>{s["titel"]}</h3><span class="kr-satz">{s["satz"]}</span><span class="kr-fakten">{fakten}</span></span>'
            f'<span class="kr-auf" aria-hidden="true">{PLUS}</span></summary>'
            f'<div class="kr-inhalt"><div class="kr-spalten">'
            f'<div><h4>Deine Aufgaben</h4>{liste(s["aufgaben"])}</div>'
            f'<div><h4>Das bringst du mit</h4>{liste(s["mitbringen"])}</div>'
            f'<div><h4>Das bekommst du</h4>{liste(s["bekommen"])}</div></div>'
            f'<a class="btn btn-bronze" href="#bewerben" data-stelle="{s["id"]}">Als {s["kurz"]} bewerben {PFEIL}</a></div></details>')


WERTE = [
    ("Handwerk zuerst", "Wir arbeiten nur fürs Handwerk. Noahs drei Brüder haben dort gelernt, zwei sind Meister."),
    ("Ehrlich", "Wir versprechen nur, was wir belegen können. Den Kunden und uns selbst."),
    ("Tempo", "Wir antworten am selben Tag und setzen um, statt wochenlang zu planen."),
    ("Klare Abläufe", "Skripte, feste Routinen und eigene KI-Werkzeuge nehmen dir Kleinkram ab."),
]
# „Was wir bieten“ (Noah, 21.11.2026: „geisteskrank nice darstellen, was wir bieten … Du kommst in ein geiles Team, das sich
# gegenseitig pusht, und man wächst gegenseitig“)
IC_WACHSEN = '<path d="M4 18 10 12l4 4 6-8"/><path d="M15 8h5v5"/>'
IC_INHABER = '<circle cx="12" cy="8" r="3.5"/><path d="M5 20a7 7 0 0 1 14 0"/>'
IC_KI = '<rect x="4" y="6" width="16" height="12" rx="3"/><path d="M9 11v2M15 11v2M12 3v3"/>'
ABLAUF = [
    ("Schnellbewerbung", "Zwei Minuten, ohne Anschreiben und Lebenslauf."),
    ("Kurzer Anruf", "Noah ruft dich an, damit ihr euch kennenlernt."),
    ("Video-Gespräch", "Wir gehen die Stelle im Detail durch, du stellst deine Fragen."),
    ("Probephase und Start", "Du legst los, und nach der Probephase entscheiden wir beide."),
]
FRAGEN = [
    ("Brauche ich Erfahrung?", "Für die Opener-Stelle nicht, du wirst eingearbeitet. Im Account Management hilft Erfahrung mit Meta-Ads, im Backoffice Erfahrung im Büro."),
    ("Wo arbeite ich?", "Von wo du willst. Wir arbeiten komplett remote, Noah selbst ist viel unterwegs."),
    ("Wie wird bezahlt?", "Als Opener bekommst du ein Fixum, dazu Provision pro erschienenem Termin und pro Abschluss. Die beiden anderen Stellen haben eine feste Vergütung. Die Zahlen nennen wir dir im ersten Gespräch."),
    ("Muss ich einen Lebenslauf schicken?", "Nein. Ein paar kurze Fragen im Formular reichen, den Rest klären wir am Telefon."),
    ("Was passiert nach dem Absenden?", "Deine Bewerbung landet direkt bei Noah. Er meldet sich bei dir am Telefon oder per Mail."),
]


def main_html():
    stellen = "".join(stelle(i, s) for i, s in enumerate(STELLEN))
    werte = "".join(f'<article class="kr-wert reveal"><span class="kr-wnr">0{i + 1}</span><h3>{t}</h3><p>{x}</p></article>'
                    for i, (t, x) in enumerate(WERTE))
    ic = lambda d: f'<span class="kr-ic"><svg viewBox="0 0 24 24" aria-hidden="true">{d}</svg></span>'
    bieten = (
        '<article class="kb kb-a reveal"><img src="/static/assets/img/karriere/a-calls-1400.webp" alt="Call mit Laptop am Strand" loading="lazy" decoding="async">'
        '<span class="kr-verlauf" aria-hidden="true"></span><div class="kb-text"><span class="kb-kicker">100 % remote</span><h3>Arbeite von überall.</h3>'
        '<p>Du brauchst einen Laptop, gutes Internet und den Anspruch, Ergebnisse zu liefern. Von wo aus, ist uns egal.</p></div></article>'
        '<article class="kb kb-zahl reveal"><b class="kb-gross">150+</b><h3>Betriebe betreut</h3><p>Ein ehrliches Produkt, das für die Betriebe funktioniert.</p></article>'
        '<article class="kb kb-zahl reveal"><b class="kb-gross">5,0<span>★</span></b><h3>Sterne bei Google</h3><p>Bei über 50 Bewertungen von unseren Kunden.</p></article>'
        '<article class="kb kb-team reveal"><span class="kb-kicker">Das Team</span><h3>Ein Kern-Team, das sich gegenseitig pusht.</h3>'
        '<p>Klein, schnell und jeder gibt Gas. Wenn einer rausfindet, was funktioniert, kriegen es alle mit. So wächst jeder über sich hinaus.</p></article>'
        f'<article class="kb reveal">{ic(IC_WACHSEN)}<h3>Du wächst mit</h3><p>Wer Gas gibt, übernimmt schnell mehr Verantwortung.</p><span class="kb-leiter"><span>Opener</span><i>→</i><span>Setter</span><i>→</i><span>Closer</span></span></article>'
        f'<article class="kb reveal">{ic(IC_INHABER)}<h3>1-zu-1 mit Noah</h3><p>Step by step an die Hand genommen, mit Wissen aus fünfstelligen Coachings.</p></article>'
        f'<article class="kb kb-breit reveal">{ic(IC_KI)}<h3>Viel läuft automatisch</h3><p>Unsere KI-Agents übernehmen einen großen Teil vom Kleinkram. Du kümmerst dich um das, was wirklich zählt.</p>'
        '<span class="kb-chips"><span>CRM</span><span>Automationen</span><span>KI-Agents</span></span></article>')
    ablauf = "".join(f'<li class="kr-schritt reveal"><span class="kr-snr">{i + 1}</span><h3>{t}</h3><p>{x}</p></li>'
                     for i, (t, x) in enumerate(ABLAUF))
    du = ('<article class="team-karte reveal"><div class="tk-bild"><img src="/static/assets/img/team/team-rudolf.webp" alt="Rudolf" width="800" height="1000" loading="lazy" decoding="async">'
          '<div class="tk-name"><b>Rudolf</b><span>Websites &amp; Anzeigen</span></div></div><p>Baut die Seiten und Anzeigen.</p></article>'
          f'<a class="team-karte team-du kr-du reveal" href="#bewerben"><div class="tk-bild"><img src="/static/assets/img/team/team-du.webp" alt="" width="800" height="1000" loading="lazy" decoding="async">'
          f'<div class="tk-name"><b>Du?</b><span>Dein Platz im Team</span></div></div><p class="tk-knopf">Jetzt bewerben {PFEIL}</p></a>')
    KENNEN = [
        ("mission", "Unsere Mission", "Wir sorgen dafür, dass Handwerksbetriebe online gefunden werden und neue Kunden & Mitarbeiter bekommen.", "Noah mit einem Kunden auf dem Betriebshof", "50% 30%"),
        ("geschichte", "Unsere Geschichte", "Noah kommt selbst aus einer Handwerkerfamilie und hat die HandwerksManufaktur 2019 gegründet. Mittlerweile haben wir über 150 Betriebe betreut.", "Noah am Laptop", "60% 35%"),
        ("setup", "Unser Setup", "Wir arbeiten komplett remote. Wo du sitzt, ist im Endeffekt egal, Hauptsache die Ergebnisse passen.", "Arbeitsplatz mit Laptop am Strand", "50% 50%"),
        ("kultur", "Unsere Kultur", "Wir bauen ein Team aus A-Playern, die Vollgas geben und sich gegenseitig pushen. Feedback gibt’s bei uns direkt und ehrlich.", "Noah und ein Kollege lachen beim gemeinsamen Arbeiten", "50% 40%"),
    ]
    kennen = ('<section class="sek kr-kennen-sek" id="kennenlernen"><div class="wrap"><div class="kopfzeile mitte reveal"><span class="kicker">Lerne uns kennen</span>'
              '<h2>Wir sind die HandwerksManufaktur.</h2></div><div class="kr-kennen">' + "".join(
                  f'<article class="kr-kk reveal"><figure><img src="/static/assets/img/karriere/a-{k}-800.webp" alt="{alt}" loading="lazy" decoding="async" style="object-position:{pos}"></figure>'
                  f'<h3>{titel}</h3><p>{text}</p></article>' for k, titel, text, alt, pos in KENNEN) + '</div></div></section>')
    # Noah, 21.11.2026: „rechts noch krassere Sachen … die Sektion ist bisschen zu simpel“ → je Zeile: was im normalen Job nervt, daneben wie es bei uns ist
    PAARE = [("Jeden Tag eine Stunde Stau auf dem Weg ins Büro.", "Laptop auf und los, egal von wo du arbeitest."),
             ("Stempeln um 8, Feierabend erst, wenn der Chef geht.", "Feste Kernzeiten, den Rest teilst du dir selbst ein."),
             ("Ein Gehalt, das gleich bleibt, egal was du leistest.", "Mehr Leistung heißt bei uns auch mehr Geld."),
             ("Kollegen, die nur Dienst nach Vorschrift machen.", "Ein Team, das Bock hat und sich gegenseitig pusht."),
             ("Eine Schulung im Jahr, wenn das Budget reicht.", "Wissen aus fünfstelligen Coaching-Invests."),
             ("Leadlisten, die schon zehnmal abtelefoniert wurden.", "Ein Skript, das funktioniert, und ein klarer Ablauf."),
             ("Ein Produkt, für das du dich am Telefon schämst.", "Echte Lösungen für gestandene Unternehmen.")]
    x_ic = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>'
    vergleich = ('<section class="sek kr-vgl-sek"><div class="wrap"><div class="kopfzeile mitte reveal"><span class="kicker">Gut zu wissen</span>'
                 '<h2>Was dich bei uns erwartet.</h2></div><div class="kr-vgl">'
                 '<div class="kr-vgl-kopf" aria-hidden="true"><span>Im normalen Job</span><i></i><span>Bei uns</span></div>'
                 + "".join(f'<div class="kr-paar"><p class="alt">{x_ic}<span><b>{alt}</b></span></p>'
                           f'<i class="pfeil" aria-hidden="true">{PFEIL}</i><p class="neu">{HAKEN}<span>{neu}</span></p></div>'
                           for alt, neu in PAARE) +
                 '</div></div></section>')
    wen = ('<section class="sek kr-wen-sek"><div class="wrap"><div class="duo"><div class="text reveal"><span class="kicker">Wen wir suchen</span>'
           '<h2>Leute, die richtig gut sein wollen.</h2>'
           '<p class="lead">Erfahrung ist schön, aber kein Muss. Wichtiger ist, dass du Bock hast und dranbleibst.</p>'
           + liste(["Du gibst Vollgas, auch wenn’s mal zäh wird.", "Du übernimmst Verantwortung für deine Ergebnisse.",
                    "Du hast Bock auf ein Team, das sich gegenseitig pusht."]) +
           f'<div class="knopfzeile"><a class="btn btn-bronze" href="#stellen">Offene Stellen ansehen {PFEIL}</a></div></div>'
           '<div class="bild reveal auf"><img src="/static/assets/img/karriere/a-pool-1400.webp" alt="Laptop am Pool mit Blick ins Grüne" loading="lazy" style="object-position:50% 60%"></div></div></div></section>')
    fragen = "".join(f'<details{" open" if i == 0 else ""}><summary>{q}{PLUS}</summary><p>{a}</p></details>' for i, (q, a) in enumerate(FRAGEN))
    wahl = "".join(f'<label class="kq-opt"><input type="radio" name="stelle" value="{s["titel"]}" data-id="{s["id"]}"><span>{s["kurz"]}</span></label>'
                   for s in STELLEN) + '<label class="kq-opt"><input type="radio" name="stelle" value="Initiativbewerbung" data-id="initiativ"><span>Initiativ</span></label>'
    return f'''<main id="inhalt"><section class="hero-klein hk-neu hk-karriere"><div class="hk-film" aria-hidden="true"><div class="hk-lage an hk-einzel"><video class="hk-desk" muted loop playsinline preload="none" data-hand data-src="/static/assets/vid/karriere/hero-d.mp4" poster="/static/assets/vid/karriere/hero-d.jpg"></video><video class="hk-mobil" muted loop playsinline preload="none" data-hand data-src="/static/assets/vid/karriere/hero-m.mp4" poster="/static/assets/vid/karriere/hero-m.jpg"></video></div></div><button class="pause" aria-label="Video anhalten"><svg class="zu" viewBox="0 0 24 24"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg><svg class="an" viewBox="0 0 24 24"><path d="M7 5v14l11-7z"/></svg></button>
<div class="wrap"><nav class="brot" aria-label="Pfad"><a href="/">Start</a><span>›</span><span>Karriere</span></nav><span class="kicker">Karriere</span><h1>Arbeite von überall. Fürs Handwerk.</h1><p class="lead">Wir bauen gerade ein kleines Kern-Team auf. Mit Leuten, die richtig Gas geben, frei arbeiten wollen und Bock haben, über sich hinauszuwachsen.</p><div class="knopfzeile"><a class="btn btn-bronze" href="#stellen">Offene Stellen ansehen {PFEIL}</a><a class="btn btn-umriss" href="#kennenlernen">Lerne uns kennen</a></div><div class="hero-fakten"><span><span class="stern">★★★★★</span> <b>5,0</b> auf Google</span><span><b>150+</b> Betriebe</span><span><b>100 %</b> remote</span></div></div></section>
{kennen}
<section class="sek band auf-dunkel kr-vorteile-sek"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Was wir bieten</span><h2>Deine Vorteile bei uns.</h2></div><div class="kr-bieten">{bieten}</div></div></section>
{vergleich}
{wen}
<section class="sek kr-stellen-sek" id="stellen"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Offene Stellen</span><h2>Hier steigst du ein.</h2><p class="lead">Lebenslauf ist uns egal. Wichtig ist, dass du Gas gibst.</p></div><div class="kr-stellen">{stellen}</div><p class="kr-initiativ reveal">Nichts Passendes dabei, aber du hast richtig Bock? Dann bewirb dich einfach initiativ. <a href="#bewerben" data-stelle="initiativ">Initiativ bewerben {PFEIL}</a></p></div></section>
<section class="sek grund kr-ablauf-sek" id="ablauf"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">So läuft die Bewerbung</span><h2>So kommst du zu uns.</h2></div><ol class="kr-ablauf">{ablauf}</ol></div></section>
<section class="sek team-sek kr-team-sek" id="team"><div class="wrap"><div class="kopfzeile mitte reveal"><span class="kicker">Das Team</span><h2>Hier ist noch Platz.</h2></div><div class="kr-team"><article class="team-karte reveal"><div class="tk-bild"><img data-k='[[0.2928,0.0166,0.4037,0.4099]]' src="/static/assets/img/team/team-noah-gross.webp" alt="Noah" width="800" height="1000" loading="lazy" decoding="async"><div class="tk-name"><b>Noah</b><span>Inhaber</span></div></div><p>Arbeitet dich persönlich ein.</p></article><article class="team-karte reveal"><div class="tk-bild"><img data-k='[[0.2363,0.0431,0.2914,0.2959]]' src="/static/assets/img/team/team-robert-gross.webp" alt="Robert" width="800" height="1000" loading="lazy" decoding="async"><div class="tk-name"><b>Robert</b><span>Shooting &amp; Schnitt</span></div></div><p>Dreht bei den Betrieben vor Ort.</p></article>{du}</div></div></section>
<section class="sek kr-bewerben-sek auf-dunkel" id="bewerben"><img class="kr-bhg" src="/static/assets/img/karriere/sonnenuntergang-1600.webp" alt="" loading="lazy" decoding="async"><div class="wrap"><div class="kr-bewerben"><div class="kr-btext reveal"><span class="kicker">Schnellbewerbung</span><h2>Bewirb dich in zwei Minuten.</h2><p class="lead">Ein paar kurze Fragen, dauert eine Minute. Deine Bewerbung landet direkt bei Noah.</p><p class="kr-direkt"><a href="tel:+4981947174990">{TEL} +49 8194 7174990</a><a href="mailto:info@handwerksmanufaktur.digital">{MAIL} info@handwerksmanufaktur.digital</a></p></div>
<form class="kr-form kr-quiz reveal" action="#" method="post" novalidate><input type="hidden" name="access_key" value="9a4e6ba4-58e9-4782-8953-e53eed867640"><input type="hidden" name="subject" value="Neue Bewerbung über handwerksmanufaktur.digital"><input type="hidden" name="from_name" value="HWM-Seite · Bewerbung"><input type="checkbox" name="botcheck" class="rd-honig" tabindex="-1" autocomplete="off" aria-hidden="true">
<button type="button" class="kq-zurueck" hidden>{ZURUECK} Zurück</button>
<fieldset class="kq-schritt an" data-k="stelle"><legend>Für welche Stelle willst du dich bewerben?</legend><div class="kq-wahl">{wahl}</div></fieldset>
<fieldset class="kq-schritt" data-k="name" hidden><legend>Wie heißt du?</legend><div class="kq-zeile"><input type="text" name="name" autocomplete="name" placeholder="Vor- und Nachname"><button type="button" class="btn btn-bronze kq-weiter">Weiter {PFEIL}</button></div></fieldset>
<fieldset class="kq-schritt" data-k="telefon" hidden><legend>Unter welcher Nummer erreichen wir dich?</legend><div class="kq-zeile"><input type="tel" name="telefon" autocomplete="tel" inputmode="tel" placeholder="z. B. 0170 1234567"><button type="button" class="btn btn-bronze kq-weiter">Weiter {PFEIL}</button></div></fieldset>
<fieldset class="kq-schritt" data-k="email" hidden><legend>Und deine E-Mail-Adresse?</legend><div class="kq-zeile"><input type="email" name="email" autocomplete="email" inputmode="email" placeholder="name@beispiel.de"><button type="button" class="btn btn-bronze kq-weiter">Weiter {PFEIL}</button></div></fieldset>
<fieldset class="kq-schritt" data-k="start" hidden><legend>Ab wann könntest du starten?</legend><div class="kq-wahl kq-drei"><label class="kq-opt"><input type="radio" name="start" value="Sofort"><span>Sofort</span></label><label class="kq-opt"><input type="radio" name="start" value="In 2–4 Wochen"><span>In 2–4 Wochen</span></label><label class="kq-opt"><input type="radio" name="start" value="In 1–3 Monaten"><span>In 1–3 Monaten</span></label></div></fieldset>
<fieldset class="kq-schritt" data-k="aktuell" hidden><legend>Was machst du gerade beruflich?</legend><div class="kq-wahl"><label class="kq-opt"><input type="radio" name="aktuell" value="Angestellt"><span>Angestellt</span></label><label class="kq-opt"><input type="radio" name="aktuell" value="Selbstständig"><span>Selbstständig</span></label><label class="kq-opt"><input type="radio" name="aktuell" value="Studium oder Ausbildung"><span>Studium oder Ausbildung</span></label><label class="kq-opt"><input type="radio" name="aktuell" value="Gerade auf der Suche"><span>Gerade auf der Suche</span></label></div></fieldset>
<div class="kq-fertig" hidden><b>Geschafft, danke!</b><span>Noah meldet sich persönlich bei dir.</span></div>
<p class="kq-fehler" hidden></p>
<div class="kq-fuss"><div class="kq-balken" aria-hidden="true"><i></i></div><span class="kq-stand">Fast geschafft</span></div>
<p class="kr-ds">Mit dem Absenden nutzen wir deine Angaben nur für deine Bewerbung. Mehr in der <a href="/datenschutz/">Datenschutzerklärung</a>.</p></form></div></div></section>
<section class="sek faq"><div class="wrap"><div class="zwei"><div class="links reveal"><span class="kicker">Häufige Fragen</span><h2>Was Bewerber oft fragen.</h2>
<div class="anker"><p>Noch etwas offen? Ruf an, am Telefon bist du direkt bei Noah.</p><a class="btn btn-tinte" href="tel:+4981947174990">{TEL} +49 8194 7174990</a></div></div><div class="reveal">{fragen}</div></div></div></section></main>'''


STIL = """<style>
.kr-stellen{display:grid;gap:14px}
.kr-stelle{background:#fff;border-radius:var(--radius);box-shadow:0 0 0 1px rgba(22,19,14,.08);transition:box-shadow var(--schnell),transform var(--schnell)}
.kr-stelle:hover{box-shadow:0 0 0 1px rgba(200,135,58,.55),0 18px 40px -24px rgba(22,19,14,.35);transform:translateY(-2px)}
.kr-stelle[open]{box-shadow:0 0 0 2px var(--bronze),0 24px 50px -30px rgba(22,19,14,.4);transform:none}
.kr-stelle summary{list-style:none;cursor:pointer;display:grid;grid-template-columns:auto 1fr auto;gap:clamp(16px,2.4vw,36px);align-items:center;padding:clamp(22px,2.6vw,34px) clamp(20px,2.8vw,40px)}
.kr-stelle summary::-webkit-details-marker{display:none}
.kr-nr{font-size:clamp(34px,4vw,56px);font-weight:800;letter-spacing:-.05em;color:var(--bronze);line-height:1;font-variant-numeric:tabular-nums}
.kr-kopf{display:grid;gap:6px;min-width:0}
.kr-bereich{font-size:13px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--bronze-tief)}
.kr-kopf h3{margin:0;font-size:clamp(22px,2.3vw,32px);line-height:1.15;letter-spacing:-.025em}
.kr-satz{color:var(--tinte-3);font-size:16px;line-height:1.5}
.kr-fakten{display:flex;flex-wrap:wrap;gap:8px;margin-top:6px}
.kr-fakten span{padding:6px 12px;border-radius:var(--pille);background:var(--papier-2);font-size:13.5px;font-weight:600;color:var(--tinte-2)}
.kr-auf .plus{display:grid;place-items:center;width:46px;height:46px;border-radius:50%;background:var(--papier-2);transition:transform var(--schnell),background var(--schnell)}
.kr-auf .plus svg{width:20px;height:20px;stroke:currentColor;fill:none;stroke-width:2.2}
.kr-stelle:hover .kr-auf .plus{background:var(--bronze-hauch)}
.kr-stelle[open] .kr-auf .plus{transform:rotate(45deg);background:var(--bronze);color:#fff}
.kr-inhalt{padding:0 clamp(20px,2.8vw,40px) clamp(24px,3vw,40px);display:grid;gap:26px;justify-items:start}
.kr-spalten{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:clamp(18px,2.6vw,40px);border-top:1px solid var(--linie);padding-top:clamp(20px,2.4vw,30px);width:100%}
.kr-spalten h4{margin:0 0 14px;font-size:16px;font-weight:800;letter-spacing:-.01em}
.kr-spalten ul,.kr-vorteil ul{list-style:none;margin:0;padding:0;display:grid;gap:11px}
.kr-spalten li{display:grid;grid-template-columns:20px 1fr;gap:10px;font-size:15.5px;line-height:1.5;color:var(--tinte-2)}
.kr-spalten li svg{width:20px;height:20px;margin-top:2px;stroke:var(--bronze);fill:none;stroke-width:2.4}
.kr-werte{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:var(--gap)}
.kr-wert{background:var(--papier);border-radius:var(--radius);padding:var(--pad);display:grid;align-content:start;gap:10px;transition:transform var(--schnell),box-shadow var(--schnell)}
.kr-wert:hover{transform:translateY(-4px);box-shadow:0 18px 40px -26px rgba(22,19,14,.4)}
.kr-wnr{font-size:14px;font-weight:700;color:var(--bronze-tief);letter-spacing:.06em}
.kr-wert h3{margin:0;font-size:clamp(20px,1.8vw,24px);letter-spacing:-.02em;line-height:1.2}
.kr-wert p{margin:0;color:var(--tinte-3);font-size:15.5px;line-height:1.55}
.kr-vorteile{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:var(--gap)}.kr-vorteil.kr-vgross{align-content:end}.kr-vgross{grid-column:span 2;grid-row:span 2;position:relative;overflow:hidden;padding:0;min-height:520px;align-content:end}.kr-vgross img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:86% 50%;transition:transform .8s var(--ease)}.kr-vgross:hover img{transform:scale(1.04)}.kr-verlauf{position:absolute;inset:0;z-index:1;background:linear-gradient(180deg,rgba(22,19,14,0) 30%,rgba(22,19,14,.55) 60%,rgba(22,19,14,.92))}.kr-vtext{z-index:2!important}.kr-vtext{position:relative;z-index:1;padding:var(--pad);display:grid;gap:12px}.kr-vgross h3{font-size:clamp(26px,2.6vw,36px)}.kr-vgross p{color:#E6DFD1;max-width:38ch}
.kr-vorteil{background:#1F1B14;border-radius:var(--radius);padding:var(--pad);display:grid;align-content:start;gap:12px;box-shadow:inset 0 0 0 1px rgba(250,247,241,.06);transition:background var(--schnell),transform var(--schnell)}
.kr-vorteil:hover{background:#2A251D;transform:translateY(-4px)}
.kr-ic{display:grid;place-items:center;width:48px;height:48px;border-radius:14px;background:rgba(200,135,58,.16);color:var(--bronze-hell)}
.kr-ic svg{width:24px;height:24px;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
.kr-vorteil h3{margin:4px 0 0;font-size:clamp(19px,1.7vw,23px);letter-spacing:-.02em;color:var(--papier);line-height:1.2}
.kr-vorteil p{margin:0;color:#CFC7B8;font-size:15.5px;line-height:1.55}
.kr-ablauf{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:var(--gap);counter-reset:s;position:relative}
.kr-schritt{position:relative;background:var(--papier);border-radius:var(--radius);padding:var(--pad);display:grid;align-content:start;gap:10px;transition:transform var(--schnell)}
.kr-schritt:hover{transform:translateY(-4px)}
.kr-snr{display:grid;place-items:center;width:44px;height:44px;border-radius:50%;background:var(--tinte);color:var(--papier);font-weight:800;font-size:17px}
.kr-schritt:first-child .kr-snr{background:var(--bronze)}
.kr-schritt h3{margin:6px 0 0;font-size:clamp(19px,1.7vw,22px);letter-spacing:-.02em}
.kr-schritt p{margin:0;color:var(--tinte-3);font-size:15.5px;line-height:1.55}
.kr-bewerben-sek{position:relative;overflow:hidden;background:var(--tinte);color:var(--papier)}.kr-bhg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.42}.kr-bewerben-sek::before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(22,19,14,.85),rgba(22,19,14,.35));z-index:0}.kr-bewerben-sek .wrap{position:relative;z-index:1}.kr-bewerben-sek .kr-btext h2{color:var(--papier)}.kr-bewerben-sek .kr-btext .lead{color:#E6DFD1}.kr-bewerben-sek .kr-direkt a{color:var(--papier)}.kr-bewerben-sek .kr-direkt svg{stroke:var(--bronze-hell)}.kr-wen-sek .text .lead+.lead{margin-top:16px}.kr-wen-sek ul{list-style:none;margin:8px 0 0;padding:0;display:grid;gap:12px}
.kr-wen-sek li{display:grid;grid-template-columns:22px 1fr;gap:10px;font-size:17px;line-height:1.5;font-weight:600;color:var(--tinte)}
.kr-wen-sek li svg{width:22px;height:22px;margin-top:2px;stroke:var(--bronze);fill:none;stroke-width:2.6}
.kr-bieten{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));grid-auto-rows:minmax(250px,auto);gap:var(--gap)}
.kb{position:relative;overflow:hidden;border-radius:var(--radius);background:#1F1B14;padding:var(--pad);display:flex;flex-direction:column;gap:12px;box-shadow:inset 0 0 0 1px rgba(250,247,241,.06);transition:transform .4s var(--ease),background .4s var(--ease)}
.kb:hover{transform:translateY(-5px);background:#2A251D}
.kb h3{margin:0;font-size:clamp(20px,1.8vw,24px);letter-spacing:-.02em;line-height:1.2;color:var(--papier)}.kb p{margin:0;color:#CFC7B8;font-size:15.5px;line-height:1.55}
.kb .kr-ic{margin-bottom:10px}
.kb-a{grid-column:1/3;grid-row:1/3;padding:0;justify-content:flex-end;min-height:540px}
.kb-a img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:86% 50%;transition:transform 1s var(--ease)}.kb-a:hover img{transform:scale(1.05)}
.kb-text{position:relative;z-index:2;padding:clamp(24px,3vw,40px);display:grid;gap:12px}.kb-a h3{font-size:clamp(34px,3.6vw,54px);letter-spacing:-.035em;line-height:1}.kb-a p{color:#EAE3D6;max-width:34ch;font-size:16.5px}
.kb-kicker{font-size:13px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--bronze-hell)}
.kb-gross{display:block;margin-bottom:14px;font-size:clamp(64px,6.4vw,104px);font-weight:800;letter-spacing:-.055em;line-height:.9;color:var(--bronze-hell)}.kb-gross span{font-size:.45em;margin-left:.08em;vertical-align:.7em}
.kb-team{grid-column:span 2;justify-content:flex-end;background:linear-gradient(135deg,#C8873A 0%,#8F5B1D 100%)}.kb-team:hover{background:linear-gradient(135deg,#D4954A 0%,#9B6524 100%)}
.kb-team h3{font-size:clamp(28px,2.8vw,42px);letter-spacing:-.03em;line-height:1.05;max-width:16ch}.kb-team p{color:#FFF3E2;max-width:46ch;font-size:16.5px}.kb-team .kb-kicker{color:#FFF3E2}
.kb-breit{grid-column:span 2}.kb-chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:4px}.kb-chips span{padding:7px 13px;border-radius:999px;background:rgba(250,247,241,.08);color:var(--papier);font-size:13.5px;font-weight:600}
@media (max-width:1100px){.kr-bieten{grid-template-columns:repeat(2,minmax(0,1fr))}.kb-a{grid-column:1/3;grid-row:auto;min-height:460px}}
@media (max-width:640px){.kr-bieten{grid-template-columns:1fr;grid-auto-rows:auto}.kb-a,.kb-team,.kb-breit{grid-column:auto}.kb{min-height:0}.kb.kb-a{min-height:440px}.kb .kr-ic,.kb-gross{margin-bottom:10px}}


.kr-kk:hover{transform:translateY(-6px);box-shadow:0 0 0 1px rgba(200,135,58,.5),0 22px 44px -28px rgba(22,19,14,.45)}


.kb-team img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 30%;opacity:.22;mix-blend-mode:luminosity;transition:opacity .5s var(--ease)}.kb-team:hover img{opacity:.32}.kb-team>*:not(img){position:relative;z-index:1}
.kr-kennen{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:var(--gap)}
.kr-kk{background:#fff;border-radius:var(--radius);padding:12px 12px 24px;box-shadow:0 0 0 1px rgba(22,19,14,.08);display:flex;flex-direction:column;gap:10px;transition:transform .35s var(--ease),box-shadow .35s var(--ease)}
.kr-kk figure{margin:0 0 8px;border-radius:calc(var(--radius) - 8px);overflow:hidden;aspect-ratio:4/3}.kr-kk img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .8s var(--ease)}.kr-kk:hover img{transform:scale(1.05)}
.kr-kk h3{margin:0 12px;font-size:clamp(21px,1.9vw,26px);letter-spacing:-.025em;line-height:1.15}.kr-kk p{margin:0 12px;color:var(--tinte-3);font-size:15.5px;line-height:1.55}
@media (max-width:1280px){.kr-kennen{grid-template-columns:repeat(2,minmax(0,1fr))}}@media (max-width:640px){.kr-kennen{grid-template-columns:1fr}}
.kb-leiter{display:flex;flex-wrap:nowrap;align-items:center;gap:2px;margin-top:4px;white-space:nowrap}.kb-leiter span{padding:5px 7px;font-size:13px!important;border-radius:999px;background:rgba(200,135,58,.16);color:var(--bronze-hell);font-size:13.5px;font-weight:700}.kb-leiter i{font-style:normal;color:var(--tinte-4)}
.kr-vgl{max-width:1080px;margin:0 auto;display:grid;gap:12px}
.kr-vgl-kopf,.kr-paar{display:grid;grid-template-columns:minmax(0,1fr) 52px minmax(0,1fr);align-items:stretch;gap:12px}
.kr-vgl-kopf span{font-size:13px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--tinte-4);padding:0 26px}
.kr-vgl-kopf span:last-child{color:var(--bronze-tief)}
.kr-paar p{margin:0;display:grid;grid-template-columns:22px 1fr;gap:14px;align-items:center;border-radius:var(--radius);padding:20px 26px;font-size:17px;line-height:1.45}
.kr-paar svg{width:22px;height:22px;fill:none;stroke-width:2.6}
.kr-paar .alt{background:var(--papier-2);color:var(--tinte-3)}.kr-paar .alt svg{stroke:var(--tinte-4)}
.kr-paar .alt b{font-weight:inherit;background:linear-gradient(var(--tinte-4),var(--tinte-4)) 0 58%/0 2px no-repeat}
.kr-paar .neu{background:#fff;color:var(--tinte);font-weight:600;box-shadow:0 0 0 2px var(--bronze),0 22px 44px -30px rgba(200,135,58,.6)}.kr-paar .neu svg{stroke:var(--bronze)}
.kr-paar .pfeil{display:grid;place-items:center;align-self:center;width:44px;height:44px;margin:auto;border-radius:50%;background:var(--bronze);color:#fff}
.kr-paar .pfeil svg{width:20px;height:20px;stroke:#fff;stroke-width:2.4}
@media (max-width:760px){.kr-vgl-kopf{display:none}.kr-vgl{gap:22px}.kr-paar{grid-template-columns:1fr;gap:8px}.kr-paar .pfeil{width:36px;height:36px;transform:rotate(90deg)}
 .kr-paar p{padding:16px 18px;font-size:16px}}
.kr-vgl-sek{overflow-x:clip}
/* Animation je Zeile (Noah, 21.11.2026: „das will ich mit geiler animation“): alt kommt, wird durchgestrichen, Pfeil, dann springt „Bei uns“ rein */
.kr-paar.anim .alt{opacity:0;transform:translateY(16px)}.kr-paar.anim .pfeil{opacity:0;transform:translateX(-14px) scale(.6)}.kr-paar.anim .neu{opacity:0;transform:translateX(-36px) scale(.94)}
.kr-paar.anim .neu svg path{stroke-dasharray:30;stroke-dashoffset:30}
.kr-paar .alt,.kr-paar .pfeil,.kr-paar .neu{transition:opacity .5s var(--ease),transform .7s cubic-bezier(.16,1,.3,1),color .4s ease}
.kr-paar .alt b{transition:background-size .55s cubic-bezier(.65,0,.35,1) .35s}.kr-paar .pfeil{transition-delay:.75s}.kr-paar .neu{transition-delay:.95s}
.kr-paar .neu svg path{transition:stroke-dashoffset .45s ease-out 1.35s}
@media (max-width:760px){.kr-paar.anim .pfeil{transform:translateY(-10px) rotate(90deg) scale(.6)}.kr-paar.anim .neu{transform:translateY(-16px) scale(.96)}}
.kr-paar.an .alt{opacity:1;transform:none;color:var(--tinte-4)}.kr-paar.an .alt b{background-size:100% 2px}.kr-paar.an .pfeil{opacity:1;transform:none}.kr-paar.an .neu{opacity:1;transform:none}.kr-paar.an .neu svg path{stroke-dashoffset:0}
@media (max-width:760px){.kr-paar.an .pfeil{transform:rotate(90deg)}}
@media (prefers-reduced-motion:reduce){.kr-paar .alt,.kr-paar .pfeil,.kr-paar .neu,.kr-paar .alt b,.kr-paar .neu svg path{transition:none!important}}
.kr-initiativ{margin:22px 0 0;font-size:16.5px;color:var(--tinte-3)}.kr-initiativ a{display:inline-flex;align-items:center;gap:6px;margin-left:6px;font-weight:700;color:var(--tinte);text-decoration:underline;text-underline-offset:4px}.kr-initiativ a svg{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:2}
.kr-quiz{gap:20px;min-height:420px;align-content:start}
.kq-schritt{border:0;margin:0;padding:0;min-width:0;display:grid;gap:18px;animation:kqrein .35s var(--ease)}@keyframes kqrein{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.kq-schritt legend{padding:0;margin:0 0 18px;font-size:clamp(22px,2.2vw,30px);font-weight:800;letter-spacing:-.025em;line-height:1.2;color:var(--tinte)}
.kq-wahl{display:grid;grid-template-columns:1fr 1fr;gap:12px}.kq-wahl.kq-drei{grid-template-columns:repeat(3,1fr)}
.kq-opt{position:relative;cursor:pointer}.kq-opt input{position:absolute;width:1px;height:1px;opacity:0;clip-path:inset(50%)}
.kq-opt span{display:flex;align-items:center;min-height:64px;padding:14px 18px;border-radius:16px;border:1.5px solid var(--linie);background:var(--papier);font-weight:700;font-size:16.5px;line-height:1.25;transition:border-color var(--schnell),background var(--schnell),transform var(--schnell)}
.kq-opt:hover span{border-color:var(--bronze);transform:translateY(-2px)}.kq-opt input:checked+span{background:var(--tinte);border-color:var(--tinte);color:var(--papier)}.kq-opt input:focus-visible+span{outline:2px solid var(--bronze);outline-offset:2px}
.kq-zeile{display:grid;grid-template-columns:1fr auto;gap:12px}.kq-zeile input{min-height:60px;border-radius:16px;border:1.5px solid var(--linie);background:var(--papier);padding:0 18px;font:inherit;font-size:17px;color:var(--tinte)}
.kq-zeile input:focus{outline:0;border-color:var(--bronze);background:#fff}.kq-zeile input.fehlt{border-color:#C0392B}.kq-zeile .btn{min-height:60px}
.kq-zurueck{justify-self:start;display:inline-flex;align-items:center;gap:6px;border:0;background:none;padding:6px 0;font:inherit;font-size:14.5px;font-weight:600;color:var(--tinte-3);cursor:pointer;min-height:44px}.kq-zurueck svg{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:2}
.kq-hinweis,.kq-fehler{margin:0;font-size:15px;font-weight:600;color:#A0322A}
.kq-fuss{display:grid;grid-template-columns:1fr auto;align-items:center;gap:14px;margin-top:6px}.kq-balken{height:8px;border-radius:999px;background:var(--papier-2);overflow:hidden}
.kq-balken i{display:block;height:100%;background:linear-gradient(90deg,var(--bronze),var(--bronze-hell));transform-origin:left;transform:scaleX(.38);transition:transform .5s var(--ease)}.kq-stand{font-size:13.5px;font-weight:700;color:var(--bronze-tief);white-space:nowrap}
.kq-fertig{display:grid;gap:6px;padding:24px;border-radius:16px;background:var(--bronze-hauch)}.kq-fertig b{font-size:22px}
@media (max-width:640px){.kq-wahl,.kq-wahl.kq-drei{grid-template-columns:1fr}.kq-zeile{grid-template-columns:1fr}.kr-quiz{min-height:0}}
@media (max-width:480px){.hk-karriere .hero-fakten{font-size:13.5px;gap:6px 12px}.hk-karriere .hero-fakten .stern{display:none}}
@media (min-width:901px){.kr-stellen-sek .kopfzeile>.lead{text-align:right;justify-self:end}}
.kr-team{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;max-width:1080px;margin:0 auto}
.kr-team .team-karte{padding:0 0 20px}
.kr-team .team-karte p{text-align:center;line-height:1.45;margin:16px 18px 0;padding:0!important;white-space:normal!important;font-size:15px;line-height:1.45;color:var(--tinte-3)}
.kr-team .tk-knopf{justify-content:center}
.kr-team .team-karte .tk-name b{font-size:clamp(22px,2vw,30px)}
.kr-bewerben{display:grid;grid-template-columns:.8fr 1.2fr;gap:clamp(32px,5vw,80px);align-items:start}
.kr-btext{position:sticky;top:calc(var(--kopf) + 24px);display:grid;gap:18px}
.kr-direkt{display:grid;gap:10px;margin:8px 0 0}
.kr-direkt a{display:inline-flex;align-items:center;gap:10px;font-weight:600;color:var(--tinte);min-height:44px}
.kr-direkt svg{width:20px;height:20px;stroke:var(--bronze-tief);fill:none;stroke-width:2}
.kr-form{color:var(--tinte);background:#fff;border-radius:var(--radius);box-shadow:0 0 0 1px rgba(22,19,14,.08),0 30px 60px -40px rgba(22,19,14,.35);padding:clamp(22px,3vw,40px);display:grid;gap:18px}
.kr-feld{display:grid;gap:8px;border:0;margin:0;padding:0;min-width:0}
.kr-feld>span,.kr-feld legend{font-size:15px;font-weight:700;color:var(--tinte);padding:0;line-height:1.4}
.kr-feld legend{margin-bottom:10px}
.kr-feld small{font-weight:500;color:var(--tinte-4)}
.kr-feld input:not([type=radio]){width:100%;min-height:52px;border-radius:14px;border:1.5px solid var(--linie);background:var(--papier);padding:0 16px;font:inherit;font-size:16px;color:var(--tinte);transition:border-color var(--schnell),background var(--schnell)}
.kr-feld input:not([type=radio]):hover{border-color:var(--tinte-4)}
.kr-feld input:not([type=radio]):focus{outline:0;border-color:var(--bronze);background:#fff}
.kr-feld input.fehlt,.kr-wahlfeld.fehlt .sf-chip span,.kr-zeiten.fehlt .sf-chip span{border-color:#C0392B!important}
.kr-zwei{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.kr-form .sf-wahl{display:flex;flex-wrap:wrap;gap:10px}
.kr-form .sf-chip{position:relative;cursor:pointer}
.kr-form .sf-chip input{position:absolute;width:1px;height:1px;margin:0;opacity:0;clip-path:inset(50%);pointer-events:none}
.kr-form .sf-chip span{display:inline-flex;align-items:center;min-height:46px;padding:0 18px;border-radius:var(--pille);border:1.5px solid var(--linie);background:var(--papier);font-weight:600;font-size:15px;transition:border-color var(--schnell),background var(--schnell),color var(--schnell)}
.kr-form .sf-chip:hover span{border-color:var(--bronze)}
.kr-form .sf-chip input:checked+span{background:var(--tinte);border-color:var(--tinte);color:var(--papier)}
.kr-form .sf-chip input:focus-visible+span{outline:2px solid var(--bronze);outline-offset:2px}
.kr-hinweis,.kr-fehler{margin:0;font-size:14.5px;color:#A0322A;font-weight:600}
.kr-senden{justify-self:start}.kr-bewerben-sek .kr-form .btn.kr-senden{background:var(--tinte)!important;color:var(--papier)!important;box-shadow:none!important}.kr-bewerben-sek .kr-form .btn.kr-senden:hover{background:var(--bronze-tief)!important}
.kr-ds{margin:0;font-size:13.5px;color:var(--tinte-4);line-height:1.5}
.kr-ds a{color:inherit;text-decoration:underline}
.kr-fertig{display:grid;gap:6px;padding:20px;border-radius:16px;background:var(--bronze-hauch)}
.kr-fertig b{font-size:18px}
.kr-form.gesendet>*:not(.kr-fertig){display:none}
@media (max-width:1100px){.kr-werte{grid-template-columns:repeat(2,minmax(0,1fr))}.kr-ablauf{grid-template-columns:repeat(2,minmax(0,1fr))}.kr-team{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:1100px){.kr-vorteile{grid-template-columns:repeat(2,minmax(0,1fr))}.kr-vgross{min-height:440px}}@media (max-width:900px){.kr-spalten,.kr-vorteile{grid-template-columns:1fr}.kr-vgross{grid-column:auto;grid-row:auto;min-height:420px}.kr-bewerben{grid-template-columns:1fr}.kr-btext{position:static}.dsk-br{display:none}}
@media (max-width:760px){.kr-stelle summary{grid-template-columns:1fr auto;align-items:start}.kr-nr{display:none}.kr-werte,.kr-ablauf{grid-template-columns:1fr}.kr-team{grid-template-columns:repeat(2,minmax(0,1fr))}.kr-zwei{grid-template-columns:1fr}.kr-senden{justify-self:stretch;justify-content:center}}
</style>"""

SKRIPT = r"""<script>
(()=>{const r=[...document.querySelectorAll('.kr-paar')];if(!r.length||!('IntersectionObserver' in window))return;r.forEach(x=>x.classList.add('anim'));
 const o=new IntersectionObserver(e=>e.forEach(x=>{if(x.isIntersecting){x.target.classList.add('an');o.unobserve(x.target)}}),{threshold:.6,rootMargin:'0px 0px -8% 0px'});r.forEach(x=>o.observe(x))})();
(()=>{const f=document.querySelector('.kr-quiz');if(!f)return;const $=(s,r=f)=>r.querySelector(s),$$=(s,r=f)=>[...r.querySelectorAll(s)];
const schritte=$$('.kq-schritt'),zur=$('.kq-zurueck'),bal=$('.kq-balken i'),stand=$('.kq-stand'),fehler=$('.kq-fehler');let weg=[0];
const idx=k=>schritte.findIndex(s=>s.dataset.k===k);
const reihe=()=>['stelle','name','telefon','email','start','aktuell'];
// Balken startet schon bei gut einem Drittel und wirkt weiter, als er ist
const zeig=i=>{schritte.forEach((s,j)=>{s.hidden=j!==i;s.classList.toggle('an',j===i)});const r=reihe(),pos=r.indexOf(schritte[i].dataset.k);
 const anteil=0.38+0.6*(pos/(r.length-1));bal.style.transform=`scaleX(${anteil})`;stand.textContent=pos>=r.length-2?'Fast geschafft':pos===0?'Dauert nur eine Minute':'Gleich geschafft';
 zur.hidden=weg.length<2;fehler.hidden=true;const e=$('input:not([type=radio])',schritte[i]);if(e&&matchMedia('(pointer:fine)').matches)e.focus({preventScroll:true})};
const weiter=()=>{const r=reihe(),k=schritte[weg[weg.length-1]].dataset.k,n=r[r.indexOf(k)+1];if(n){weg.push(idx(n));zeig(weg[weg.length-1])}else senden()};
zur.addEventListener('click',()=>{if(weg.length>1){weg.pop();zeig(weg[weg.length-1])}});
const telOk=v=>v.replace(/\D/g,'').length>=6&&/^[+()\d\s\/.-]+$/.test(v.trim()),mailOk=v=>/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim());
const pruef=s=>{const e=$('input:not([type=radio])',s);if(!e)return true;const v=e.value.trim();const ok=e.name==='telefon'?telOk(v):e.name==='email'?mailOk(v):v.length>2;
 e.classList.toggle('fehlt',!ok);if(!ok){fehler.textContent=e.name==='telefon'?'Bitte eine Telefonnummer eintragen.':e.name==='email'?'Bitte eine gültige E-Mail-Adresse eintragen.':'Bitte deinen Namen eintragen.';fehler.hidden=false;e.focus()}return ok};
$$('.kq-weiter').forEach(b=>b.addEventListener('click',()=>{if(pruef(b.closest('.kq-schritt')))weiter()}));
$$('.kq-schritt input:not([type=radio])').forEach(e=>e.addEventListener('keydown',ev=>{if(ev.key==='Enter'){ev.preventDefault();if(pruef(e.closest('.kq-schritt')))weiter()}}));
$$('.kq-opt input').forEach(r=>r.addEventListener('click',()=>{const s=r.closest('.kq-schritt');if(s.hidden)return;
 setTimeout(weiter,220)}));
const waehle=id=>{const i=$(`input[name=stelle][data-id="${id}"]`);if(!i)return;i.checked=true;weg=[0];weiter()};
document.querySelectorAll('[data-stelle]').forEach(a=>a.addEventListener('click',()=>waehle(a.dataset.stelle)));
async function senden(){const st=$('input[name=stelle]:checked');stand.textContent='Wird gesendet …';const fd=new FormData(f);fd.set('subject','Neue Bewerbung: '+(st?st.value:''));fd.append('Seite',location.pathname);
 try{const r=await fetch('https://api.web3forms.com/submit',{method:'POST',body:fd});if(!r.ok)throw 0}catch(x){fehler.textContent='Das hat nicht geklappt. Ruf gern direkt an: +49 8194 7174990';fehler.hidden=false;stand.textContent='Fast geschafft';return}
 schritte.forEach(s=>s.hidden=true);zur.hidden=true;$('.kq-fertig').hidden=false;bal.style.transform='scaleX(1)';stand.textContent='Geschafft';
 document.dispatchEvent(new CustomEvent('hwm:bewerbung',{detail:{stelle:st&&st.dataset.id}}))}
zeig(0);const h=location.hash.match(/^#bewerben-(\w+)/);if(h)waehle(h[1]);})();
</script>"""


def jobposting():
    org = {"@type": "Organization", "name": "HandwerksManufaktur Ltd.", "sameAs": "https://handwerksmanufaktur.digital/",
           "logo": "https://handwerksmanufaktur.digital/static/assets/img/favicon.svg"}
    jobs = []
    for s in STELLEN:
        text = (f"<p>{s['satz']}</p><p>Deine Aufgaben:</p><ul>" + "".join(f"<li>{x}</li>" for x in s["aufgaben"]) +
                "</ul><p>Das bringst du mit:</p><ul>" + "".join(f"<li>{x}</li>" for x in s["mitbringen"]) +
                "</ul><p>Das bekommst du:</p><ul>" + "".join(f"<li>{x}</li>" for x in s["bekommen"]) + "</ul>")
        jobs.append({"@context": "https://schema.org", "@type": "JobPosting", "title": s["titel"], "description": text,
                     "datePosted": "2026-11-21", "validThrough": "2027-03-31", "employmentType": s["jp_typ"],
                     "hiringOrganization": org, "jobLocationType": "TELECOMMUTE", "directApply": True,
                     "applicantLocationRequirements": [{"@type": "Country", "name": n} for n in ("Deutschland", "Österreich", "Schweiz")],
                     "url": f"https://handwerksmanufaktur.digital/karriere/#stelle-{s['id']}"})
    return '<script type="application/ld+json">' + json.dumps(jobs, ensure_ascii=False) + "</script>"


def bauen():
    h = (WURZEL / "ueber-uns/index.html").read_text(encoding="utf-8")
    alt_titel = re.search(r"<title>(.*?)</title>", h).group(1)
    alt_beschr = re.search(r'<meta name="description" content="([^"]*)"', h).group(1)
    h = h.replace(alt_titel, TITEL).replace(alt_beschr, BESCHR)
    h = h.replace("https://handwerksmanufaktur.digital/ueber-uns/", "https://handwerksmanufaktur.digital/karriere/")
    # Vorlade-Bilder von Über uns raus, das Hero-Standbild der Karriereseite rein
    h, n = re.subn(r'<link rel="preload" as="image"[^>]*>', "", h)
    assert n >= 1, n
    h = h.replace('<link rel="stylesheet" href="/static/seiten-neu.css',
                  '<link rel="preload" as="image" href="/static/assets/vid/karriere/hero-d.jpg" fetchpriority="high"><link rel="stylesheet" href="/static/seiten-neu.css', 1)
    h = h.replace('<a href="/ueber-uns/" class=aktiv>Über uns</a>', '<a href="/ueber-uns/">Über uns</a>')
    a, e = h.index('<main id="inhalt">'), h.index("</main>") + len("</main>")
    h = h[:a] + main_html() + h[e:]
    h = h.replace("</head>", STIL + jobposting() + "</head>", 1)
    h = h.replace("</body>", SKRIPT + "</body>", 1)
    h = fuss_neu(h)
    assert "class=aktiv" not in h and "ueber-uns/\"" not in h.split("<main", 1)[1].split("</main>")[0]
    ziel = WURZEL / "karriere/index.html"
    ziel.parent.mkdir(exist_ok=True)
    ziel.write_text(h, encoding="utf-8")
    print("✓ karriere/index.html", len(h))


if __name__ == "__main__":
    bauen()

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
        "aufgaben": ["Du rufst Inhaber von Handwerksbetrieben an, 150 bis 200 Anwahlen am Tag.",
                     "Du weckst Interesse und legst qualifizierte Termine in den Kalender unseres Sales-Teams.",
                     "Du hältst jeden Anruf sauber im CRM fest.",
                     "Läuft es gut, wirst du schnell Setter und später auch Closer."],
        "mitbringen": ["Täglich mindestens 5 Stunden aktiv am Telefon, Mo–Do zwischen 7 und 17 Uhr, Fr zwischen 7 und 13 Uhr.",
                       "Lust auf Kaltakquise und ein dickes Fell.",
                       "Ruhiger Arbeitsplatz, Headset und stabiles Internet.",
                       "Erfahrung im Vertrieb ist schön, aber kein Muss."],
        "bekommen": ["Fixum, dazu Provision pro erschienenem Termin und pro Abschluss.",
                     "Skripte, einen klaren Ablauf und Einarbeitung direkt durch Noah.",
                     "Ein Angebot, bei dem Termine leicht kommen: In einer Woche im September hat eine Person über 30 Termine gelegt."],
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
    ("Probetag und Start", "Du arbeitest einen Tag mit, danach entscheiden wir beide."),
]
FRAGEN = [
    ("Brauche ich Erfahrung?", "Für die Opener-Stelle nicht, du wirst eingearbeitet. Im Account Management hilft Erfahrung mit Meta-Ads, im Backoffice Erfahrung im Büro."),
    ("Wo arbeite ich?", "Von wo du willst. Wir arbeiten komplett remote, Noah selbst ist viel unterwegs."),
    ("Wie wird bezahlt?", "Als Opener bekommst du ein Fixum, dazu Provision pro erschienenem Termin und pro Abschluss. Die beiden anderen Stellen haben eine feste Vergütung. Die Zahlen nennen wir dir im ersten Gespräch."),
    ("Muss ich einen Lebenslauf schicken?", "Nein. Wenn du einen hast oder ein LinkedIn-Profil, kannst du im Formular einen Link angeben."),
    ("Was passiert nach dem Absenden?", "Deine Bewerbung landet direkt bei Noah. Er meldet sich bei dir am Telefon oder per Mail."),
]


def main_html():
    stellen = "".join(stelle(i, s) for i, s in enumerate(STELLEN))
    werte = "".join(f'<article class="kr-wert reveal"><span class="kr-wnr">0{i + 1}</span><h3>{t}</h3><p>{x}</p></article>'
                    for i, (t, x) in enumerate(WERTE))
    ic = lambda d: f'<span class="kr-ic"><svg viewBox="0 0 24 24" aria-hidden="true">{d}</svg></span>'
    bieten = (
        '<article class="kb kb-a reveal"><img src="/static/assets/img/karriere/a-calls-1400.webp" alt="Call mit Laptop am Strand" loading="lazy" decoding="async">'
        '<span class="kr-verlauf" aria-hidden="true"></span><div class="kb-text"><span class="kb-kicker">Freiheit</span><h3>Arbeite von überall.</h3>'
        '<p>Du brauchst Laptop, gutes Internet und den Anspruch zu liefern. Wir messen Ergebnisse, keine Stunden.</p></div></article>'
        '<article class="kb kb-zahl reveal"><b class="kb-gross">150+</b><h3>Betriebe betreut</h3><p>Du verkaufst und betreust etwas, das nachweislich funktioniert.</p></article>'
        '<article class="kb kb-zahl reveal"><b class="kb-gross">5,0<span>★</span></b><h3>Sterne bei Google</h3><p>Unsere Kunden empfehlen uns weiter.</p></article>'
        '<article class="kb kb-team reveal"><img src="/static/assets/img/karriere/a-team-1400.webp" alt="" loading="lazy" decoding="async"><span class="kb-kicker">Das Team</span><h3>Ein Team, das sich gegenseitig pusht.</h3>'
        '<p>Hier zieht keiner allein. Wir teilen, was funktioniert, geben uns ehrliches Feedback und werden zusammen jeden Monat besser.</p></article>'
        f'<article class="kb reveal">{ic(IC_WACHSEN)}<h3>Du wächst mit</h3><p>Wer liefert, übernimmt schnell mehr Verantwortung.</p><span class="kb-leiter"><span>Opener</span><i>→</i><span>Setter</span><i>→</i><span>Closer</span></span></article>'
        f'<article class="kb reveal">{ic(IC_INHABER)}<h3>1-zu-1 mit Noah</h3><p>Du wirst persönlich eingearbeitet und bekommst unser ganzes Wissen.</p></article>'
        f'<article class="kb kb-breit reveal">{ic(IC_KI)}<h3>Werkzeuge, die mitarbeiten</h3><p>Den Kleinkram erledigen unsere Systeme, du kümmerst dich um das, was zählt.</p>'
        '<span class="kb-chips"><span>CRM</span><span>Automationen</span><span>eigene KI-Agenten</span></span></article>')
    ablauf = "".join(f'<li class="kr-schritt reveal"><span class="kr-snr">{i + 1}</span><h3>{t}</h3><p>{x}</p></li>'
                     for i, (t, x) in enumerate(ABLAUF))
    du = "".join(f'<a class="team-karte team-du kr-du reveal" href="#bewerben" data-stelle="{s["id"]}"><div class="tk-bild">'
                 f'<img src="/static/assets/img/team/team-du.webp" alt="" width="800" height="1000" loading="lazy" decoding="async">'
                 f'<div class="tk-name"><b>Du?</b><span>{s["kurz"]}</span></div></div><p class="tk-knopf">Jetzt bewerben {PFEIL}</p></a>'
                 for s in STELLEN)
    KENNEN = [
        ("mission", "Unsere Mission", "Wir bringen Handwerksbetriebe online nach vorn: mit Websites, die Aufträge bringen, und Anzeigen, die Kunden und Mitarbeiter finden.", "Noah mit einem Kunden auf dem Betriebshof", "50% 30%"),
        ("geschichte", "Unsere Geschichte", "Noah kommt aus einer Handwerkerfamilie und hat 2019 angefangen. Heute betreuen wir über 150 Betriebe in Deutschland, Österreich und der Schweiz.", "Noah am Laptop", "60% 35%"),
        ("setup", "Unser Setup", "Komplett remote. Wo du arbeitest, ist deine Sache, solange die Ergebnisse stimmen. Freiheit und Verantwortung gehören bei uns zusammen.", "Arbeitsplatz mit Laptop am Strand", "50% 50%"),
        ("kultur", "Unsere Kultur", "Jeder trägt sein Ergebnis. Feedback ist Werkzeug, keine Strafe. Und wir pushen uns gegenseitig, statt Ellenbogen auszufahren.", "Noah und ein Kollege lachen beim gemeinsamen Arbeiten", "50% 40%"),
    ]
    kennen = ('<section class="sek kr-kennen-sek" id="kennenlernen"><div class="wrap"><div class="kopfzeile mitte reveal"><span class="kicker">Lerne uns kennen</span>'
              '<h2>Wir sind die HandwerksManufaktur.</h2></div><div class="kr-kennen">' + "".join(
                  f'<article class="kr-kk reveal"><figure><img src="/static/assets/img/karriere/a-{k}-800.webp" alt="{alt}" loading="lazy" decoding="async" style="object-position:{pos}"></figure>'
                  f'<h3>{titel}</h3><p>{text}</p></article>' for k, titel, text, alt, pos in KENNEN) + '</div></div></section>')
    JA = ["Ein Angebot, das funktioniert: über 150 Betriebe, 5,0 bei Google.", "Klare Ziele und Zahlen, an denen du dich messen kannst.",
          "Ehrliches Feedback, jede Woche.", "Freie Wahl, von wo du arbeitest.", "Aufstieg nach Leistung, nicht nach Dienstjahren."]
    NEIN = ["Stechuhr und Anwesenheitspflicht.", "Politik und Ellenbogen.", "Meetings, die zu nichts führen.",
            "Jemanden, der dir über die Schulter schaut.", "Ein Team, das sich mit Mittelmaß zufriedengibt."]
    x_ic = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>'
    vergleich = ('<section class="sek kr-vgl-sek"><div class="wrap"><div class="kopfzeile mitte reveal"><span class="kicker">Ehrlich gesagt</span>'
                 '<h2>Was du bei uns findest. Und was nicht.</h2></div><div class="kr-vgl">'
                 '<div class="kr-vgl-ja reveal"><h3>Das findest du bei uns</h3>' + liste(JA) + '</div>'
                 '<div class="kr-vgl-nein reveal"><h3>Das findest du nicht</h3><ul>' + "".join(f"<li>{x_ic}<span>{x}</span></li>" for x in NEIN) + '</ul></div>'
                 '</div></div></section>')
    wen = ('<section class="sek kr-wen-sek"><div class="wrap"><div class="duo"><div class="text reveal"><span class="kicker">Wen wir suchen</span>'
           '<h2>Leute, die richtig gut sein wollen.</h2>'
           '<p class="lead">Wir suchen keine Lebensläufe, sondern Leute, die liefern. Ob du schon Erfahrung hast, ist zweitrangig. Wichtig ist, dass du richtig gut werden willst.</p>'
           + liste(["Du gibst dich nicht mit Durchschnitt zufrieden.", "Du übernimmst Verantwortung für deine Ergebnisse.",
                    "Du hast Lust auf ein Team, das sich gegenseitig pusht."]) +
           f'<div class="knopfzeile"><a class="btn btn-bronze" href="#stellen">Offene Stellen ansehen {PFEIL}</a></div></div>'
           '<div class="bild reveal auf"><img src="/static/assets/img/karriere/a-pool-1400.webp" alt="Laptop am Pool mit Blick ins Grüne" loading="lazy" style="object-position:50% 60%"></div></div></div></section>')
    fragen = "".join(f'<details{" open" if i == 0 else ""}><summary>{q}{PLUS}</summary><p>{a}</p></details>' for i, (q, a) in enumerate(FRAGEN))
    wahl = "".join(f'<label class="sf-chip"><input type="radio" name="stelle" value="{s["titel"]}" data-id="{s["id"]}" required><span>{s["kurz"]}</span></label>'
                   for s in STELLEN)
    return f'''<main id="inhalt"><section class="hero-klein hk-neu hk-karriere"><div class="hk-film" aria-hidden="true"><div class="hk-lage an hk-einzel"><video class="hk-desk" muted loop playsinline preload="none" data-hand data-src="/static/assets/vid/karriere/hero-d.mp4" poster="/static/assets/vid/karriere/hero-d.jpg"></video><video class="hk-mobil" muted loop playsinline preload="none" data-hand data-src="/static/assets/vid/karriere/hero-m.mp4" poster="/static/assets/vid/karriere/hero-m.jpg"></video></div></div><button class="pause" aria-label="Video anhalten"><svg class="zu" viewBox="0 0 24 24"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg><svg class="an" viewBox="0 0 24 24"><path d="M7 5v14l11-7z"/></svg></button>
<div class="wrap"><nav class="brot" aria-label="Pfad"><a href="/">Start</a><span>›</span><span>Karriere</span></nav><span class="kicker">Karriere</span><h1>Arbeite von überall. Fürs Handwerk.</h1><p class="lead">Für Leute, die in ihrem Job richtig gut werden wollen<br class="dsk-br"> und dafür Freiheit statt Stechuhr bekommen.</p><div class="knopfzeile"><a class="btn btn-bronze" href="#stellen">Offene Stellen ansehen {PFEIL}</a><a class="btn btn-umriss" href="#kennenlernen">Lerne uns kennen</a></div><div class="hero-fakten"><span><span class="stern">★★★★★</span> <b>5,0</b> auf Google</span><span><b>seit 2019</b> nur Handwerk</span><span><b>150+</b> Betriebe</span><span><b>100 %</b> remote</span></div></div></section>
{kennen}
<section class="sek band auf-dunkel kr-vorteile-sek"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Was wir bieten</span><h2>Deine Vorteile bei uns.</h2></div><div class="kr-bieten">{bieten}</div></div></section>
{vergleich}
{wen}
<section class="sek kr-stellen-sek" id="stellen"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">Offene Stellen</span><h2>Hier steigst du ein.</h2><p class="lead">Kein Anschreiben, kein Lebenslauf nötig.</p></div><div class="kr-stellen">{stellen}</div></div></section>
<section class="sek grund kr-ablauf-sek" id="ablauf"><div class="wrap"><div class="kopfzeile reveal"><span class="kicker">So läuft die Bewerbung</span><h2>So kommst du zu uns.</h2></div><ol class="kr-ablauf">{ablauf}</ol></div></section>
<section class="sek team-sek kr-team-sek" id="team"><div class="wrap"><div class="kopfzeile mitte reveal"><span class="kicker">Das Team</span><h2>Hier ist noch Platz.</h2></div><div class="kr-team"><article class="team-karte reveal"><div class="tk-bild"><img data-k='[[0.2928,0.0166,0.4037,0.4099]]' src="/static/assets/img/team/team-noah-gross.webp" alt="Noah" width="800" height="1000" loading="lazy" decoding="async"><div class="tk-name"><b>Noah</b><span>Inhaber</span></div></div><p>Arbeitet dich persönlich ein.</p></article><article class="team-karte reveal"><div class="tk-bild"><img data-k='[[0.2363,0.0431,0.2914,0.2959]]' src="/static/assets/img/team/team-robert-gross.webp" alt="Robert" width="800" height="1000" loading="lazy" decoding="async"><div class="tk-name"><b>Robert</b><span>Shooting &amp; Schnitt</span></div></div><p>Dreht bei den Betrieben vor Ort.</p></article>{du}</div></div></section>
<section class="sek kr-bewerben-sek auf-dunkel" id="bewerben"><img class="kr-bhg" src="/static/assets/img/karriere/sonnenuntergang-1600.webp" alt="" loading="lazy" decoding="async"><div class="wrap"><div class="kr-bewerben"><div class="kr-btext reveal"><span class="kicker">Schnellbewerbung</span><h2>Bewirb dich in zwei Minuten.</h2><p class="lead">Kein Anschreiben, kein Lebenslauf. Deine Bewerbung landet direkt bei Noah.</p><p class="kr-direkt"><a href="tel:+4981947174990">{TEL} +49 8194 7174990</a><a href="mailto:info@handwerksmanufaktur.digital">{MAIL} info@handwerksmanufaktur.digital</a></p></div>
<form class="kr-form reveal" action="#" method="post" novalidate><input type="hidden" name="access_key" value="9a4e6ba4-58e9-4782-8953-e53eed867640"><input type="hidden" name="subject" value="Neue Bewerbung über handwerksmanufaktur.digital"><input type="hidden" name="from_name" value="HWM-Seite · Bewerbung"><input type="checkbox" name="botcheck" class="rd-honig" tabindex="-1" autocomplete="off" aria-hidden="true">
<fieldset class="kr-feld kr-wahlfeld"><legend>Für welche Stelle?</legend><div class="sf-wahl">{wahl}</div></fieldset>
<div class="kr-zwei"><label class="kr-feld"><span>Vor- und Nachname</span><input type="text" name="name" autocomplete="name" required></label><label class="kr-feld"><span>Telefonnummer</span><input type="tel" name="telefon" autocomplete="tel" inputmode="tel" placeholder="z. B. 0170 1234567" required></label></div>
<div class="kr-zwei"><label class="kr-feld"><span>E-Mail-Adresse</span><input type="email" name="email" autocomplete="email" inputmode="email" required></label><label class="kr-feld"><span>Ab wann kannst du starten?</span><input type="text" name="start" placeholder="z. B. sofort oder 1. Januar" required></label></div>
<label class="kr-feld"><span>Was machst du gerade beruflich?</span><input type="text" name="aktuell" placeholder="z. B. Vertrieb, Studium, Agentur" required></label>
<fieldset class="kr-feld kr-zeiten" hidden><legend>Kannst du Mo–Do zwischen 7 und 17 Uhr und Fr zwischen 7 und 13 Uhr täglich mindestens 5 Stunden telefonieren?</legend><div class="sf-wahl"><label class="sf-chip"><input type="radio" name="telefonzeit" value="Ja"><span>Ja</span></label><label class="sf-chip"><input type="radio" name="telefonzeit" value="Nein"><span>Nein</span></label></div><p class="kr-hinweis" hidden>Die Telefonzeit ist bei dieser Stelle Voraussetzung, weil wir die Betriebe nur dann erreichen.</p></fieldset>
<label class="kr-feld"><span>LinkedIn oder Lebenslauf <small>(freiwillig)</small></span><input type="url" name="link" inputmode="url" placeholder="Link einfügen"></label>
<p class="kr-fehler" hidden>Bitte fülle alle Felder aus und wähle eine Stelle.</p>
<button type="submit" class="btn btn-bronze kr-senden">Bewerbung abschicken {PFEIL}</button>
<p class="kr-ds">Mit dem Absenden nutzen wir deine Angaben nur für deine Bewerbung. Mehr in der <a href="/datenschutz/">Datenschutzerklärung</a>.</p>
<div class="kr-fertig" hidden><b>Danke für deine Bewerbung.</b><span>Noah meldet sich persönlich bei dir.</span></div></form></div></div></section>
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
.kr-kennen{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:var(--gap)}
.kr-kk{background:#fff;border-radius:var(--radius);padding:12px 12px 26px;box-shadow:0 0 0 1px rgba(22,19,14,.08);display:flex;flex-direction:column;gap:10px;transition:transform .35s var(--ease),box-shadow .35s var(--ease)}
.kr-kk:hover{transform:translateY(-6px);box-shadow:0 0 0 1px rgba(200,135,58,.5),0 22px 44px -28px rgba(22,19,14,.45)}
.kr-kk figure{margin:0 0 8px;border-radius:calc(var(--radius) - 8px);overflow:hidden;aspect-ratio:4/3}.kr-kk img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .8s var(--ease)}.kr-kk:hover img{transform:scale(1.05)}
.kr-kk h3{margin:0 12px;font-size:clamp(21px,1.9vw,26px);letter-spacing:-.025em;line-height:1.15}.kr-kk p{margin:0 12px;color:var(--tinte-3);font-size:15.5px;line-height:1.55}
.kb-team img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 30%;opacity:.22;mix-blend-mode:luminosity;transition:opacity .5s var(--ease)}.kb-team:hover img{opacity:.32}.kb-team>*:not(img){position:relative;z-index:1}
@media (max-width:1100px){.kr-kennen{grid-template-columns:repeat(2,minmax(0,1fr))}}@media (max-width:640px){.kr-kennen{grid-template-columns:1fr}}
.kr-vgl{display:grid;grid-template-columns:1fr 1fr;gap:var(--gap);max-width:1040px;margin:0 auto}
.kr-vgl>div{border-radius:var(--radius);padding:clamp(26px,3vw,44px);display:grid;align-content:start;gap:18px}
.kr-vgl-ja{background:#fff;box-shadow:0 0 0 2px var(--bronze)}.kr-vgl-nein{background:var(--papier-2)}
.kr-vgl h3{margin:0;font-size:clamp(22px,2vw,28px);letter-spacing:-.025em}
.kr-vgl ul{list-style:none;margin:0;padding:0;display:grid;gap:14px}.kr-vgl li{display:grid;grid-template-columns:22px 1fr;gap:12px;font-size:16.5px;line-height:1.5;color:var(--tinte-2)}
.kr-vgl li svg{width:22px;height:22px;margin-top:1px;fill:none;stroke-width:2.6}.kr-vgl-ja li svg{stroke:var(--bronze)}.kr-vgl-nein li svg{stroke:var(--tinte-4)}.kr-vgl-nein li span{color:var(--tinte-3)}
.kb-leiter{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin-top:4px}.kb-leiter span{padding:6px 12px;border-radius:999px;background:rgba(200,135,58,.16);color:var(--bronze-hell);font-size:13.5px;font-weight:700}.kb-leiter i{font-style:normal;color:var(--tinte-4)}
@media (max-width:760px){.kr-vgl{grid-template-columns:1fr}}
.kr-team{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:16px}
.kr-team .team-karte{padding:0 0 20px}
.kr-team .team-karte p{text-align:center;margin:16px 18px 0;font-size:15px;line-height:1.45;color:var(--tinte-3)}
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
@media (max-width:1100px){.kr-werte{grid-template-columns:repeat(2,minmax(0,1fr))}.kr-ablauf{grid-template-columns:repeat(2,minmax(0,1fr))}.kr-team{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media (max-width:1100px){.kr-vorteile{grid-template-columns:repeat(2,minmax(0,1fr))}.kr-vgross{min-height:440px}}@media (max-width:900px){.kr-spalten,.kr-vorteile{grid-template-columns:1fr}.kr-vgross{grid-column:auto;grid-row:auto;min-height:420px}.kr-bewerben{grid-template-columns:1fr}.kr-btext{position:static}.dsk-br{display:none}}
@media (max-width:760px){.kr-stelle summary{grid-template-columns:1fr auto;align-items:start}.kr-nr{display:none}.kr-werte,.kr-ablauf{grid-template-columns:1fr}.kr-team{grid-template-columns:repeat(2,minmax(0,1fr))}.kr-team>:first-child{grid-column:span 2}.kr-team>:first-child .tk-bild{aspect-ratio:16/11}.kr-zwei{grid-template-columns:1fr}.kr-senden{justify-self:stretch;justify-content:center}}
</style>"""

SKRIPT = """<script>
(()=>{const f=document.querySelector('.kr-form');if(!f)return;const $=(s,r=f)=>r.querySelector(s),$$=(s,r=f)=>[...r.querySelectorAll(s)];
const zeiten=$('.kr-zeiten'),hinweis=$('.kr-hinweis',zeiten),fehler=$('.kr-fehler');
const opener=()=>{const c=$('input[name=stelle]:checked');return c&&c.dataset.id==='opener'};
const pruefen=()=>{zeiten.hidden=!opener();if(!opener())$$('input[name=telefonzeit]').forEach(i=>i.checked=false);$$('input[name=telefonzeit]').forEach(i=>i.required=opener());hinweis.hidden=!(opener()&&$('input[name=telefonzeit][value=Nein]').checked)};
f.addEventListener('change',pruefen);
const waehle=id=>{const i=$(`input[name=stelle][data-id="${id}"]`);if(i){i.checked=true;pruefen()}};
document.querySelectorAll('[data-stelle]').forEach(a=>a.addEventListener('click',()=>waehle(a.dataset.stelle)));
const telOk=v=>v.replace(/\\D/g,'').length>=6&&/^[+()\\d\\s\\/.-]+$/.test(v.trim()),mailOk=v=>/^[^\\s@]+@[^\\s@]+\\.[^\\s@]{2,}$/.test(v.trim());
f.addEventListener('submit',async e=>{e.preventDefault();let ok=true;
 const st=$('input[name=stelle]:checked');$('.kr-wahlfeld').classList.toggle('fehlt',!st);if(!st)ok=false;
 $$('input[required]:not([type=radio])').forEach(i=>{const v=i.value.trim();const g=v.length>1&&(i.name!=='telefon'||telOk(v))&&(i.name!=='email'||mailOk(v));i.classList.toggle('fehlt',!g);if(!g)ok=false});
 if(opener()){const t=$('input[name=telefonzeit]:checked');zeiten.classList.toggle('fehlt',!t);if(!t)ok=false;if(t&&t.value==='Nein'){hinweis.hidden=false;ok=false}}
 fehler.hidden=ok;if(!ok){const x=$('.fehlt');if(x)x.scrollIntoView({block:'center',behavior:'smooth'});return}
 const k=$('.kr-senden');k.disabled=true;const fd=new FormData(f);fd.set('subject','Neue Bewerbung: '+st.value);fd.append('Seite',location.pathname);
 try{const r=await fetch('https://api.web3forms.com/submit',{method:'POST',body:fd});if(!r.ok)throw 0}catch(x){k.disabled=false;fehler.textContent='Das hat nicht geklappt. Ruf gern direkt an: +49 8194 7174990';fehler.hidden=false;return}
 f.classList.add('gesendet');$('.kr-fertig').hidden=false;document.dispatchEvent(new CustomEvent('hwm:bewerbung',{detail:{stelle:st.dataset.id}}));});
const h=location.hash.match(/^#bewerben-(\\w+)/);if(h)waehle(h[1]);})();
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

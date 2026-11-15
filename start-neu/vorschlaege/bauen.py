# Vorschlagsseite (noindex): immer NUR die aktuelle Runde, nie alte Listen mitliefern (Noah, 15.11.2026).
# Runde 7 (Noah mochte 6, 9, 20: Servus ich bin Noah + Brüder/Handwerksfirmen + ich weiß, wie es zugeht + abends keine Lust). Runde 6 (Aufbau nach Noah: Intro, Überleitung, einer der drei Familiensätze, Outro; Vorbild Felix auf zimmerei-partner.de, kürzer). Runde 5 (Runde 4 war Noah zu unauthentisch, Werbetexter-Sätze): Noahs eigene Sätze aus den Calls als Vorlage. Runde 4: komplette Über-uns-Sektionen (kleine Zeile, Überschrift, Text), HWM persönlich, SHK ohne Persönliches.
from pathlib import Path
import html
N = 'Noah Seelau, Gründer'
BLOECKE = [('Über uns · kleiner Satz unter der Überschrift', '/ueber-uns/ oben, unter „Du bist auf der Baustelle daheim. Wir im Internet.“ (live steht vorerst Nr. 1)', [('Unterzeile', '', 'Wir kümmern uns um Website, Anzeigen und Bewerbungen, damit du dich um deine Baustellen kümmern kannst.', ''), ('Unterzeile', '', 'Du sorgst für gute Arbeit. Wir sorgen dafür, dass man sie online sieht.', ''), ('Unterzeile', '', 'Wir bringen deinen Betrieb ins Internet und Kunden und Mitarbeiter zu dir.', ''), ('Unterzeile', '', 'Kleines Team, kurze Wege. Du sprichst von Anfang bis Ende mit denselben Leuten.', ''), ('Unterzeile', '', 'Wir bauen deine Website, schalten deine Anzeigen und holen dir Bewerbungen. Du machst dein Handwerk.', ''), ('Unterzeile', '', 'Wer wir sind, wie wir arbeiten und warum wir das Handwerk so gut kennen.', ''), ('Unterzeile', '', 'Hier liest du, wer wir sind und warum wir wissen, wie ein Betrieb tickt.', ''), ('Unterzeile', '', 'Damit dein Betrieb online so gut dasteht wie auf der Baustelle.', ''), ('Unterzeile', '', 'Wir reden mit dir wie mit einem von uns: klar und ohne Umwege.', ''), ('Unterzeile', '', 'Wir übernehmen das Marketing, damit mehr Zeit für deinen Betrieb bleibt.', '')])]
e = html.escape
def h(x):
    a, _, b = x.partition('|')
    return e(a) + (f'<br><em>{e(b)}</em>' if b else '')
out = ['<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Über-uns-Texte</title><style>'
 ':root{--ink:#0B1424;--sub:#4A5666;--line:#DCE3EC;--paper:#F3F6FA;--warm:#C9581A}*{box-sizing:border-box;margin:0;padding:0}body{background:var(--paper);color:var(--ink);font:17px/1.55 Inter,system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased}'
 '.wrap{max-width:760px;margin:0 auto;padding:32px 20px 96px}h1{font-size:clamp(30px,5vw,44px);letter-spacing:-.03em;line-height:1.1;margin-bottom:8px}.lead{color:var(--sub)}h2{font-size:24px;letter-spacing:-.02em;margin:56px 0 16px}h2 small{display:block;font-size:15px;font-weight:400;letter-spacing:0;color:var(--sub);margin-top:4px}'
 '.k{background:#fff;border:1px solid var(--line);border-radius:24px;padding:32px;margin-bottom:16px;position:relative}.nr{position:absolute;top:28px;right:32px;font-size:15px;font-weight:600;color:var(--sub)}.kl{font-size:14px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--warm);margin-bottom:16px}'
 '.k h3{font-size:clamp(28px,5vw,38px);line-height:1.1;letter-spacing:-.03em;margin-bottom:20px;text-wrap:balance}.k h3 em{font-style:italic;font-weight:500;color:var(--warm)}.k p{color:var(--sub);max-width:58ch}.k .sig{margin-top:20px;color:var(--ink);font-weight:600;font-size:15px}'
 '@media(max-width:560px){.k{padding:24px 20px}.nr{top:20px;right:20px}}'
 '</style></head><body><div class="wrap"><h1>Über-uns-Texte</h1><p class="lead">Nenn mir Seite und Nummer.</p>']
for titel, dom, liste in BLOECKE:
    out.append(f'<h2>{e(titel)}<small>{e(dom)}</small></h2>')
    for i, (kl, hh, tx, sig) in enumerate(liste, 1):
        out.append(f'<div class="k"><span class="nr">{i}</span><div class="kl">{e(kl)}</div>' + (f'<h3 style="margin-bottom:0">{h(hh)}</h3>' if hh else '') + (f'<p>{e(tx)}</p>' if tx else '') + (f'<p class="sig">{e(sig)}</p>' if sig else '') + '</div>')
out.append('</div></body></html>')
s = ''.join(out)
assert '–' not in s and '—' not in s and 'sondern' not in s and 'komme aus einer' not in s and 'keine Lust' not in s
Path(__file__).with_name('index.html').write_text(s)
print(sum(len(l) for _, _, l in BLOECKE), 'Texte')

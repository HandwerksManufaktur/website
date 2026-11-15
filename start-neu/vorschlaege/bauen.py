# Vorschlagsseite (noindex): immer NUR die aktuelle Runde, nie alte Listen mitliefern (Noah, 15.11.2026).
# Runde 7 (Noah mochte 6, 9, 20: Servus ich bin Noah + Brüder/Handwerksfirmen + ich weiß, wie es zugeht + abends keine Lust). Runde 6 (Aufbau nach Noah: Intro, Überleitung, einer der drei Familiensätze, Outro; Vorbild Felix auf zimmerei-partner.de, kürzer). Runde 5 (Runde 4 war Noah zu unauthentisch, Werbetexter-Sätze): Noahs eigene Sätze aus den Calls als Vorlage. Runde 4: komplette Über-uns-Sektionen (kleine Zeile, Überschrift, Text), HWM persönlich, SHK ohne Persönliches.
from pathlib import Path
import html
N = 'Noah Seelau, Gründer'
BLOECKE = [('Handwerksmanufaktur', 'Servus, Brüder, ich weiß, wie es zugeht', [
 ('Über uns', 'Servus, ich bin Noah.', 'Zwei meiner Brüder sind im Handwerk, und wir haben in der Familie mehrere Handwerksfirmen. Daher weiß ich, wie es in den Betrieben zugeht. Seit 2019 machen wir Websites und Anzeigen nur fürs Handwerk, für über 150 Betriebe bisher.', N),
 ('Über uns', 'Seit 2019 nur fürs Handwerk.', 'Servus, ich bin Noah. Zwei meiner Brüder sind im Handwerk, und wir haben in der Familie mehrere Handwerksfirmen. Daher weiß ich, wie es in einem Betrieb zugeht. Deshalb arbeiten wir für Handwerksbetriebe und für sonst niemanden.', N),
 ('Über uns', 'Ich weiß, wie es im Handwerk zugeht.', 'Servus, ich bin Noah. Zwei meiner Brüder sind im Handwerk, und wir haben in der Familie mehrere Handwerksfirmen. Ich weiß einfach, wie es in den Betrieben läuft. Seit 2019 kümmern wir uns für Handwerksbetriebe um Website, Aufträge und Mitarbeiter.', N),
 ('Über uns', 'Wer hinter der Handwerksmanufaktur steht.', 'Servus, ich bin Noah. Wir haben in der Familie mehrere Handwerksfirmen, und meine drei Brüder sind da alle reingerutscht. Daher weiß ich, wie es in einem Betrieb zugeht. Seit 2019 arbeiten wir nur fürs Handwerk, über 150 Betriebe waren es bisher.', N),
 ('Über uns', 'Das hat einen Grund.', 'Servus, ich bin Noah. Seit 2019 arbeiten wir nur fürs Handwerk. Zwei meiner Brüder sind im Handwerk, und wir haben in der Familie mehrere Handwerksfirmen. Daher weiß ich, wie es in deinem Betrieb zugeht.', N),
 ('Über uns', 'Wir wissen, für wen wir arbeiten.', 'Servus, ich bin Noah. Zwei meiner Brüder sind im Handwerk, und wir haben in der Familie mehrere Handwerksfirmen. Ich weiß, wie es in den Betrieben zugeht. Ruf einfach an, wenn du wissen willst, was wir für deinen Betrieb tun können.', N),
 ('Über uns', 'Handwerk kenne ich von daheim.', 'Servus, ich bin Noah. Wir haben in der Familie mehrere Handwerksfirmen, und meine drei Brüder sind da alle reingerutscht. Ich weiß einfach, wie es im Handwerk zugeht. Deshalb machen wir seit 2019 nichts anderes: Websites, Aufträge und Mitarbeiter für Handwerksbetriebe.', N),
 ('Über uns', 'Warum nur Handwerk?', 'Servus, ich bin Noah. Zwei meiner Brüder sind im Handwerk, und wir haben in der Familie mehrere Handwerksfirmen. Daher weiß ich, wie es in einem Betrieb zugeht. Das ist der Grund, warum wir seit 2019 nur für Handwerksbetriebe arbeiten.', N),
 ('Über uns', 'Du musst uns nichts erklären.', 'Servus, ich bin Noah. Zwei meiner Brüder sind im Handwerk, und wir haben in der Familie mehrere Handwerksfirmen. Ich weiß, wie es in den Betrieben zugeht. Über 150 Handwerksbetriebe haben seit 2019 mit uns gearbeitet.', N),
 ('Über uns', 'Der Gründer.', 'Servus, ich bin Noah. Zwei meiner Brüder sind im Handwerk, und wir haben in der Familie mehrere Handwerksfirmen. Daher weiß ich, wie es bei dir im Betrieb zugeht. Du machst dein Handwerk, wir kümmern uns um Website und Anzeigen. Seit 2019, nur fürs Handwerk.', N),
]), ('SHK', 'gleicher Ton', [
 ('Über uns', 'Servus, ich bin Noah.', 'Zwei meiner Brüder sind im Handwerk, und wir haben in der Familie mehrere Handwerksfirmen. Daher weiß ich, wie es im Handwerk zugeht. Für SHK-Betriebe holen wir Monteure und Aufträge für Bad und Wärmepumpe.', N),
 ('Über uns', 'Wer dahinter steht.', 'Servus, ich bin Noah. Zwei meiner Brüder sind im Handwerk, und wir haben in der Familie mehrere Handwerksfirmen. Daher weiß ich, wie es in einem Betrieb zugeht. Wir holen dir Monteure und Aufträge aus deinem Umkreis.', N),
 ('Über uns', 'Ich weiß, wie es im Handwerk zugeht.', 'Servus, ich bin Noah. Zwei meiner Brüder sind im Handwerk, und wir haben in der Familie mehrere Handwerksfirmen. Ich weiß einfach, wie es in den Betrieben läuft. Für SHK-Betriebe holen wir Monteure und Aufträge für Bad und Wärmepumpe.', N),
 ('Über uns', 'Du beherrschst dein Handwerk. Wir unseres.', 'Servus, ich bin Noah. Zwei meiner Brüder sind im Handwerk, und wir haben in der Familie mehrere Handwerksfirmen. Daher weiß ich, wie es in deinem Betrieb zugeht. Du musst uns nichts erklären.', N),
 ('Über uns', 'Der Partner für SHK-Betriebe.', 'Servus, ich bin Noah. Wir haben in der Familie mehrere Handwerksfirmen, und meine drei Brüder sind da alle reingerutscht. Ich weiß, wie es im Handwerk zugeht. Für SHK-Betriebe holen wir Monteure und Aufträge.', N),
 ('Über uns', 'Wir wissen, für wen wir arbeiten.', 'Servus, ich bin Noah. Zwei meiner Brüder sind im Handwerk, und wir haben in der Familie mehrere Handwerksfirmen. Ich weiß, wie es in den Betrieben zugeht. Seit 8 Jahren arbeiten wir nur fürs Handwerk, über 150 Betriebe bisher.', N),
 ('Über uns', 'Handwerk kenne ich von daheim.', 'Servus, ich bin Noah. Wir haben in der Familie mehrere Handwerksfirmen, und meine drei Brüder sind da alle reingerutscht. Ich weiß einfach, wie es im Handwerk zugeht. Wir holen dir Monteure und Aufträge, und du führst nur noch die Gespräche.', N),
 ('Über uns', 'Du musst uns nichts erklären.', 'Servus, ich bin Noah. Zwei meiner Brüder sind im Handwerk, und wir haben in der Familie mehrere Handwerksfirmen. Daher weiß ich, wie es in einem Betrieb zugeht. Für SHK-Betriebe sorgen wir dafür, dass Monteure und Aufträge planbar kommen.', N),
 ('Über uns', 'Spezialisiert auf SHK.', 'Servus, ich bin Noah. Zwei meiner Brüder sind im Handwerk, und wir haben in der Familie mehrere Handwerksfirmen. Ich weiß, wie es im Handwerk zugeht. Mit der Handwerksmanufaktur arbeiten wir für SHK-Betriebe und holen Monteure und Aufträge für Bad und Wärmepumpe.', N),
 ('Über uns', 'Der Gründer.', 'Servus, ich bin Noah. Zwei meiner Brüder sind im Handwerk, und wir haben in der Familie mehrere Handwerksfirmen. Daher weiß ich, wie es bei dir im Betrieb zugeht. Wir holen dir Monteure und Aufträge aus deinem Umkreis.', N),
])]
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
        out.append(f'<div class="k"><span class="nr">{i}</span><div class="kl">{e(kl)}</div><h3>{h(hh)}</h3><p>{e(tx)}</p>' + (f'<p class="sig">{e(sig)}</p>' if sig else '') + '</div>')
out.append('</div></body></html>')
s = ''.join(out)
assert '–' not in s and '—' not in s and 'sondern' not in s and 'komme aus einer' not in s and 'keine Lust' not in s
Path(__file__).with_name('index.html').write_text(s)
print(sum(len(l) for _, _, l in BLOECKE), 'Texte')

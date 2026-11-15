# Vorschlagsseite (noindex): immer NUR die aktuelle Runde, nie alte Listen mitliefern (Noah, 15.11.2026).
# Runde 4: komplette Über-uns-Sektionen (kleine Zeile, Überschrift, Text), HWM persönlich, SHK ohne Persönliches.
from pathlib import Path
import html
N = 'Noah Seelau, Gründer'
BLOECKE = [('Handwerksmanufaktur', 'persönlich, Handwerkssprache', [
 ('Über uns', 'Einer musste|ins Büro.', 'Meine Brüder haben den Meister gemacht. Mein Cousin hat die Spenglerei. Ich hab mir den Rechner genommen. Seit 2019 bauen wir Websites für Handwerksbetriebe, füllen Auftragsbücher und holen Verstärkung. Über 150 Betriebe waren es bis heute. Wie es auf der Baustelle zugeht, muss mir keiner erklären.', N),
 ('Über uns', 'Der Meisterbrief hängt|bei meinen Brüdern.', 'Bei mir hängt keiner. Ich hab was anderes gelernt: wie ein Handwerksbetrieb im Internet gefunden wird, an Aufträge kommt und an gute Leute. Seit 2019 mache ich das für Betriebe wie die in meiner Familie. Über 150 bisher.', N),
 ('Über uns', 'Handwerk liegt bei uns|in der Familie.', 'Zwei meiner Brüder sind Meister. Mein Cousin führt eine Spenglerei. Und einen Tiefbau-Betrieb haben wir auch in der Familie. Ich bin der, der ins Internet gegangen ist. Seit 2019 mache ich nichts anderes als Websites, Aufträge und Mitarbeiter für Handwerksbetriebe.', N),
 ('Über uns', 'Servus,|ich bin Noah.', 'Meine Brüder stehen auf der Baustelle, ich sitze am Rechner. Zwei von ihnen haben den Meister, mein Cousin führt eine Spenglerei, und einen Tiefbau-Betrieb haben wir auch in der Familie. Seit 2019 sorge ich mit meinem Team dafür, dass Handwerker online Aufträge und Mitarbeiter finden.', N),
 ('Über uns', 'Wir kennen dein Handwerk.|Von daheim.', 'Spenglerei beim Cousin. Tiefbau in der Familie. Zwei Brüder mit Meister. Da lernst du früh, wie ein Betrieb tickt und wo es klemmt. Heute sorgen wir dafür, dass Betriebe wie deiner online so gut dastehen wie auf der Baustelle. Seit 2019, bei über 150 Betrieben.', N),
 ('Über uns', 'Vom Fach.|Nur eben fürs Internet.', 'Dein Handwerk kannst du. Unseres ist, dass man dich findet. Seit 2019 bauen wir Websites, bringen Aufträge und holen Mitarbeiter, ausschließlich für Handwerksbetriebe. Dass ich mit Handwerkern groß geworden bin, hilft: zwei Brüder mit Meister, ein Cousin mit Spenglerei, Tiefbau in der Familie.', N),
 ('Über uns', 'Handschlag zählt.|Auch im Internet.', 'Im Handwerk gilt, was ausgemacht ist. Bei uns auch. Das kenne ich von daheim: zwei Brüder mit Meister, ein Cousin mit Spenglerei, Tiefbau in der Familie. Seit 2019 arbeiten wir nur für Handwerksbetriebe. Über 150 haben uns bis heute vertraut.', N),
 ('Über uns', 'Wir sprechen Handwerk.|Seit 2019.', 'Bei uns hörst du kein Marketing-Deutsch. Ich bin mit Handwerkern groß geworden: zwei Brüder mit Meister, ein Cousin mit Spenglerei, ein Tiefbau-Betrieb in der Familie. Deshalb reden wir mit dir so, wie du mit deinen Kunden redest. Klar und ohne Umwege.', N),
 ('Über uns', 'Bei uns daheim|sind fast alle vom Bau.', 'Zwei Brüder mit Meisterbrief, ein Cousin mit eigener Spenglerei, dazu ein Tiefbau-Betrieb mit rund 20 Leuten. Ich weiß, wie ein Betrieb läuft. Und was er abends nicht auch noch machen will: Website, Anzeigen, Bewerbungen. Genau das übernehmen wir. Seit 2019, nur für Handwerker.', N),
 ('Über uns', 'Seit 2019|nur Handwerk.', 'Wir machen eine Sache. Die dafür richtig: Websites, Aufträge und Mitarbeiter für Handwerksbetriebe. Über 150 Betriebe in acht Jahren, 5,0 Sterne bei 57 Bewertungen auf Google. Dahinter steht Noah, der Bruder von zwei Meistern.', ''),
]), ('SHK', 'ohne Persönliches, schlicht', [
 ('Über uns', 'Ein Team.|Ein Gewerk.', 'Wir arbeiten für Betriebe aus Sanitär, Heizung und Klima. Deshalb wissen wir, womit man einen Anlagenmechaniker erreicht und wann jemand sein Bad sanieren will. Das musst du uns nicht erklären.', ''),
 ('Über uns', 'Planbar|statt Zufall.', 'Empfehlungen sind gut. Verlassen kannst du dich darauf nicht. Wir sorgen dafür, dass Bewerbungen und Anfragen aus deinem Umkreis regelmäßig kommen. Über 150 Handwerksbetriebe haben wir bisher betreut.', ''),
 ('Über uns', 'Wir kennen|dein Gewerk.', 'Wärmepumpe, Badsanierung, Kundendienst: Wir wissen, wofür dir die Leute fehlen und welche Aufträge du willst. Darauf bauen wir Kampagne und Website. Dein Handwerk musst du uns nicht erklären.', ''),
 ('Über uns', 'Kleines Team.|Kurze Wege.', 'Du hast einen Ansprechpartner, der dein Gewerk kennt. Monteure, Aufträge und Website kommen aus einem Team. So weiß jeder, was beim anderen gerade läuft.', ''),
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
assert '–' not in s and '—' not in s
Path(__file__).with_name('index.html').write_text(s)
print(sum(len(l) for _, _, l in BLOECKE), 'Texte')

# Vorschlagsseite (noindex): immer NUR die aktuelle Runde, nie alte Listen mitliefern (Noah, 15.11.2026).
# Runde 5 (Runde 4 war Noah zu unauthentisch, Werbetexter-Sätze): Noahs eigene Sätze aus den Calls als Vorlage. Runde 4: komplette Über-uns-Sektionen (kleine Zeile, Überschrift, Text), HWM persönlich, SHK ohne Persönliches.
from pathlib import Path
import html
N = 'Noah Seelau, Gründer'
BLOECKE = [('Handwerksmanufaktur', 'so wie Noah im Gespräch redet', [
 ('Über uns', 'Bei uns in der Familie sind fast alle Handwerker.', 'Ich hab zwei Brüder mit Meister, mein Cousin hat eine Spenglerei und wir haben selber einen Tiefbau-Betrieb in der Familie. Ich bin der mit dem Marketing. Seit 2019 mache ich das für Handwerksbetriebe, und zwar nur für die.', N),
 ('Über uns', 'Warum nur Handwerk?', 'Weil ich mich da auskenne. Meine Brüder sind Meister, mein Cousin hat eine Spenglerei. Ich weiß, wie es in einem Betrieb zugeht und dass für Marketing eigentlich nie Zeit ist. Deshalb nehmen wir dir das ab.', N),
 ('Über uns', 'Mundpropaganda ist die beste Werbung.', 'Das stimmt, und das sagen wir auch jedem Kunden. Nur reicht sie halt nicht immer, wenn du einen Monteur suchst oder das Auftragsbuch voller sein soll. Dann kommen wir dazu. Seit 2019 machen wir das für Handwerksbetriebe, über 150 bisher.', N),
 ('Über uns', 'Ich bin Noah.', 'Ich mache seit acht Jahren Marketing für Handwerksbetriebe und sonst für niemanden. Über 150 Betriebe haben wir betreut, bei Google stehen 57 Bewertungen mit fünf Sternen. Das sag ich nicht, um zu prahlen. Du sollst nur wissen, mit wem du es zu tun hast.', N),
 ('Über uns', 'Marketing ist planbar.', 'Viele Betriebe leben von Empfehlungen, und das läuft mal besser, mal schlechter. Mit Website und Anzeigen siehst du, wie viele Leute draufgehen und wie viele Anfragen daraus werden. Genau das bauen wir für Handwerksbetriebe auf, seit 2019.', N),
 ('Über uns', 'Was wir machen.', 'Wir sorgen dafür, dass dein Betrieb online gefunden wird und dass Anfragen und Bewerbungen reinkommen. Dafür bauen wir deine Website, schalten Anzeigen und drehen bei dir im Betrieb, mit deinen Leuten. Du kümmerst dich nur noch um die Anfragen.', ''),
 ('Über uns', 'Wir verkaufen keine Leads.', 'Wir bauen bei dir einen eigenen Kanal auf: deine Website, deine Anzeigen, dein Name. Die Anfragen gehören dir allein. So arbeiten wir seit 2019 mit Handwerksbetrieben, über 150 waren es bisher.', ''),
 ('Über uns', 'Wir sind keine große Agentur.', 'Du hast mit mir und einem kleinen Team zu tun, nicht jedes Mal mit jemand anderem. Wir arbeiten seit 2019 nur mit Handwerksbetrieben. Über 150 waren es bisher, bei Google stehen wir bei 5,0 Sternen aus 57 Bewertungen.', N),
 ('Über uns', 'Wer dahinter steht.', 'Servus, ich bin Noah. Ich hab die Handwerksmanufaktur 2019 gegründet, weil viele Handwerksbetriebe gute Arbeit machen und man das online einfach nicht sieht. Handwerk kenne ich von daheim: Meine Brüder sind Meister, mein Cousin hat eine Spenglerei.', N),
 ('Über uns', 'Seit 2019 nur Handwerk.', 'Websites, Anzeigen für neue Aufträge, Anzeigen für neue Mitarbeiter. Mehr machen wir nicht, und das nur für Handwerksbetriebe. Über 150 haben wir bisher betreut. Wenn du wissen willst, wie das bei dir aussehen würde, ruf einfach an.', N),
]), ('SHK', 'ohne Persönliches', [
 ('Über uns', 'Wir arbeiten für SHK-Betriebe.', 'Wir schalten Anzeigen für Monteure, Bäder und Wärmepumpen und bauen die Website dazu. Gedreht wird bei dir im Betrieb, mit deinen Leuten. Über 150 Handwerksbetriebe haben wir bisher betreut.', ''),
 ('Über uns', 'Marketing ist planbar.', 'Empfehlungen laufen mal besser, mal schlechter. Mit Anzeigen in deinem Umkreis siehst du, wie viele Bewerbungen und Anfragen reinkommen, und kannst damit rechnen. Das bauen wir für SHK-Betriebe auf.', ''),
 ('Über uns', 'Deine Anfragen gehören dir.', 'Wir verkaufen keine Leads. Die Anzeigen laufen auf deinen Namen, Bewerbungen und Anfragen kommen direkt zu dir. Um den Rest kümmern wir uns.', ''),
 ('Über uns', 'Kleines Team.', 'Du hast einen festen Ansprechpartner, der SHK kennt. Wir arbeiten seit 8 Jahren nur für Handwerksbetriebe. Über 150 waren es bisher, bei Google stehen 5,0 Sterne aus 57 Bewertungen.', ''),
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

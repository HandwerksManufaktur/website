// Prüft den Endpunkt /konzept-anfrage (src/konzept.js) ohne ein einziges echtes Close-/Resend-/D1-Ziel:
// fetch und D1 sind Attrappen, jeder Aufruf wird mitgeschrieben.
// Aufruf: node test/konzept_anfrage.mjs            (bündelt src/konzept.js vorher mit esbuild)
//         node test/konzept_anfrage.mjs --fehler   (baut einen Fehler ein: die Proben MÜSSEN rot werden)
import { execSync } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync, unlinkSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const dir = mkdtempSync(join(tmpdir(), 'ka-'));
const out = join(dir, 'k.mjs');
const wurzel = new URL('..', import.meta.url).pathname;
let quelle = join(wurzel, 'src/konzept.js');
const fehlerArg = process.argv.find(a => a.startsWith('--fehler'));   // --fehler = alle Fehler zusammen · --fehler=N = nur Fehler Nr. N (0-basiert)
if (fehlerArg) {
  // Gegenprobe: jeder Eintrag baut einen Fehler in eine TEMP-KOPIE der Quelle ein (die echte Datei bleibt unberührt);
  // trifft ein Suchtext nicht, bricht der Lauf ab — sonst wäre die Gegenprobe still wirkungslos.
  const fehler = [
    ['`${kanalLabel(code)} ${jetzt.getUTCFullYear()}`', 'kanalLabel(code)'],                                // Quelle ohne Jahr
    ["close.art !== 'nachtrag'", 'false'],                                                                  // Kunde bekommt nie eine Mail
    ["klick.utm_source === 'google'", 'false'],                                                             // Ads-Quelle
    ['if (env.CLOSE_FIELD_GCLID && gclid) await schritt', 'if (false) await schritt'],                      // B2: Feld nicht nach dem Lead setzen
    ["await schritt('Aufgabe', () =>", "await (() =>"],                                                     // B2: Teilfehler wird zum Totalfehler
    ["} catch (e) { console.error('[Konzept] D1 lesen', fehlerText(e)); vorher = null; }", '} catch (e) { throw e; }'], // B1: D1 lesen nicht abgefangen
    ['signal: zeitlimit(),', ''],                                                                           // B1: Zeitlimit weg
    ['...seiteZeilen(d.seite).map(([l, v]) => `${l}: ${v}`),', ''],                                         // B4: seite nicht in der Notiz
    ['...seiteZeilen(d.seite),\n', '\n'],                                                                   // B4: seite nicht in der Mail
    ["replace(/[^\\p{L}\\p{N} \\-_.+%\\/]/gu, '')", "replace(/[^\\w.\\-~%+]/g, '')"],                    // B5: UTM zu streng
    ["(/^[A-Za-z0-9_-]{1,200}$/.test(roh) ? roh : '')", "roh.replace(/[^\\w.\\-~%+]/g, '').slice(0, 200)"],   // B5: Kennung nicht streng
    ["export const klickId = k => k.gclid || '';", "export const klickId = k => k.gclid || k.gbraid || k.wbraid || '';"], // B6
    ["custom['Google Click ID'] !== gclid", "!custom['Google Click ID']"],                                  // B6: alter gclid wird nie ersetzt
    ["const notiz = (lead_id, extra) => schritt('Notiz', () => close(", "const notiz = (lead_id, extra) => (() => close("],   // B2: Notiz-Fehler verwirft die Lead-ID
    ['teilfehler.some(t => t.was === \'Feld Google Click ID\')', 'false'],                                  // B2: Notiz nennt Feldfehler nicht
    ["if (extra) { try { await insert(true); } catch (e) { console.error('[Konzept] D1 mit extra', fehlerText(e)); await insert(false); } }", "if (extra) { await insert(true); }"], // B3: kein Rückfall ohne Spalte
    ["if (Object.keys(d.klick || {}).length) extraObj.klick = d.klick;", ""],                               // B3: Klick nicht in D1
    ["...(Object.keys(d.klick || {}).length ? [['Google-Klick', klickText(d.klick)]] : []),", ""],          // B3: Klick nicht in der Mail
    ["if (lead && alt !== gclid) {", "if (false) {"],                                                       // A: Nachtrag aktualisiert das Feld nicht
    ["logoVerloren = true;\n", "\n"],                                                                        // B: verlorenes Logo wird nicht erkannt
    ["delete ohne.attachments;", ""],                                                                       // B: Wiederholung OHNE Anhang
    ["const m = mailBetrieb(d, logo, logoVerloren);", "const m = mailBetrieb(d, logo, false);"],           // B: Kundenmail bestätigt das Logo trotzdem
  ];
  let text = readFileSync(quelle, 'utf8');
  const nur = fehlerArg.includes('=') ? Number(fehlerArg.split('=')[1]) : -1;
  for (const [i, [alt, neu]] of fehler.entries()) { if (nur >= 0 && i !== nur) continue; if (!text.includes(alt)) { console.error('Gegenprobe: Suchtext nicht gefunden: ' + alt); process.exit(2); } text = text.replace(alt, neu); }
  globalThis.ANZAHL_FEHLER = fehler.length;
  quelle = join(wurzel, 'src/_konzept_fehler.js'); writeFileSync(quelle, text);
}
try { execSync(`npx esbuild ${quelle} --bundle --format=esm --outfile=${out} --log-level=warning`, { cwd: wurzel }); }
finally { if (quelle.endsWith('_konzept_fehler.js')) unlinkSync(quelle); }
const K = await import(out);

const JETZT = new Date('2026-09-29T10:00:00Z');
function formular(felder, logo) {
  const fd = new FormData();
  for (const [k, v] of Object.entries(felder)) fd.append(k, v);
  if (logo) fd.append('logo', new File([new Uint8Array(logo.groesse).fill(7)], logo.name, { type: logo.typ }));
  return fd;
}
const GUT = { betrieb: 'Testbetrieb Claude', name: 'Max Muster', email: 'max@beispiel.de', telefon: '0170 1234567', website: 'beispiel.de', code: 'kleinanzeigen' };

function welt({ closeTreffer = [], closeFehler = false, d1Vorher = null, d1Zaehler = 0, closeLehntAb = null, d1Fehler = false, d1OhneExtra = false, closeHaengt = false, resendFehler = false, resendLehntAnhang = false, leadCustom = {} } = {}) {
  const aufrufe = [], d1 = [];
  const fetchImpl = async (u, o = {}) => {
    const body = o.body ? JSON.parse(o.body) : null;
    aufrufe.push({ u: String(u), m: o.method || 'GET', body, signal: o.signal });
    if (String(u).startsWith('https://api.close.com')) {
      if (closeHaengt) throw new DOMException('The operation timed out.', 'TimeoutError');
      if (closeFehler) return new Response('kaputt', { status: 500 });
      if (closeLehntAb && closeLehntAb(String(u), o.method || 'GET', body)) return new Response('{"errors":["abgelehnt"]}', { status: 400 });
      if (String(u).includes('/lead/?query=')) return Response.json({ data: closeTreffer });
      if ((o.method || 'GET') === 'GET' && /\/lead\/lead_[A-Z]+\/\?_fields/.test(String(u))) return Response.json({ id: 'lead', custom: leadCustom });
      if (o.method === 'POST' && String(u).endsWith('/lead/')) return Response.json({ id: 'lead_NEU' });
      return Response.json({ id: 'x' });
    }
    if (String(u).startsWith('https://api.resend.com')) return resendFehler || (resendLehntAnhang && body.attachments) ? new Response('kaputt', { status: 500 }) : Response.json({ id: 'mail' });
    throw new Error('unerwartetes Ziel ' + u);
  };
  const db = {
    prepare: sql => ({
      bind: (...a) => ({
        first: async () => { if (d1Fehler) throw new Error('D1 down'); return sql.includes('COUNT(*)') ? { n: d1Zaehler } : d1Vorher; },
        run: async () => { if (d1Fehler || (d1OhneExtra && /, extra\)/.test(sql))) throw new Error('D1 down / no column extra'); d1.push({ sql, a }); return {}; },
      }),
    }),
  };
  return { aufrufe, d1, env: { CLOSE_API_KEY: 'k', RESEND_API_KEY: 'r', RUN_DB: db }, fetchImpl };
}
async function schick(w, felder, { logo = null, trocken = false } = {}) {
  const req = new Request('https://w.test/konzept-anfrage' + (trocken ? '?trocken=1' : ''), { method: 'POST', body: formular(felder, logo), headers: { 'cf-connecting-ip': '1.2.3.4' } });
  try {
    const r = await K.handleKonzeptAnfrage(req, w.env, { fetchImpl: w.fetchImpl, jetzt: () => JETZT });
    return { status: r.status, j: await r.json() };
  } catch (e) { return { status: 500, j: {}, wurf: String(e) }; }   // ein geworfener Fehler heißt: der Besucher bekäme 500 — die Probe wird rot
}
const mails = w => w.aufrufe.filter(a => a.u.includes('resend'));
const close = (w, teil, m) => w.aufrufe.filter(a => a.u.includes('close') && a.u.includes(teil) && (!m || a.m === m));

const proben = [];
const probe = (name, ok) => proben.push([name, !!ok]);

{ const w = welt(); const r = await schick(w, GUT, { trocken: true });
  probe('Trockenlauf: Quelle „Kleinanzeigen 2026"', r.j.quelle === 'Kleinanzeigen 2026');
  probe('Trockenlauf: kein einziger Aufruf nach außen, kein D1', w.aufrufe.length === 0 && w.d1.length === 0); }

{ const w = welt(); const r = await schick(w, GUT);
  const lead = close(w, '/lead/', 'POST')[0];
  probe('Neu: 200 + Lead angelegt', r.status === 200 && lead);
  probe('Neu: Lead trägt Quelle, Status Hot, Kontakt mit E-Mail + Telefon',
    lead && lead.body[`custom.${K.CLOSE_QUELLE_FELD}`] === 'Kleinanzeigen 2026' && lead.body.status_id === K.CLOSE_STATUS_HOT
    && lead.body.contacts[0].emails[0].email === 'max@beispiel.de' && lead.body.contacts[0].phones[0].phone === '0170 1234567');
  probe('Neu: Website normalisiert (https://beispiel.de)', lead && lead.body.url === 'https://beispiel.de');
  probe('Neu: Notiz + Anruf-Aufgabe für heute', close(w, '/activity/note/', 'POST').length === 1 && close(w, '/task/', 'POST')[0]?.body.date === '2026-09-29');
  const [intern, betrieb] = mails(w);
  probe('Neu: Mail an info@ mit Betrieb + Code im Betreff', intern && intern.body.to[0] === 'info@handwerksmanufaktur.digital' && /Testbetrieb Claude · Code KLEINANZEIGEN/.test(intern.body.subject));
  probe('Neu ohne Logo: Betrieb wird ums Logo gebeten + Terminlink', betrieb && betrieb.body.to[0] === 'max@beispiel.de' && /Logo/.test(betrieb.body.text) && betrieb.body.text.includes(K.CAL_KONZEPT) && /^Hallo Max,/.test(betrieb.body.text));
  probe('Neu: Antwort geht an info@ (reply_to)', betrieb && betrieb.body.reply_to === 'info@handwerksmanufaktur.digital');
  probe('Neu: D1-Zeile mit Code, Lead und hat_logo = 0', w.d1.length === 1 && w.d1[0].a[1] === 'KLEINANZEIGEN' && w.d1[0].a[8] === 'lead_NEU' && w.d1[0].a[10] === 0);
  probe('Kundenmail ohne Gedankenstrich', betrieb && !/[–—]/.test(betrieb.body.text)); }

{ const w = welt(); const r = await schick(w, { ...GUT, code: '' }, { logo: { name: 'logo.png', typ: 'image/png', groesse: 2048 } });
  const [intern, betrieb] = mails(w);
  probe('Ohne Code: Quelle „Website 2026"', close(w, '/lead/', 'POST')[0]?.body[`custom.${K.CLOSE_QUELLE_FELD}`] === 'Website 2026');
  probe('Mit Logo: Anhang in der info@-Mail (Base64, 2 KB)', intern?.body.attachments?.[0]?.filename === 'logo.png' && Buffer.from(intern.body.attachments[0].content, 'base64').length === 2048);
  probe('Mit Logo: Betrieb wird NICHT ums Logo gebeten', betrieb && !/brauche ich noch dein Logo/.test(betrieb.body.text) && r.j.hat_logo === true); }

{ const w = welt({ closeTreffer: [{ id: 'lead_ALT', custom: { Quelle: 'GMaps-Scrape 08/26' } }] }); await schick(w, GUT);
  probe('Lead gibt es schon: kein neuer Lead, Quelle bleibt', close(w, '/lead/', 'POST').length === 0 && close(w, '/lead/lead_ALT/', 'PUT').length === 0 && close(w, '/task/', 'POST')[0]?.body.lead_id === 'lead_ALT'); }

{ const w = welt({ d1Vorher: { lead_id: 'lead_ERST' } }); await schick(w, GUT);
  probe('Gleiche E-Mail binnen 24 h: nur Nachtrag-Notiz am ersten Lead, keine zweite Kundenmail',
    close(w, '/lead/', 'POST').length === 0 && close(w, '/activity/note/', 'POST')[0]?.body.lead_id === 'lead_ERST' && mails(w).length === 1 && /^Nachtrag/.test(mails(w)[0].body.subject)); }

{ const w = welt(); const r = await schick(w, { ...GUT, bot: 'ich bin ein bot' });
  probe('Honeypot: still ok, nichts passiert', r.status === 200 && w.aufrufe.length === 0); }

{ const w = welt(); const r = await schick(w, { ...GUT, email: 'kaputt' });
  probe('Ungültige E-Mail: 400', r.status === 400 && w.aufrufe.length === 0); }
{ const w = welt(); const r = await schick(w, GUT, { logo: { name: 'gross.png', typ: 'image/png', groesse: 5 * 1024 * 1024 + 1 } });
  probe('Logo über 5 MB: 400', r.status === 400); }
{ const w = welt(); const r = await schick(w, GUT, { logo: { name: 'x.exe', typ: 'application/octet-stream', groesse: 10 } });
  probe('Logo falscher Typ: 400', r.status === 400); }

{ const w = welt({ closeFehler: true }); const r = await schick(w, GUT);
  probe('Close fällt aus: Anfrage geht trotzdem an info@ (mit Warnung), Kunde bekommt 200', r.status === 200 && /nicht geantwortet/.test(mails(w)[0]?.body.html || '') && w.d1[0]?.a[9] === 'close-fehler'); }

{ const w = welt({ d1Zaehler: 5 }); const r = await schick(w, GUT);
  probe('Rate-Limit: 6. Anfrage je IP und Stunde → 429, nichts nach außen', r.status === 429 && w.aufrufe.length === 0); }

probe('Vorname: „Frau Müller" → keine Anrede mit Vorname', K.vorname('Frau Müller') === '' && K.vorname('Anna Maier') === 'Anna');
probe('Code wird bereinigt (Leerzeichen, Kleinschreibung, Unsinn)', K.codeSauber(' insta gram ') === 'INSTAGRAM' && K.codeSauber('<script>') === '');

// 📈 Google-Ads-Klick (30.09.2026): gclid/utm reisen mit, Quelle „Google Ads – Suche", Feld nur mit CLOSE_FIELD_GCLID
const ADS = { ...GUT, code: 'SEO-LANDSBERG', gclid: 'TEST123', utm_source: 'google', utm_medium: 'cpc', utm_campaign: '99', bot: '' };
{ const w = welt(); await schick(w, ADS);
  const lead = close(w, '/lead/', 'POST')[0]; const note = close(w, '/activity/note/', 'POST')[0];
  probe('Ads: Quelle = „Google Ads – Suche" bei utm_source=google + cpc', lead?.body[`custom.${K.CLOSE_QUELLE_FELD}`] === 'Google Ads – Suche');
  probe('Ads: gclid steht in der Lead-Notiz (Feld-Variable leer)', /Google-Klick: gclid=TEST123/.test(note?.body.note || '') && !Object.keys(lead.body).some(k => k.startsWith('custom.') && k !== `custom.${K.CLOSE_QUELLE_FELD}`)); }
{ const w = welt(); w.env.CLOSE_FIELD_GCLID = 'cf_TESTFELD'; await schick(w, ADS);
  const put = close(w, '/lead/lead_NEU/', 'PUT');
  probe('Ads: mit CLOSE_FIELD_GCLID landet gclid im Close-Feld — per eigenem PUT, nicht im Lead-POST',
    put.length === 1 && put[0].body['custom.cf_TESTFELD'] === 'TEST123' && !('custom.cf_TESTFELD' in close(w, '/lead/', 'POST')[0].body)); }
{ const w = welt(); await schick(w, { ...GUT, gclid: 'A<b>x"', utm_source: 'newsletter' });
  const note = close(w, '/activity/note/', 'POST')[0];
  probe('Ungültige Kennung (HTML, Anführungszeichen) wird verworfen, fremde utm_source ändert die Quelle nicht',
    !/gclid|<b>/.test(note?.body.note || '') && close(w, '/lead/', 'POST')[0]?.body[`custom.${K.CLOSE_QUELLE_FELD}`] === 'Kleinanzeigen 2026'); }
{ const w = welt(); await schick(w, GUT);
  probe('Ohne Klick-Felder: keine Google-Klick-Zeile in der Notiz', !/Google-Klick/.test(close(w, '/activity/note/', 'POST')[0]?.body.note || '')); }


// ---------------- Review-Befunde 30.09.2026 ----------------
const TESTFELD = { CLOSE_FIELD_GCLID: 'cf_TESTFELD' };
const ZEIT = 'https://api.close.com';

// 1 · D1 fällt aus → Close und Mails laufen trotzdem, Besucher bekommt 200
{ const w = welt({ d1Fehler: true }); const r = await schick(w, GUT);
  probe('B1: D1 down → trotzdem Lead in Close, beide Mails, 200', r.status === 200 && close(w, '/lead/', 'POST').length === 1 && mails(w).length === 2); }
// 1 · Zeitlimit: jeder Aufruf trägt ein Abbruch-Signal; hängt Close, kommt die Sicherungsmail
{ const w = welt(); await schick(w, GUT);
  probe('B1: jeder Close- und Resend-Aufruf hat ein Zeitlimit-Signal', w.aufrufe.length >= 5 && w.aufrufe.every(a => a.signal && typeof a.signal.aborted === 'boolean')); }
{ const w = welt({ closeHaengt: true }); const r = await schick(w, GUT);
  probe('B1: Close hängt (Timeout) → Sicherungsmail mit Warnung, 200, D1 art = close-fehler',
    r.status === 200 && /nicht geantwortet/.test(mails(w)[0]?.body.html || '') && w.d1[0]?.a[9] === 'close-fehler'); }
{ const w = welt({ closeHaengt: true, resendFehler: true }); const r = await schick(w, GUT);
  probe('B1: Close hängt UND Mail geht nicht → 502 (Besucher soll anrufen)', r.status === 502); }

// 2 · ungültiges gclid-Feld lässt den Lead nicht mehr scheitern
{ const w = welt(); w.env.CLOSE_FIELD_GCLID = 'cf_KAPUTT';
  const ab = (u, m, b) => m === 'PUT' && b && 'custom.cf_KAPUTT' in b;
  const w2 = welt({ closeLehntAb: ab }); w2.env.CLOSE_FIELD_GCLID = 'cf_KAPUTT';
  const r = await schick(w2, ADS);
  const lead = close(w2, '/lead/', 'POST')[0]; const note = close(w2, '/activity/note/', 'POST')[0];
  probe('B2: Lead-POST enthält das optionale Feld nie', lead && !('custom.cf_KAPUTT' in lead.body));
  probe('B2: Close lehnt das Feld ab → Lead bleibt, Notiz + Aufgabe laufen, Wert steht in der Notiz, kein Close-Fehler-Alarm',
    r.status === 200 && lead && note && /gclid=TEST123/.test(note.body.note) && /nicht gesetzt/.test(note.body.note) && close(w2, '/task/', 'POST').length === 1 && w2.d1[0]?.a[9] === 'neu');
  probe('B2: interne Mail benennt den Teilfehler und sagt NICHT „von Hand anlegen"',
    /Feld Google Click ID fehlgeschlagen/.test(mails(w2)[0]?.body.html || '') && !/von Hand anlegen/.test(mails(w2)[0]?.body.html || '')); }
// 2 · Notiz scheitert nach erfolgreicher Anlage → Lead-ID bleibt
{ const w = welt({ closeLehntAb: u => u.includes('/activity/note/') }); const r = await schick(w, GUT);
  const html = mails(w)[0]?.body.html || '';
  probe('B2: Notiz scheitert → Lead-ID bleibt (Link in der Mail, D1 lead_id + art neu), Mail sagt „Notiz fehlgeschlagen", nicht „von Hand anlegen"',
    r.status === 200 && html.includes('/lead/lead_NEU/') && /Lead angelegt, aber unvollständig/.test(html) && /Notiz fehlgeschlagen/.test(html) && !/von Hand anlegen/.test(html) && w.d1[0]?.a[8] === 'lead_NEU' && w.d1[0]?.a[9] === 'neu'); }
{ const w = welt({ closeLehntAb: u => u.includes('/task/') }); await schick(w, GUT);
  probe('B2: Aufgabe scheitert → Lead + Notiz bleiben, Mail nennt „Aufgabe fehlgeschlagen"', /Aufgabe fehlgeschlagen/.test(mails(w)[0]?.body.html || '') && w.d1[0]?.a[8] === 'lead_NEU'); }
{ const w = welt({ d1Vorher: { lead_id: 'lead_ERST' }, closeLehntAb: u => u.includes('/activity/note/') }); await schick(w, GUT);
  probe('B2: Nachtrag — Notiz scheitert → Lead-ID bleibt erhalten', /Notiz fehlgeschlagen/.test(mails(w)[0]?.body.html || '') && w.d1[0]?.a[8] === 'lead_ERST' && w.d1[0]?.a[9] === 'nachtrag'); }

// 3 · Klick-Felder in interner Mail und D1 (auch bei Close-Ausfall)
{ const w = welt({ closeFehler: true }); await schick(w, { ...ADS, seite: '/lp/schreinerei/?gewerk=schreinerei&homepage=nein&ziel=mehr-anfragen' });
  const html = mails(w)[0]?.body.html || ''; const extra = w.d1[0]?.a[13];
  probe('B3: Close down → interne Mail trägt gclid und utm', /gclid=TEST123/.test(html) && /utm_source=google/.test(html) && /nicht geantwortet/.test(html));
  probe('B3: D1-Zeile trägt gclid/utm + Landingpage-Antworten in `extra` (JSON)', extra && JSON.parse(extra).klick?.gclid === 'TEST123' && /schreinerei/.test(JSON.parse(extra).seite) && /INSERT INTO konzept_anfragen \(.*, extra\)/.test(w.d1[0].sql)); }
{ const w = welt({ d1OhneExtra: true }); const r = await schick(w, ADS);
  probe('B3: Spalte `extra` fehlt noch → Insert fällt auf die alte Fassung zurück, Zeile geht nicht verloren', r.status === 200 && w.d1.length === 1 && !/extra/.test(w.d1[0].sql)); }

// 4 · `seite` (Gewerk, Homepage, Ziel) in Notiz und Mail
{ const w = welt(); await schick(w, { ...GUT, seite: '/lp/elektro/?gewerk=elektro&homepage=ja&ziel=mehr-anfragen' });
  const note = close(w, '/activity/note/', 'POST')[0]?.body.note || ''; const html = mails(w)[0]?.body.html || '';
  probe('B4: Close-Notiz trägt Gewerk, Homepage, Ziel und Landingpage als eigene Zeilen',
    /^Gewerk: elektro$/m.test(note) && /^Homepage: ja$/m.test(note) && /^Ziel: mehr-anfragen$/m.test(note) && /^Landingpage: \/lp\/elektro\/$/m.test(note));
  probe('B4: interne Mail trägt Gewerk, Homepage, Ziel', />Gewerk<.*elektro/.test(html) && />Homepage<.*ja/.test(html) && />Ziel<.*mehr-anfragen/.test(html)); }
{ const l = K.seiteZeilen('/lp/x/?gewerk=Baustoffe · Tiefbau&homepage=nein&ziel=a%20b&sonst=1');
  probe('B4: Parser: Gewerk mit Leerzeichen/Punkt, %-Kodierung, unbekannte Antworten als „Weitere"',
    l.find(z => z[0] === 'Gewerk')?.[1] === 'Baustoffe · Tiefbau' && l.find(z => z[0] === 'Ziel')?.[1] === 'a b' && l.find(z => z[0] === 'Weitere Antworten')?.[1] === 'sonst=1'); }

// 5 · Bereinigung: Kennungen streng, UTM-Texte großzügig
{ const fd = new FormData(); fd.set('utm_term', 'webdesign für handwerker'); fd.set('utm_campaign', 'Frühjahr_2026-Süd/Test+1.0%20'); fd.set('gclid', 'Cj0KCQ_x-Y9'); fd.set('gbraid', 'ab cd'); fd.set('wbraid', 'x'.repeat(201)); fd.set('utm_content', '<b>Hi</b>\n\u0007"x"');
  const k = K.klickLesen(fd);
  probe('B5: utm_term behält Leerzeichen und Umlaute', k.utm_term === 'webdesign für handwerker');
  probe('B5: utm_campaign behält Umlaute und - _ . + % /', k.utm_campaign === 'Frühjahr_2026-Süd/Test+1.0%20');
  probe('B5: gclid streng [A-Za-z0-9_-]{1,200}; Leerzeichen und Überlänge → verworfen', k.gclid === 'Cj0KCQ_x-Y9' && !k.gbraid && !k.wbraid);
  probe('B5: kein HTML, keine Steuerzeichen, keine Anführungszeichen in UTM-Texten', k.utm_content === 'bHi/b x' && !/[<>"\u0007\n]/.test(k.utm_content)); }
{ const fd = new FormData(); fd.set('utm_source', 'ä'.repeat(300)); probe('B5: UTM-Text höchstens 200 Zeichen', K.klickLesen(fd).utm_source?.length === 200); }

// 6 · klickId: nur gclid ins Feld; gbraid/wbraid nur in die Notiz; jüngster gclid gewinnt
{ const w = welt(); w.env.CLOSE_FIELD_GCLID = 'cf_TESTFELD'; await schick(w, { ...GUT, gbraid: 'GB123', utm_source: 'google', utm_medium: 'cpc' });
  const note = close(w, '/activity/note/', 'POST')[0]?.body.note || '';
  probe('B6: nur gbraid → NICHT im Close-Feld, aber in der Notiz mit Typ', close(w, '/lead/lead_NEU/', 'PUT').length === 0 && /gbraid=GB123/.test(note) && /kein gclid/.test(note)); }
{ const w = welt({ closeTreffer: [{ id: 'lead_ALT', custom: { Quelle: 'x', 'Google Click ID': 'ALT999' } }] }); w.env.CLOSE_FIELD_GCLID = 'cf_TESTFELD'; await schick(w, ADS);
  const put = close(w, '/lead/lead_ALT/', 'PUT'); const note = close(w, '/activity/note/', 'POST')[0]?.body.note || '';
  probe('B6: bestehender Lead mit altem gclid → der neue ersetzt ihn, die Notiz hält alt UND neu mit Datum',
    put.length === 1 && put[0].body['custom.cf_TESTFELD'] === 'TEST123' && /vorher ALT999/.test(note) && /gclid=TEST123 · .* · am 29\.09\.2026/.test(note)); }
{ const w = welt({ closeTreffer: [{ id: 'lead_ALT', custom: { Quelle: 'x', 'Google Click ID': 'TEST123' } }] }); w.env.CLOSE_FIELD_GCLID = 'cf_TESTFELD'; await schick(w, ADS);
  probe('B6: derselbe gclid schon im Feld → kein überflüssiger PUT', close(w, '/lead/lead_ALT/', 'PUT').length === 0); }


// ---------------- Nachbefunde Codex 30.09.2026 ----------------
// A · Nachtragszweig hält das gclid-Feld aktuell
{ const w = welt({ d1Vorher: { lead_id: 'lead_ALT' }, leadCustom: { 'Google Click ID': 'ALT999' } }); w.env.CLOSE_FIELD_GCLID = 'cf_TESTFELD'; await schick(w, ADS);
  const put = close(w, '/lead/lead_ALT/', 'PUT'); const note = close(w, '/activity/note/', 'POST')[0]?.body.note || '';
  probe('A: Nachtrag mit neuem gclid → Feld wird ersetzt, Notiz nennt alt und neu, kein zweiter Lead',
    put.length === 1 && put[0].body['custom.cf_TESTFELD'] === 'TEST123' && /vorher ALT999/.test(note) && close(w, '/lead/', 'POST').length === 0); }
{ const w = welt({ d1Vorher: { lead_id: 'lead_ALT' }, leadCustom: {} }); w.env.CLOSE_FIELD_GCLID = 'cf_TESTFELD'; await schick(w, ADS);
  probe('A: Nachtrag holt einen früher gescheiterten PUT nach (Feld leer → gesetzt)', close(w, '/lead/lead_ALT/', 'PUT').length === 1 && /nachgetragen/.test(close(w, '/activity/note/', 'POST')[0]?.body.note || '')); }
{ const w = welt({ d1Vorher: { lead_id: 'lead_ALT' }, leadCustom: { 'Google Click ID': 'TEST123' } }); w.env.CLOSE_FIELD_GCLID = 'cf_TESTFELD'; await schick(w, ADS);
  probe('A: Nachtrag, derselbe gclid steht schon im Feld → kein PUT', close(w, '/lead/lead_ALT/', 'PUT').length === 0); }
{ const w = welt({ d1Vorher: { lead_id: 'lead_ALT' } }); await schick(w, ADS);
  probe('A: Nachtrag ohne CLOSE_FIELD_GCLID → weder Lesen noch PUT', close(w, '/lead/lead_ALT/').length === 0); }

// B · Resend lehnt die Mail mit Logo-Anhang ab
const LOGO = { name: 'logo.png', typ: 'image/png', groesse: 2048 };
{ const w = welt({ resendLehntAnhang: true }); const r = await schick(w, GUT, { logo: LOGO });
  const ms = mails(w); const [m1, m2, kunde] = ms;
  probe('B: Anhang abgelehnt → zweiter Versuch OHNE Anhang mit Hinweis „Logo-Anhang nicht zustellbar"',
    ms.length === 3 && m1.body.attachments && m2 && !m2.body.attachments && /Logo-Anhang nicht zustellbar/.test(m2.body.subject + m2.body.html) && m2.body.to[0] === 'info@handwerksmanufaktur.digital');
  probe('B: Kundenmail bestätigt das Logo NICHT, bittet um erneutes Schicken',
    kunde && kunde.body.to[0] === 'max@beispiel.de' && !/Logo ist angekommen/.test(kunde.body.text) && /Schick uns dein Logo bitte noch einmal per Mail/.test(kunde.body.text));
  probe('B: Antwort und D1 sagen hat_logo = 0, Close-Notiz „Logo verloren", Lead bleibt',
    r.status === 200 && r.j.hat_logo === false && w.d1[0]?.a[10] === 0 && close(w, '/activity/note/', 'POST').some(a => /Logo verloren/.test(a.body.note)) && w.d1[0]?.a[8] === 'lead_NEU'); }
{ const w = welt(); const r = await schick(w, GUT, { logo: LOGO });
  probe('B: Gegenprobe — Anhang geht durch → ein Versuch, hat_logo = 1, Logo-Bestätigung', mails(w).length === 2 && r.j.hat_logo === true && w.d1[0]?.a[10] === 1 && /Logo ist angekommen/.test(mails(w)[1].body.text)); }
{ const w = welt({ d1Vorher: { lead_id: 'lead_ERST' }, resendLehntAnhang: true }); const r = await schick(w, GUT, { logo: LOGO });
  probe('B: auch beim Nachtrag: Anhang abgelehnt → Mail ohne Anhang, hat_logo false', mails(w).length === 2 && !mails(w)[1].body.attachments && r.j.hat_logo === false); }

let rot = 0;
for (const [n, ok] of proben) { console.log(`${ok ? '✅' : '❌'} ${n}`); if (!ok) rot++; }
console.log(`\n${proben.length - rot}/${proben.length} grün`);
process.exit(rot ? 1 : 0);

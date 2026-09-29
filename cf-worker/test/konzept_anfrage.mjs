// Prüft den Endpunkt /konzept-anfrage (src/konzept.js) ohne ein einziges echtes Close-/Resend-/D1-Ziel:
// fetch und D1 sind Attrappen, jeder Aufruf wird mitgeschrieben.
// Aufruf: node test/konzept_anfrage.mjs            (bündelt src/konzept.js vorher mit esbuild)
//         node test/konzept_anfrage.mjs --fehler   (baut einen Fehler ein: die Proben MÜSSEN rot werden)
import { execSync } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const dir = mkdtempSync(join(tmpdir(), 'ka-'));
const out = join(dir, 'k.mjs');
execSync(`npx esbuild src/konzept.js --bundle --format=esm --outfile=${out} --log-level=warning`, { cwd: new URL('..', import.meta.url).pathname });
if (process.argv.includes('--fehler')) {   // Gegenprobe: Quelle ohne Jahr + Kunde bekommt nie eine Mail
  writeFileSync(out, readFileSync(out, 'utf8').replace('`${kanalLabel(code)} ${jetzt.getUTCFullYear()}`', 'kanalLabel(code)').replace("close.art !== 'nachtrag'", 'false'));
}
const K = await import(out);

const JETZT = new Date('2026-09-29T10:00:00Z');
function formular(felder, logo) {
  const fd = new FormData();
  for (const [k, v] of Object.entries(felder)) fd.append(k, v);
  if (logo) fd.append('logo', new File([new Uint8Array(logo.groesse).fill(7)], logo.name, { type: logo.typ }));
  return fd;
}
const GUT = { betrieb: 'Testbetrieb Claude', name: 'Max Muster', email: 'max@beispiel.de', telefon: '0170 1234567', website: 'beispiel.de', code: 'kleinanzeigen' };

function welt({ closeTreffer = [], closeFehler = false, d1Vorher = null, d1Zaehler = 0 } = {}) {
  const aufrufe = [], d1 = [];
  const fetchImpl = async (u, o = {}) => {
    const body = o.body ? JSON.parse(o.body) : null;
    aufrufe.push({ u: String(u), m: o.method || 'GET', body });
    if (String(u).startsWith('https://api.close.com')) {
      if (closeFehler) return new Response('kaputt', { status: 500 });
      if (String(u).includes('/lead/?query=')) return Response.json({ data: closeTreffer });
      if (o.method === 'POST' && String(u).endsWith('/lead/')) return Response.json({ id: 'lead_NEU' });
      return Response.json({ id: 'x' });
    }
    if (String(u).startsWith('https://api.resend.com')) return Response.json({ id: 'mail' });
    throw new Error('unerwartetes Ziel ' + u);
  };
  const db = {
    prepare: sql => ({
      bind: (...a) => ({
        first: async () => sql.includes('COUNT(*)') ? { n: d1Zaehler } : d1Vorher,
        run: async () => { d1.push({ sql, a }); return {}; },
      }),
    }),
  };
  return { aufrufe, d1, env: { CLOSE_API_KEY: 'k', RESEND_API_KEY: 'r', RUN_DB: db }, fetchImpl };
}
async function schick(w, felder, { logo = null, trocken = false } = {}) {
  const req = new Request('https://w.test/konzept-anfrage' + (trocken ? '?trocken=1' : ''), { method: 'POST', body: formular(felder, logo), headers: { 'cf-connecting-ip': '1.2.3.4' } });
  const r = await K.handleKonzeptAnfrage(req, w.env, { fetchImpl: w.fetchImpl, jetzt: () => JETZT });
  return { status: r.status, j: await r.json() };
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

let rot = 0;
for (const [n, ok] of proben) { console.log(`${ok ? '✅' : '❌'} ${n}`); if (!ok) rot++; }
console.log(`\n${proben.length - rot}/${proben.length} grün`);
process.exit(rot ? 1 : 0);

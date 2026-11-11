// Prüft /termin-anfrage (src/termin.js) mit Attrappen statt Close/Resend/Calendly — jeder Aufruf wird mitgeschrieben.
// Aufruf: node test/termin_anfrage.mjs            → alle Proben grün
//         node test/termin_anfrage.mjs --fehler   → baut je einen Fehler in eine Temp-Kopie ein, jede Gegenprobe MUSS rot werden
import { mkdtempSync, readFileSync, writeFileSync, copyFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const src = new URL('../src/', import.meta.url).pathname;

const MUTATIONEN = [
  ['if (await hmac(env, p) !== sig) return null;', ''],                                       // Token ohne Signaturprüfung
  ["if (!themen.length) return { fehler: 'Bitte wähl aus, worum es gehen soll.' };", ''],    // Themen nicht Pflicht
  ["if (t.task_id) { try { await close(`/task/${t.task_id}/`, 'PUT', { is_complete: true });", "if (false) { try { await close(`/task/${t.task_id}/`, 'PUT', { is_complete: true });"], // Aufgabe bleibt offen
  ['`Worum es geht: ${themenText(d.themen)}`,', ''],                                           // Themen fehlen in der Notiz
];

async function laden(mut) {
  const dir = mkdtempSync(join(tmpdir(), 'ta-'));
  copyFileSync(join(src, 'konzept.js'), join(dir, 'konzept.js'));
  let s = readFileSync(join(src, 'termin.js'), 'utf8');
  if (mut) { if (!s.includes(mut[0])) throw new Error('Mutation trifft nicht: ' + mut[0]); s = s.replace(mut[0], mut[1]); }
  writeFileSync(join(dir, 'termin.js'), s);
  return import(join(dir, 'termin.js'));
}

function attrappe({ treffer = [] } = {}) {
  const log = [];
  const f = async (url, opt = {}) => {
    const body = opt.body ? JSON.parse(opt.body) : null;
    log.push({ url, methode: opt.method || 'GET', body });
    const ok = d => new Response(JSON.stringify(d), { status: 200 });
    if (url.includes('api.close.com') && url.includes('/lead/?query=')) return ok({ data: treffer });
    if (url.endsWith('/lead/') && opt.method === 'POST') return ok({ id: 'lead_NEU123' });
    if (url.endsWith('/task/') && opt.method === 'POST') return ok({ id: 'task_AUF1' });
    if (url.includes('api.calendly.com/scheduled_events/')) return ok({ resource: { start_time: '2026-11-13T09:00:00.000000Z', name: 'Kostenloses Beratungsgespräch' } });
    return ok({});
  };
  return { f, log };
}
const env = { CLOSE_API_KEY: 'x', RESEND_API_KEY: 'y', KONZEPT_SALT: 'salz', CALENDLY_API_KEY: 'c' };
const req = (body, q = '') => new Request('https://w.test/termin-anfrage' + q, { method: 'POST', body: JSON.stringify(body) });
const KONTAKT = { schritt: 'kontakt', seite: 'shk', themen: ['website', 'seo', 'quatsch'], name: 'Max Muster', betrieb: 'Muster Haustechnik GmbH', telefon: '+49 171 1234567', email: 'Max@Muster.de', pfad: '/' };

async function proben(m) {
  const fehler = [];
  const pruef = (cond, was) => { if (!cond) fehler.push(was); };
  const jetzt = () => new Date('2026-11-11T08:00:00Z');

  // 1 neuer Lead
  let a = attrappe();
  let r = await (await m.handleTerminAnfrage(req(KONTAKT), env, { fetchImpl: a.f, jetzt })).json();
  pruef(r.ok && r.tok, '1 ok + tok');
  const post = a.log.find(x => x.url.endsWith('/lead/') && x.methode === 'POST');
  pruef(post && post.body.name === 'Muster Haustechnik GmbH', '1 Lead = Betrieb');
  pruef(post && Object.values(post.body).includes('SHK-Website 2026'), '1 Quelle SHK-Website 2026');
  pruef(post && post.body.contacts[0].emails[0].email === 'max@muster.de', '1 Mail klein');
  const notiz = a.log.find(x => x.url.includes('/activity/note/'));
  pruef(notiz && notiz.body.note.includes('Worum es geht: Website, Bei Google gefunden werden (SEO)'), '1 Themen in Notiz (ohne Unsinn)');
  const task = a.log.find(x => x.url.endsWith('/task/') && x.methode === 'POST');
  pruef(task && task.body.date === '2026-11-11', '1 Aufgabe heute');
  pruef(a.log.some(x => x.url.includes('resend.com') && x.body.subject.includes('Muster Haustechnik')), '1 Mail an info@');
  pruef(!JSON.stringify(r).includes('lead_NEU123'), '1 keine Lead-ID an den Browser');

  // 2 Buchung mit Token
  a = attrappe();
  let r2 = await (await m.handleTerminAnfrage(req({ schritt: 'gebucht', tok: r.tok, event_uri: 'https://api.calendly.com/scheduled_events/abc-123' }), env, { fetchImpl: a.f, jetzt })).json();
  pruef(r2.ok, '2 ok');
  const n2 = a.log.find(x => x.url.includes('/activity/note/'));
  pruef(n2 && n2.body.lead_id === 'lead_NEU123' && n2.body.note.includes('13.11.2026') && n2.body.note.includes('10:00'), '2 Notiz mit Berliner Zeit');
  pruef(a.log.some(x => x.url.includes('/task/task_AUF1/') && x.body && x.body.is_complete === true), '2 Aufgabe abgehakt');

  // 3 gefälschtes Token
  a = attrappe();
  const falsch = r.tok.split('.')[0] + '.AAAA';
  let r3 = await m.handleTerminAnfrage(req({ schritt: 'gebucht', tok: falsch }), env, { fetchImpl: a.f, jetzt });
  pruef(r3.status === 403 && !a.log.length, '3 falsches Token abgewiesen');
  const fremd = btoa('lead_FREMD||9999999999999').replace(/=+$/, '') + '.' + r.tok.split('.')[1];
  r3 = await m.handleTerminAnfrage(req({ schritt: 'gebucht', tok: fremd }), env, { fetchImpl: a.f, jetzt });
  pruef(r3.status === 403, '3 fremde Lead-ID abgewiesen');

  // 4 Pflicht: Themen, Telefon
  a = attrappe();
  let r4 = await m.handleTerminAnfrage(req({ ...KONTAKT, themen: [] }), env, { fetchImpl: a.f, jetzt });
  pruef(r4.status === 400 && !a.log.length, '4 ohne Thema abgewiesen');
  r4 = await m.handleTerminAnfrage(req({ ...KONTAKT, telefon: 'abc' }), env, { fetchImpl: a.f, jetzt });
  pruef(r4.status === 400, '4 Telefon geprüft');

  // 5 bestehender Lead → kein neuer
  a = attrappe({ treffer: [{ id: 'lead_ALT', custom: { Quelle: 'Kaltakquise' } }] });
  await m.handleTerminAnfrage(req(KONTAKT), env, { fetchImpl: a.f, jetzt });
  pruef(!a.log.some(x => x.url.endsWith('/lead/') && x.methode === 'POST'), '5 kein Doppel-Lead');
  pruef(!a.log.some(x => x.methode === 'PUT' && x.url.includes('lead_ALT')), '5 Quelle nicht überschrieben');

  // 6 Close fällt aus → trotzdem ok (Kalender öffnet), Mail warnt
  const kaputt = async (url, opt = {}) => url.includes('api.close.com') ? new Response('nein', { status: 500 }) : new Response('{}', { status: 200 });
  const r6 = await (await m.handleTerminAnfrage(req(KONTAKT), env, { fetchImpl: kaputt, jetzt })).json();
  pruef(r6.ok && !r6.tok && r6.close === false, '6 Close-Ausfall blockiert den Kalender nicht');

  // 7 Honeypot
  a = attrappe();
  await m.handleTerminAnfrage(req({ ...KONTAKT, bot: 'x' }), env, { fetchImpl: a.f, jetzt });
  pruef(!a.log.length, '7 Honeypot schluckt still');
  return fehler;
}

if (process.argv.includes('--fehler')) {
  let still = 0;
  for (const mut of MUTATIONEN) {
    const f = await proben(await laden(mut));
    console.log(f.length ? `✅ Gegenprobe rot (${f[0]})` : `❌ Gegenprobe blieb grün: ${mut[0].slice(0, 60)}`);
    if (!f.length) still++;
  }
  process.exit(still ? 1 : 0);
} else {
  const f = await proben(await laden(null));
  if (f.length) { console.log('❌ ' + f.join('\n❌ ')); process.exit(1); }
  console.log('✅ termin-anfrage: alle Proben grün');
}

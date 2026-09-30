/**
 * 🎁 Konzept-Anfrage mit Kanal-Code (29.09.2026, 🌐 Helena)
 *
 * Noah: „Mit dem Code KLEINANZEIGEN bekommen die gratis ein Website-Konzept." Später dasselbe für
 * andere Kanäle — ein neuer Kanal ist NUR ein URL-Parameter (?code=INSTAGRAM), hier wird nichts gepflegt.
 *
 * Ablauf je Anfrage (POST /konzept-anfrage, multipart/form-data von handwerksmanufaktur.digital/konzept/):
 *   1. prüfen (Honeypot, Pflichtfelder, Logo ≤ 5 MB png/jpg/svg/pdf), Rate-Limit je IP-Hash (5/Stunde)
 *   2. dieselbe E-Mail binnen 24 h → KEIN zweiter Lead, nur eine Nachtrag-Notiz am ersten
 *   3. Close: Lead über die E-Mail suchen; gibt es ihn, Notiz + Aufgabe daran (Quelle nur, wenn leer),
 *      sonst neuer Lead (Status Hot, Quelle „<Kanal> 2026") mit Kontakt, Notiz und Anruf-Aufgabe für heute
 *   4. Mail an info@ mit allen Angaben, Logo als ANHANG — bewusst kein R2: ein Anhang braucht keinen
 *      neuen Speicher, keine Löschfrist und keinen öffentlichen Link, und die Mail ist das Sicherheitsnetz,
 *      falls Close einmal nicht antwortet (dann steht der Fehler oben in der Mail)
 *   5. Bestätigung an den Betrieb (ohne Logo: Bitte ums Logo als Antwort + Terminlink)
 *   6. Zeile in D1 `konzept_anfragen` (run-db) — Datenbasis für „Anfragen je Kanal" im Cockpit
 *
 * `?trocken=1` prüft und plant nur: kein Close, keine Mail, kein D1. Für Tests.
 */

export const CLOSE_QUELLE_FELD = 'cf_Vq9zqF0eZEGkU9ycE1bHMF2hbmE26Vpk0o0J0gi93q1'; // Lead-Feld „Quelle" (Text)
export const CLOSE_STATUS_HOT = 'stat_BBiSehUMZ59SCNHrcYdEg3xpIslsqGyP21OMatL4XgO';
// Google-Ads-Klick (30.09.2026): das Lead-Feld „Google Click ID" (Text) gibt es in Close noch NICHT. Ist die Umgebungsvariable
// CLOSE_FIELD_GCLID (= cf_… des Feldes) gesetzt, wird die Kennung dort abgelegt; sonst steht sie nur in der Lead-Notiz.
export const QUELLE_GOOGLE_ADS = 'Google Ads – Suche';
export const CAL_KONZEPT = 'https://calendly.com/noahseelau/website-potenzial-video'; // Terminart „Website-Konzept" (45 Min., Video)
const INFO = 'info@handwerksmanufaktur.digital';
const ABSENDER = 'Noah Seelau <onboarding@handwerksmanufaktur.digital>';
const LOGO_MAX = 5 * 1024 * 1024;
const LOGO_TYPEN = { 'image/png': 'png', 'image/jpeg': 'jpg', 'image/svg+xml': 'svg', 'application/pdf': 'pdf' };
const RATE_PRO_STUNDE = 5;
const ZEITLIMIT_MS = 10000;   // je Aufruf an Close/Resend — hängt ein Dienst, gilt das wie ein Ausfall (Sicherungsmail)
const zeitlimit = () => AbortSignal.timeout(ZEITLIMIT_MS);

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};
const antwort = (d, status = 200) => new Response(JSON.stringify(d), { status, headers: { ...CORS, 'Content-Type': 'application/json' } });

const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const sauber = (v, max = 200) => String(v ?? '').replace(/[\u0000-\u001f\u007f]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, max);

export function kanalLabel(code) {
  if (!code) return 'Website';
  return code.toLowerCase().split('-').map(t => t.charAt(0).toUpperCase() + t.slice(1)).join('-');
}
export function quelleVon(code, jetzt = new Date(), klick = null) {
  if (klick && klick.utm_source === 'google' && /^(cpc|ppc|paid)/.test(klick.utm_medium || '')) return QUELLE_GOOGLE_ADS;
  return `${kanalLabel(code)} ${jetzt.getUTCFullYear()}`;
}

/** Klick-Felder aus dem Formular (nur bekannte Namen).
 *  Kennungen (gclid/gbraid/wbraid) sind streng [A-Za-z0-9_-]{1,200} — alles andere ist keine echte Kennung und wird verworfen
 *  (abgeschnitten oder umgebaut wäre sie für Googles Offline-Import wertlos). UTM-Texte sind Klartext: Buchstaben inkl. Umlaute,
 *  Ziffern, Leerzeichen und - _ . + % /, höchstens 200 Zeichen, keine Steuerzeichen, kein HTML. */
export const KLICK_NAMEN = ['gclid', 'gbraid', 'wbraid', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
const KENNUNGEN = ['gclid', 'gbraid', 'wbraid'];
export function klickLesen(fd) {
  const k = {};
  for (const n of KLICK_NAMEN) {
    const roh = String(fd.get(n) ?? '').trim();
    const v = KENNUNGEN.includes(n)
      ? (/^[A-Za-z0-9_-]{1,200}$/.test(roh) ? roh : '')
      : roh.replace(/[\u0000-\u001f\u007f]/g, ' ').replace(/[^\p{L}\p{N} \-_.+%\/]/gu, '').replace(/\s+/g, ' ').trim().slice(0, 200);
    if (v) k[n] = v;
  }
  return k;
}
/** Ins Close-Feld „Google Click ID" gehört NUR ein echtes gclid (Googles Offline-Import braucht genau das). gbraid/wbraid: nur Notiz. */
export const klickId = k => k.gclid || '';

/** Die Antworten der Landingpage stecken in `seite` (lp.js): „/lp/pfad/?gewerk=schreinerei&homepage=ja&ziel=…". */
export function seiteLesen(seite) {
  const roh = String(seite || '');
  if (!roh) return { pfad: '', antworten: {} };
  const i = roh.indexOf('?');
  const pfad = i < 0 ? roh : roh.slice(0, i);
  const antworten = {};
  if (i >= 0) for (const teil of roh.slice(i + 1).split('&')) {
    const j = teil.indexOf('='); if (j < 1) continue;
    let v = teil.slice(j + 1); try { v = decodeURIComponent(v); } catch { /* bleibt roh */ }
    antworten[teil.slice(0, j)] = sauber(v, 120);
  }
  return { pfad: sauber(pfad, 120), antworten };
}
const ANTWORT_LABEL = { gewerk: 'Gewerk', homepage: 'Homepage', ziel: 'Ziel' };
/** [[Label, Wert], …] für Notiz und Mail — bekannte Antworten zuerst, unbekannte als „Weitere". */
export function seiteZeilen(seite) {
  const { pfad, antworten } = seiteLesen(seite);
  const z = [];
  if (pfad) z.push(['Landingpage', pfad]);
  for (const [k, l] of Object.entries(ANTWORT_LABEL)) if (antworten[k]) z.push([l, antworten[k]]);
  const rest = Object.entries(antworten).filter(([k]) => !ANTWORT_LABEL[k]);
  if (rest.length) z.push(['Weitere Antworten', rest.map(([k, v]) => `${k}=${v}`).join(' · ')]);
  return z;
}
export const klickText = k => Object.entries(k || {}).map(([n, v]) => `${n}=${v}`).join(' · ');

export function codeSauber(v) {
  const c = String(v ?? '').trim().toUpperCase().replace(/\s+/g, '');
  return /^[A-Z0-9-]{2,30}$/.test(c) ? c : '';
}

export function vorname(name) {
  const w = sauber(name).split(' ').filter(Boolean);
  if (w.length < 2) return '';
  if (/^(herr|frau|firma|fa\.?|familie|dr\.?)$/i.test(w[0])) return '';
  return /^[A-Za-zÄÖÜäöüß-]{2,}$/.test(w[0]) ? w[0] : '';
}

export function websiteSauber(v) {
  let w = sauber(v, 200);
  if (!w) return '';
  if (!/^https?:\/\//i.test(w)) w = 'https://' + w.replace(/^\/+/, '');
  try { const u = new URL(w); return /\./.test(u.hostname) ? u.origin + (u.pathname === '/' ? '' : u.pathname) : ''; } catch { return ''; }
}

/** Liest und prüft das Formular. Gibt { fehler } oder { daten, logo } zurück. */
export async function lesen(request) {
  let fd;
  try { fd = await request.formData(); } catch { return { fehler: 'Formular konnte nicht gelesen werden.' }; }
  if (sauber(fd.get('bot'))) return { bot: true };
  const d = {
    betrieb: sauber(fd.get('betrieb'), 120),
    name: sauber(fd.get('name'), 120),
    email: sauber(fd.get('email'), 160).toLowerCase(),
    telefon: sauber(fd.get('telefon'), 40),
    website: websiteSauber(fd.get('website')),
    code: codeSauber(fd.get('code')),
    seite: sauber(fd.get('seite'), 200),
    klick: klickLesen(fd),
  };
  if (d.betrieb.length < 2) return { fehler: 'Bitte den Namen deines Betriebs eintragen.' };
  if (d.name.length < 2) return { fehler: 'Bitte deinen Namen eintragen.' };
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(d.email)) return { fehler: 'Bitte eine gültige E-Mail-Adresse eintragen.' };
  if (d.telefon.replace(/\D/g, '').length < 6 || !/^[+()\d\s\/.-]+$/.test(d.telefon)) return { fehler: 'Bitte eine gültige Telefonnummer eintragen.' };
  let logo = null;
  const f = fd.get('logo');
  if (f && typeof f === 'object' && f.size > 0) {
    if (f.size > LOGO_MAX) return { fehler: 'Das Logo ist größer als 5 MB. Schick es uns gern später per Mail.' };
    const endung = (String(f.name || '').split('.').pop() || '').toLowerCase();
    const typ = LOGO_TYPEN[f.type] || ({ png: 'png', jpg: 'jpg', jpeg: 'jpg', svg: 'svg', pdf: 'pdf' })[endung];
    if (!typ) return { fehler: 'Das Logo bitte als PNG, JPG, SVG oder PDF.' };
    logo = { name: sauber(f.name, 80) || `logo.${typ}`, typ, groesse: f.size, puffer: await f.arrayBuffer() };
  }
  return { daten: d, logo };
}

function b64(buf) {
  const bytes = new Uint8Array(buf); let s = '';
  for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  return btoa(s);
}

async function ipHash(request, env) {
  const ip = request.headers.get('cf-connecting-ip') || request.headers.get('x-forwarded-for') || 'unbekannt';
  const h = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(`${env.KONZEPT_SALT || 'hwm'}|${ip}`));
  return [...new Uint8Array(h)].slice(0, 8).map(b => b.toString(16).padStart(2, '0')).join('');
}

/* ---------------- Close ---------------- */
function closeApi(env, fetchImpl) {
  const auth = 'Basic ' + btoa(`${env.CLOSE_API_KEY}:`);
  return async (pfad, methode = 'GET', body) => {
    const r = await fetchImpl('https://api.close.com/api/v1' + pfad, {
      method: methode,
      headers: { Authorization: auth, 'Content-Type': 'application/json', 'User-Agent': 'HWM-Konzept-Worker/1.0' },
      body: body ? JSON.stringify(body) : undefined,
      signal: zeitlimit(),
    });
    const t = await r.text();
    if (!r.ok) throw new Error(`Close ${methode} ${pfad.split('?')[0]} → ${r.status} ${t.slice(0, 200)}`);
    return t ? JSON.parse(t) : {};
  };
}

export function notizText(d, logo, quelle, extra = '', heute = '') {
  const am = /^\d{4}-\d{2}-\d{2}$/.test(heute) ? ` · am ${heute.slice(8)}.${heute.slice(5, 7)}.${heute.slice(0, 4)}` : '';
  const k = d.klick || {};
  return [
    `🎁 Konzept-Anfrage über handwerksmanufaktur.digital/konzept${extra}`,
    `Kanal: ${d.code || 'ohne Code'} → Quelle „${quelle}"`,
    `Betrieb: ${d.betrieb}`,
    `Name: ${d.name}`,
    `E-Mail: ${d.email}`,
    `Telefon: ${d.telefon}`,
    `Website: ${d.website || 'keine angegeben'}`,
    ...seiteZeilen(d.seite).map(([l, v]) => `${l}: ${v}`),
    ...(Object.keys(k).length ? [`Google-Klick: ${klickText(k)}${am}`] : []),
    ...(!k.gclid && (k.gbraid || k.wbraid) ? ['Hinweis: kein gclid — gbraid/wbraid stehen nur hier, nicht im Feld „Google Click ID"'] : []),
    `Logo: ${logo ? `hochgeladen (${logo.name}, ${Math.round(logo.groesse / 1024)} KB) — liegt als Anhang in der Mail an ${INFO}` : 'nicht hochgeladen — per Mail angefragt'}`,
  ].join('\n');
}

const fehlerText = e => String((e && e.message) || e).slice(0, 200);

async function inClose(env, fetchImpl, d, logo, quelle, heute, vorhandeneLeadId) {
  const close = closeApi(env, fetchImpl);
  const teilfehler = [];   // ab dem Moment, in dem es eine Lead-ID gibt, ist jeder Fehler nur noch ein Teilfehler — die ID bleibt
  const schritt = async (was, fn) => { try { return await fn(); } catch (e) { teilfehler.push({ was, fehler: fehlerText(e) }); console.error('[Konzept] Teilfehler', was, fehlerText(e)); return null; } };
  const gclid = klickId(d.klick || {});
  const notiz = (lead_id, extra) => schritt('Notiz', () => close('/activity/note/', 'POST', { lead_id, note: notizText(d, logo, quelle, extra, heute) }));
  // Nachtrag an einen Lead aus einer Anfrage der letzten 24 h
  if (vorhandeneLeadId) {
    // auch der Nachtrag hält das Feld aktuell: der jüngste gclid gewinnt, und ein früher gescheiterter PUT wird nachgeholt
    let zus = '';
    if (env.CLOSE_FIELD_GCLID && gclid) {
      const lead = await schritt('Feld Google Click ID lesen', () => close(`/lead/${vorhandeneLeadId}/?_fields=id,custom`));
      const alt = lead && (lead.custom || {})['Google Click ID'];
      if (lead && alt !== gclid) {
        const ok = await schritt('Feld Google Click ID', () => close(`/lead/${vorhandeneLeadId}/`, 'PUT', { [`custom.${env.CLOSE_FIELD_GCLID}`]: gclid }));
        if (ok) zus = alt ? ` (Google Click ID im Feld ersetzt: vorher ${alt})` : ' (Google Click ID im Feld nachgetragen)';
      }
    }
    await notiz(vorhandeneLeadId, ' (erneut abgeschickt)' + zus);
    return { lead_id: vorhandeneLeadId, art: 'nachtrag', teilfehler };
  }
  const such = await close(`/lead/?query=${encodeURIComponent(`email:"${d.email}"`)}&_fields=id,display_name,custom&_limit=2`);
  const treffer = (such.data || []);
  let leadId, art, zusatz = '';
  if (treffer.length === 1) {
    leadId = treffer[0].id; art = 'bestehend';
    const custom = treffer[0].custom || {};
    if (!custom.Quelle) await schritt('Feld Quelle', () => close(`/lead/${leadId}/`, 'PUT', { [`custom.${CLOSE_QUELLE_FELD}`]: quelle }));
    // der jüngste Klick zählt: ein neuer gclid ersetzt den alten, die Notiz hält beide
    if (env.CLOSE_FIELD_GCLID && gclid && custom['Google Click ID'] !== gclid) {
      const alt = custom['Google Click ID'];
      const ok = await schritt('Feld Google Click ID', () => close(`/lead/${leadId}/`, 'PUT', { [`custom.${env.CLOSE_FIELD_GCLID}`]: gclid }));
      if (ok && alt) zusatz = ` (Google Click ID im Feld ersetzt: vorher ${alt})`;
    }
  } else {
    // 0 Treffer → neu. Mehrere Treffer → nicht raten, neuer Lead (die Notiz nennt es, Noah führt zusammen).
    // Das optionale gclid-Feld kommt NICHT in den POST: ein falsch benanntes Feld lässt Close den ganzen Lead ablehnen (400).
    const neu = await close('/lead/', 'POST', {
      name: d.betrieb,
      url: d.website || undefined,
      status_id: CLOSE_STATUS_HOT,
      contacts: [{ name: d.name, emails: [{ email: d.email, type: 'office' }], phones: [{ phone: d.telefon, type: 'office' }] }],
      [`custom.${CLOSE_QUELLE_FELD}`]: quelle,
    });
    leadId = neu.id; art = treffer.length > 1 ? 'neu-mehrdeutig' : 'neu';
    if (env.CLOSE_FIELD_GCLID && gclid) await schritt('Feld Google Click ID', () => close(`/lead/${leadId}/`, 'PUT', { [`custom.${env.CLOSE_FIELD_GCLID}`]: gclid }));
  }
  const hinweis = (art === 'bestehend' ? ' (Lead gab es schon)' : art === 'neu-mehrdeutig' ? ' (⚠️ E-Mail steht an mehreren Leads — bitte zusammenführen)' : '') + zusatz
    + (teilfehler.some(t => t.was === 'Feld Google Click ID') ? ' (⚠️ Feld „Google Click ID" nicht gesetzt — der Wert steht in dieser Notiz)' : '');
  await notiz(leadId, hinweis);
  await schritt('Aufgabe', () => close('/task/', 'POST', {
    lead_id: leadId, date: heute,
    text: `🎁 Konzept-Anfrage (${kanalLabel(d.code)}): ${d.name} anrufen, Konzeptgespräch ausmachen${logo ? '' : ', Logo fehlt noch'}`,
  }));
  return { lead_id: leadId, art, teilfehler };
}

/* ---------------- Mails ---------------- */
export function mailIntern(d, logo, quelle, close) {
  const teil = close.teilfehler || [];
  const closeZeile = close.lead_id
    ? `<a href="https://app.close.com/lead/${esc(close.lead_id)}/">Lead öffnen</a> (${esc(close.art)})${teil.length ? ` — ⚠️ ${teil.map(t => `${esc(t.was)} fehlgeschlagen`).join(', ')}` : ''}`
    : `⚠️ nicht angelegt: ${esc(close.fehler || '')}`;
  const zeilen = [['Betrieb', d.betrieb], ['Name', d.name], ['E-Mail', d.email], ['Telefon', d.telefon],
    ['Website', d.website || '—'], ['Code', d.code || 'ohne Code'], ['Quelle in Close', quelle],
    ...seiteZeilen(d.seite),
    ...(Object.keys(d.klick || {}).length ? [['Google-Klick', klickText(d.klick)]] : []),
    ['Logo', logo ? `im Anhang (${esc(logo.name)})` : 'fehlt — der Betrieb wurde per Mail gebeten'],
    ['Close', closeZeile]];
  const rows = zeilen.map(([k, v]) => `<tr><td style="padding:8px 12px;color:#6b6258;white-space:nowrap">${k}</td><td style="padding:8px 12px;font-weight:600">${k === 'Close' || k === 'Logo' ? v : esc(v)}</td></tr>`).join('');
  const warn = close.lead_id
    ? (teil.length ? `<p style="background:#fff3d6;padding:10px 12px;border-radius:6px"><b>Lead angelegt, aber unvollständig:</b> ${teil.map(t => `${esc(t.was)} fehlgeschlagen (${esc(t.fehler)})`).join('; ')}. Bitte in Close nachtragen — den Lead nicht neu anlegen.</p>` : '')
    : '<p style="background:#fde8e4;padding:10px 12px;border-radius:6px"><b>Close hat nicht geantwortet.</b> Bitte den Lead von Hand anlegen.</p>';
  return {
    betreff: `Neue Konzept-Anfrage · ${d.betrieb} · Code ${d.code || 'ohne'}`,
    html: `<div style="font-family:Arial,sans-serif;max-width:600px">${warn}<table style="border-collapse:collapse;width:100%;background:#faf7f1;border-radius:8px">${rows}</table></div>`,
  };
}

export function mailBetrieb(d, logo, logoVerloren = false) {
  const vn = vorname(d.name);
  const anrede = vn ? `Hallo ${vn},` : 'Hallo,';
  const absaetze = logoVerloren
    ? [`danke für deine Anfrage für ${d.betrieb}. Ich setze mich an dein Konzept.`,
       `Dein Logo ist bei uns leider nicht angekommen. Schick uns dein Logo bitte noch einmal per Mail, am besten als PNG, SVG oder PDF, einfach als Antwort auf diese Mail.`,
       `Wann passt dir ein kurzes Gespräch zum Konzept? Such dir hier einen Termin aus:`]
    : logo
    ? [`danke für deine Anfrage für ${d.betrieb}. Dein Logo ist angekommen, ich setze mich an dein Konzept.`,
       `Wann passt dir ein kurzes Gespräch dazu? Such dir hier einen Termin aus:`]
    : [`danke für deine Anfrage für ${d.betrieb}. Ich setze mich an dein Konzept.`,
       `Dafür brauche ich noch dein Logo. Schick es mir einfach als Antwort auf diese Mail, am besten als PNG, SVG oder PDF.`,
       `Wann passt dir ein kurzes Gespräch zum Konzept? Such dir hier einen Termin aus:`];
  const text = [anrede, '', ...absaetze.flatMap(a => [a, '']), CAL_KONZEPT, '', 'Beste Grüße', 'Noah', '', 'Noah Seelau · HandwerksManufaktur', '+49 8194 7174990 · handwerksmanufaktur.digital'].join('\n');
  const html = `<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.55;color:#16130E;max-width:560px">`
    + `<p>${esc(anrede)}</p>${absaetze.map(a => `<p>${esc(a)}</p>`).join('')}`
    + `<p><a href="${CAL_KONZEPT}" style="display:inline-block;background:#16130E;color:#FAF7F1;padding:12px 20px;border-radius:999px;text-decoration:none;font-weight:700">Termin aussuchen</a></p>`
    + `<p>Beste Grüße<br>Noah</p><p style="color:#6b6258;font-size:13px">Noah Seelau · HandwerksManufaktur<br>+49 8194 7174990 · <a href="https://handwerksmanufaktur.digital/" style="color:#6b6258">handwerksmanufaktur.digital</a></p></div>`;
  return { betreff: logo && !logoVerloren ? 'Dein Website-Konzept' : 'Dein Website-Konzept: dein Logo fehlt noch', text, html };
}

async function resend(env, fetchImpl, body) {
  const r = await fetchImpl('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal: zeitlimit(),
  });
  if (!r.ok) throw new Error(`Resend ${r.status} ${(await r.text()).slice(0, 200)}`);
  return r.json().catch(() => ({}));
}

/* ---------------- Hauptablauf ---------------- */
export async function handleKonzeptAnfrage(request, env, { fetchImpl = fetch, jetzt = () => new Date() } = {}) {
  const url = new URL(request.url);
  const trocken = url.searchParams.get('trocken') === '1';
  const gelesen = await lesen(request);
  if (gelesen.bot) return antwort({ ok: true });                    // Honeypot: still schlucken
  if (gelesen.fehler) return antwort({ ok: false, fehler: gelesen.fehler }, 400);
  const { daten: d, logo } = gelesen;
  const now = jetzt();
  const quelle = quelleVon(d.code, now, d.klick);
  const heute = new Date(now.getTime() + 2 * 3600e3).toISOString().slice(0, 10); // deutsche Zeit, grob genug fürs Fälligkeitsdatum
  const hash = await ipHash(request, env);

  if (trocken) {
    return antwort({ ok: true, trocken: true, quelle, kanal: kanalLabel(d.code), code: d.code, hat_logo: !!logo,
      notiz: notizText(d, logo, quelle), mail_betrieb: mailBetrieb(d, logo), mail_intern: mailIntern(d, logo, quelle, { lead_id: 'lead_TROCKEN', art: 'trocken' }).betreff });
  }

  const db = env.RUN_DB;
  let vorher = null;
  if (db) {
    // D1 ist Zubehör (Rate-Limit, Nachtrag-Erkennung, Statistik): fällt es aus, laufen Close und Mails trotzdem.
    try {
      const seit = new Date(now.getTime() - 3600e3).toISOString();
      const n = await db.prepare('SELECT COUNT(*) AS n FROM konzept_anfragen WHERE ip_hash = ? AND zeit >= ?').bind(hash, seit).first();
      if ((n?.n || 0) >= RATE_PRO_STUNDE) return antwort({ ok: false, fehler: 'Zu viele Anfragen in kurzer Zeit. Ruf uns gern direkt an: +49 8194 7174990' }, 429);
      const tag = new Date(now.getTime() - 24 * 3600e3).toISOString();
      vorher = await db.prepare('SELECT lead_id FROM konzept_anfragen WHERE email = ? AND zeit >= ? AND lead_id IS NOT NULL ORDER BY zeit DESC LIMIT 1').bind(d.email, tag).first();
    } catch (e) { console.error('[Konzept] D1 lesen', fehlerText(e)); vorher = null; }
  }

  let close;
  try { close = await inClose(env, fetchImpl, d, logo, quelle, heute, vorher?.lead_id || null); }
  catch (e) { close = { lead_id: null, art: 'close-fehler', fehler: String(e.message || e) }; console.error('[Konzept] Close', close.fehler); }

  const intern = mailIntern(d, logo, quelle, close);
  const internMail = { from: ABSENDER.replace('Noah Seelau', 'Konzept-Anfrage'), to: [INFO], reply_to: d.email, subject: (close.art === 'nachtrag' ? 'Nachtrag: ' : '') + intern.betreff, html: intern.html };
  let internOk = true, logoVerloren = false;
  if (logo) {
    internMail.attachments = [{ filename: logo.name, content: b64(logo.puffer) }];
    try { await resend(env, fetchImpl, internMail); }
    catch (e) {
      // Resend lehnt die Mail mit Anhang ab: einmal OHNE Anhang erneut, damit die Anfrage selbst ankommt — das Logo gilt dann als verloren
      console.error('[Konzept] Mail intern mit Logo', fehlerText(e));
      logoVerloren = true;
      const warn = '<p style="background:#fde8e4;padding:10px 12px;border-radius:6px"><b>Logo-Anhang nicht zustellbar.</b> Der Betrieb wurde gebeten, das Logo noch einmal per Mail zu schicken.</p>';
      const ohne = { ...internMail, subject: 'Logo-Anhang nicht zustellbar: ' + internMail.subject, html: warn + internMail.html };
      delete ohne.attachments;
      try { await resend(env, fetchImpl, ohne); } catch (e2) { internOk = false; console.error('[Konzept] Mail intern', fehlerText(e2)); }
    }
  } else {
    try { await resend(env, fetchImpl, internMail); } catch (e) { internOk = false; console.error('[Konzept] Mail intern', fehlerText(e)); }
  }
  if (!internOk && !close.lead_id) return antwort({ ok: false, fehler: 'Das hat gerade nicht geklappt. Ruf uns gern direkt an: +49 8194 7174990' }, 502);
  if (logoVerloren && close.lead_id) {   // die Close-Notiz sagte „Logo hochgeladen" — das stimmt nicht mehr
    try { await closeApi(env, fetchImpl)('/activity/note/', 'POST', { lead_id: close.lead_id, note: '⚠️ Logo verloren: der Anhang war nicht zustellbar. Der Betrieb wurde gebeten, das Logo noch einmal per Mail zu schicken.' }); }
    catch (e) { console.error('[Konzept] Notiz Logo verloren', fehlerText(e)); }
  }
  const logoDa = !!logo && !logoVerloren;

  let betriebOk = null;
  if (close.art !== 'nachtrag') {
    const m = mailBetrieb(d, logo, logoVerloren);
    try { await resend(env, fetchImpl, { from: ABSENDER, to: [d.email], reply_to: INFO, subject: m.betreff, html: m.html, text: m.text }); betriebOk = true; }
    catch (e) { betriebOk = false; console.error('[Konzept] Mail Betrieb', e.message); }
  }

  if (db) {
    const basis = [now.toISOString(), d.code || null, quelle, d.betrieb, d.name, d.email, d.telefon, d.website || null, close.lead_id, close.art,
      logoDa ? 1 : 0, betriebOk === null ? null : betriebOk ? 1 : 0, hash];
    const sp = 'zeit, code, quelle, betrieb, name, email, telefon, website, lead_id, art, hat_logo, mail_betrieb, ip_hash';
    // Klick-Felder + Landingpage-Antworten + Teilfehler als JSON in `extra` — die Spalte gibt es erst nach
    //   ALTER TABLE konzept_anfragen ADD COLUMN extra TEXT;
    // Fehlt sie noch, fällt der Insert auf die alte Fassung zurück (die Werte stehen dann in Close-Notiz und Mail).
    const extraObj = {};
    if (d.seite) extraObj.seite = d.seite;
    if (Object.keys(d.klick || {}).length) extraObj.klick = d.klick;
    if ((close.teilfehler || []).length) extraObj.teilfehler = close.teilfehler.map(t => t.was);
    if (logoVerloren) extraObj.logo_verloren = true;
    if (close.fehler) extraObj.close_fehler = close.fehler;
    const extra = Object.keys(extraObj).length ? JSON.stringify(extraObj) : null;
    const insert = async (mitExtra) => {
      const spalten = mitExtra ? `${sp}, extra` : sp;
      const werte = mitExtra ? [...basis, extra] : basis;
      await db.prepare(`INSERT INTO konzept_anfragen (${spalten}) VALUES (${werte.map(() => '?').join(', ')})`).bind(...werte).run();
    };
    try {
      if (extra) { try { await insert(true); } catch (e) { console.error('[Konzept] D1 mit extra', fehlerText(e)); await insert(false); } }
      else await insert(false);
    } catch (e) { console.error('[Konzept] D1', fehlerText(e)); }
  }
  return antwort({ ok: true, kanal: kanalLabel(d.code), hat_logo: logoDa, termin: CAL_KONZEPT });
}

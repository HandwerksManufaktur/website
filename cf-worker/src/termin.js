/**
 * 📅 Termin-Dialog der Websites (11.11.2026, 🌐 Helena)
 *
 * Noah, 11.11.2026: „Jetzt Termin buchen … zuerst eine kurze Auswahl: worum geht es … dann Namen/Firmennamen
 * eingeben … und wenn sie dann weiterklicken, über eine Automatisierung gleich im Kalender eingetragen."
 * Anlass: Alex-Heeg-Call 06.11.2026 (Tim): Buchungen kommen auch über die Website → Kalender-CTA auf die Seite.
 *
 * Der Dialog (termin.js auf handwerksmanufaktur.digital und shk.handwerksmanufaktur.digital) ruft zweimal:
 *   POST /termin-anfrage  {schritt:"kontakt", seite, themen[], name, betrieb, telefon, email}
 *        → Close: Lead über die E-Mail suchen (sonst neu, Status Hot, Quelle „Website 2026" bzw. „SHK-Website 2026"),
 *          Notiz mit Themen, Anruf-Aufgabe für heute („falls kein Termin gebucht wird"), Mail an info@.
 *        ← {ok, lead_id, tok}   tok = signiert (lead_id|task_id|ablauf), damit Schritt 2 nur am eigenen Lead schreibt
 *   POST /termin-anfrage  {schritt:"gebucht", tok, event_uri}
 *        → Termin aus Calendly lesen (falls CALENDLY_API_KEY gesetzt), Notiz „Termin gebucht", Anruf-Aufgabe abhaken,
 *          Mail an info@.
 * Der Termin selbst steht durch Calendly sofort in Noahs Google-Kalender (Terminart „Kostenloses Beratungsgespräch",
 * Slug potenzial-erstgespraech) — das macht Calendly, nicht dieser Worker.
 * `?trocken=1` prüft nur (kein Close, keine Mail).
 */
import { closeApi, resend, CLOSE_QUELLE_FELD, CLOSE_STATUS_HOT } from './konzept.js';

const INFO = 'info@handwerksmanufaktur.digital';
const ABSENDER = 'Termin-Anfrage <onboarding@handwerksmanufaktur.digital>';
const CORS = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'POST, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type' };
const antwort = (d, status = 200) => new Response(JSON.stringify(d), { status, headers: { ...CORS, 'Content-Type': 'application/json' } });
const sauber = (v, max = 200) => String(v ?? '').replace(/[\u0000-\u001f\u007f]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, max);
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const fehlerText = e => String((e && e.message) || e).slice(0, 200);

export const THEMEN = {
  website: 'Website', kunden: 'Neue Kunden (Leadgen)', mitarbeiter: 'Neue Mitarbeiter (Recruiting)',
  seo: 'Bei Google gefunden werden (SEO)', ads: 'Google-Anzeigen', offen: 'Noch offen',
};
export const SEITEN = {
  hwm: { name: 'handwerksmanufaktur.digital', quelle: 'Website' },
  shk: { name: 'shk.handwerksmanufaktur.digital', quelle: 'SHK-Website' },
};
const TOK_GUELTIG_MS = 6 * 3600e3;

/* ---------- Token (HMAC) ---------- */
const b64u = buf => btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
async function hmac(env, text) {
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(env.KONZEPT_SALT || env.CLOSE_API_KEY || 'hwm'), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  return b64u(await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(text)));
}
export async function tokMachen(env, leadId, taskId, jetzt = Date.now()) {
  const p = `${leadId}|${taskId || ''}|${jetzt + TOK_GUELTIG_MS}`;
  return `${btoa(p).replace(/=+$/, '')}.${await hmac(env, p)}`;
}
export async function tokLesen(env, tok, jetzt = Date.now()) {
  const [teil, sig] = String(tok || '').split('.');
  if (!teil || !sig) return null;
  let p; try { p = atob(teil); } catch { return null; }
  if (await hmac(env, p) !== sig) return null;
  const [lead, task, ablauf] = p.split('|');
  if (!/^lead_[A-Za-z0-9]+$/.test(lead) || !(Number(ablauf) > jetzt)) return null;
  return { lead_id: lead, task_id: /^task_[A-Za-z0-9]+$/.test(task) ? task : null };
}

/* ---------- Eingabe ---------- */
export function lesenKontakt(j) {
  if (sauber(j.bot)) return { bot: true };
  const seite = SEITEN[j.seite] ? j.seite : 'hwm';
  const themen = [...new Set((Array.isArray(j.themen) ? j.themen : []).filter(t => THEMEN[t]))];
  const d = {
    seite, themen,
    name: sauber(j.name, 120), betrieb: sauber(j.betrieb, 120),
    telefon: sauber(j.telefon, 40), email: sauber(j.email, 160).toLowerCase(),
    pfad: sauber(j.pfad, 160),
  };
  if (!themen.length) return { fehler: 'Bitte wähl aus, worum es gehen soll.' };
  if (d.name.length < 2) return { fehler: 'Bitte deinen Namen eintragen.' };
  if (d.betrieb.length < 2) return { fehler: 'Bitte den Namen deines Betriebs eintragen.' };
  // Telefon ist seit 11.11.2026 optional: der Dialog fragt nur Name, Betrieb, E-Mail (Noah: so wenig Felder wie möglich)
  if (d.telefon && (d.telefon.replace(/\D/g, '').length < 6 || !/^[+()\d\s\/.-]+$/.test(d.telefon))) return { fehler: 'Bitte eine gültige Telefonnummer eintragen.' };
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(d.email)) return { fehler: 'Bitte eine gültige E-Mail-Adresse eintragen.' };
  return { daten: d };
}
export const themenText = t => t.map(x => THEMEN[x]).join(', ');
export function notizKontakt(d, quelle, hinweis = '') {
  return [
    `📅 Termin-Anfrage über ${SEITEN[d.seite].name}${hinweis}`,
    `Worum es geht: ${themenText(d.themen)}`,
    `Betrieb: ${d.betrieb}`, `Name: ${d.name}`, `Telefon: ${d.telefon || '— (nicht abgefragt, ggf. in Calendly)'}`, `E-Mail: ${d.email}`,
    ...(d.pfad ? [`Seite: ${d.pfad}`] : []),
    `Quelle: ${quelle}`,
    'Stand: Daten eingetragen, Kalender geöffnet — ob gebucht wurde, steht in der nächsten Notiz. Ohne Buchung: anrufen.',
  ].join('\n');
}

/* ---------- Close ---------- */
async function kontaktInClose(env, fetchImpl, d, quelle, heute) {
  const close = closeApi(env, fetchImpl);
  const teilfehler = [];
  const schritt = async (was, fn) => { try { return await fn(); } catch (e) { teilfehler.push({ was, fehler: fehlerText(e) }); return null; } };
  const such = await close(`/lead/?query=${encodeURIComponent(`email:"${d.email}"`)}&_fields=id,display_name,custom&_limit=2`);
  const treffer = such.data || [];
  let leadId, art;
  if (treffer.length === 1) {
    leadId = treffer[0].id; art = 'bestehend';
    if (!(treffer[0].custom || {}).Quelle) await schritt('Feld Quelle', () => close(`/lead/${leadId}/`, 'PUT', { [`custom.${CLOSE_QUELLE_FELD}`]: quelle }));
  } else {
    const neu = await close('/lead/', 'POST', {
      name: d.betrieb, status_id: CLOSE_STATUS_HOT,
      contacts: [{ name: d.name, emails: [{ email: d.email, type: 'office' }], ...(d.telefon ? { phones: [{ phone: d.telefon, type: 'office' }] } : {}) }],
      [`custom.${CLOSE_QUELLE_FELD}`]: quelle,
    });
    leadId = neu.id; art = treffer.length > 1 ? 'neu-mehrdeutig' : 'neu';
  }
  const hinweis = art === 'bestehend' ? ' (Lead gab es schon)' : art === 'neu-mehrdeutig' ? ' (⚠️ E-Mail steht an mehreren Leads — bitte zusammenführen)' : '';
  await schritt('Notiz', () => close('/activity/note/', 'POST', { lead_id: leadId, note: notizKontakt(d, quelle, hinweis) }));
  const task = await schritt('Aufgabe', () => close('/task/', 'POST', {
    lead_id: leadId, date: heute,
    text: `📅 Termin-Anfrage Website (${themenText(d.themen)}): ${d.name} ${d.telefon ? 'anrufen' : 'per Mail nachfassen'}, falls kein Termin gebucht wurde`,
  }));
  return { lead_id: leadId, task_id: task && task.id, art, teilfehler };
}

async function calendlyTermin(env, fetchImpl, uri) {
  if (!env.CALENDLY_API_KEY || !/^https:\/\/api\.calendly\.com\/scheduled_events\/[A-Za-z0-9-]+$/.test(uri || '')) return null;
  try {
    const r = await fetchImpl(uri, { headers: { Authorization: `Bearer ${env.CALENDLY_API_KEY}`, 'User-Agent': 'hwm-termin-worker/1.0' }, signal: AbortSignal.timeout(8000) });
    if (!r.ok) return null;
    const ev = (await r.json()).resource || {};
    return { start: ev.start_time, name: ev.name };
  } catch { return null; }
}
export function berlinText(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  if (isNaN(d)) return '';
  return new Intl.DateTimeFormat('de-DE', { timeZone: 'Europe/Berlin', weekday: 'short', day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }).format(d) + ' Uhr (deutsche Zeit)';
}

function mailHtml(titel, zeilen, leadId, warn = '') {
  const rows = zeilen.map(([k, v]) => `<tr><td style="padding:8px 12px;color:#6b6258;white-space:nowrap">${esc(k)}</td><td style="padding:8px 12px;font-weight:600">${esc(v)}</td></tr>`).join('');
  const lead = leadId ? `<p><a href="https://app.close.com/lead/${esc(leadId)}/">Lead in Close öffnen</a></p>` : '<p style="background:#fde8e4;padding:10px 12px;border-radius:6px"><b>Close hat nicht geantwortet.</b> Bitte den Lead von Hand anlegen.</p>';
  return `<div style="font-family:Arial,sans-serif;max-width:600px"><h2 style="font-size:18px">${esc(titel)}</h2>${warn}<table style="border-collapse:collapse;width:100%;background:#faf7f1;border-radius:8px">${rows}</table>${lead}</div>`;
}

/* ---------- Hauptablauf ---------- */
export async function handleTerminAnfrage(request, env, { fetchImpl = fetch, jetzt = () => new Date() } = {}) {
  const trocken = new URL(request.url).searchParams.get('trocken') === '1';
  let j;
  try { j = await request.json(); } catch { return antwort({ ok: false, fehler: 'Anfrage konnte nicht gelesen werden.' }, 400); }
  const now = jetzt();

  if (j.schritt === 'gebucht') {
    const t = await tokLesen(env, j.tok, now.getTime());
    if (!t) return antwort({ ok: false, fehler: 'ungültig' }, 403);
    if (trocken) return antwort({ ok: true, trocken: true, lead_id: t.lead_id });
    const close = closeApi(env, fetchImpl);
    const termin = await calendlyTermin(env, fetchImpl, sauber(j.event_uri, 200));
    const wann = termin && termin.start ? berlinText(termin.start) : 'Zeit steht im Kalender (Calendly)';
    const fehler = [];
    try { await close('/activity/note/', 'POST', { lead_id: t.lead_id, note: `✅ Termin über den Website-Dialog gebucht: Kostenloses Beratungsgespräch · ${wann}` }); } catch (e) { fehler.push('Notiz: ' + fehlerText(e)); }
    if (t.task_id) { try { await close(`/task/${t.task_id}/`, 'PUT', { is_complete: true }); } catch (e) { fehler.push('Aufgabe abhaken: ' + fehlerText(e)); } }
    try {
      await resend(env, fetchImpl, { from: ABSENDER, to: [INFO], subject: `Termin gebucht über die Website · ${wann}`,
        html: mailHtml('Termin über den Website-Dialog gebucht', [['Termin', wann], ['Terminart', 'Kostenloses Beratungsgespräch']], t.lead_id,
          fehler.length ? `<p style="background:#fff3d6;padding:10px 12px;border-radius:6px">${esc(fehler.join(' · '))}</p>` : '') });
    } catch (e) { console.error('[Termin] Mail gebucht', fehlerText(e)); }
    return antwort({ ok: true });
  }

  const g = lesenKontakt(j);
  if (g.bot) return antwort({ ok: true });
  if (g.fehler) return antwort({ ok: false, fehler: g.fehler }, 400);
  const d = g.daten;
  const quelle = `${SEITEN[d.seite].quelle} ${now.getUTCFullYear()}`;
  const heute = new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Berlin' }).format(now);
  if (trocken) return antwort({ ok: true, trocken: true, quelle, heute, notiz: notizKontakt(d, quelle) });

  let c;
  try { c = await kontaktInClose(env, fetchImpl, d, quelle, heute); }
  catch (e) { c = { lead_id: null, art: 'close-fehler', fehler: fehlerText(e), teilfehler: [] }; console.error('[Termin] Close', c.fehler); }
  const warn = c.teilfehler && c.teilfehler.length ? `<p style="background:#fff3d6;padding:10px 12px;border-radius:6px">Unvollständig: ${esc(c.teilfehler.map(t => `${t.was} (${t.fehler})`).join('; '))}</p>` : '';
  let mailOk = true;
  try {
    await resend(env, fetchImpl, { from: ABSENDER, to: [INFO], reply_to: d.email,
      subject: `Termin-Anfrage · ${d.betrieb} · ${themenText(d.themen)}`,
      html: mailHtml(`Termin-Anfrage über ${SEITEN[d.seite].name} — Kalender geöffnet, Buchung folgt ggf.`,
        [['Worum es geht', themenText(d.themen)], ['Betrieb', d.betrieb], ['Name', d.name], ['Telefon', d.telefon || '—'], ['E-Mail', d.email], ['Seite', d.pfad || '—'], ['Quelle in Close', quelle]],
        c.lead_id, warn) });
  } catch (e) { mailOk = false; console.error('[Termin] Mail', fehlerText(e)); }
  // Der Kalender öffnet sich IMMER — auch wenn Close oder die Mail hängen, darf die Buchung nicht scheitern.
  const tok = c.lead_id ? await tokMachen(env, c.lead_id, c.task_id, now.getTime()) : null;
  return antwort({ ok: true, tok, close: !!c.lead_id, mail: mailOk });
}
